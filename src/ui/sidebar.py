import uuid

import streamlit as st

from src.agent.health import check_anthropic, check_gigachat, check_ollama, check_openai
from src.schemas.enums import LLMProvider
from src.services.chat_session import delete_session, list_sessions
from src.settings import Settings
from src.ui.constants import EXAMPLES, PROVIDER_MODELS, TOOL_LABELS


_NO_KEY_ERRORS = {"API-ключ не задан", "Client ID / Secret не заданы"}


def _provider_label(status: tuple[bool, str], provider: LLMProvider) -> str:
    ok, err = status
    if ok:
        return f"\u2705 {provider.value} — connected"
    if err in _NO_KEY_ERRORS:
        return f"\u2b1c {provider.value} — no key"
    return f"\u274c {provider.value} — error"


def _check_provider(settings: Settings, provider: LLMProvider) -> tuple[bool, str]:
    if provider == LLMProvider.OPENAI:
        key = settings.openai_api_key.get_secret_value()
        if not key:
            return False, "API-ключ не задан"
        return check_openai(key)

    if provider == LLMProvider.ANTHROPIC:
        key = settings.anthropic_api_key.get_secret_value()
        if not key:
            return False, "API-ключ не задан"
        return check_anthropic(key)

    if provider == LLMProvider.GIGACHAT:
        creds = settings.gigachat_credentials
        if not creds:
            return False, "Client ID / Secret не заданы"
        return check_gigachat(creds, scope=settings.gigachat_scope, verify_ssl=settings.gigachat_verify_ssl)

    if provider == LLMProvider.OLLAMA:
        return check_ollama(settings.ollama_base_url)

    return False, "Unknown provider"


def _render_chat_history_section() -> None:
    st.header("Chat History")

    search_query = st.text_input(
        "Search chats",
        placeholder="Search...",
        label_visibility="collapsed",
    )
    sessions = list_sessions(query=search_query)
    if not sessions:
        st.caption("No conversations found" if search_query else "No conversations yet")
        return

    for s in sessions:
        col_title, col_del = st.columns([5, 1], vertical_alignment="center")
        with col_title:
            if st.button(s["title"], key=f"sess_{s['thread_id']}", use_container_width=True):
                st.session_state.thread_id = s["thread_id"]
                st.session_state.messages = []
                st.session_state.pop("agent", None)
                st.session_state._load_from_history = True
                st.rerun()
        with col_del:
            if st.button("\U0001f5d1", key=f"del_{s['thread_id']}"):
                delete_session(s["thread_id"])
                if st.session_state.get("thread_id") == s["thread_id"]:
                    st.session_state.thread_id = str(uuid.uuid4())
                    st.session_state.messages = []
                st.rerun()


def render_sidebar(settings: Settings) -> tuple[LLMProvider, str, float]:
    with st.sidebar:
        st.header("Settings")

        providers = list(LLMProvider)
        statuses: dict[LLMProvider, tuple[bool, str]] = {}
        for p in providers:
            statuses[p] = _check_provider(settings, p)

        default_idx = providers.index(settings.llm_provider)
        selected_provider = st.selectbox(
            "LLM Provider",
            providers,
            index=default_idx,
            format_func=lambda p: _provider_label(statuses[p], provider=p),
        )

        ok, err = statuses[selected_provider]
        if not ok:
            st.warning(err)

        models = PROVIDER_MODELS.get(selected_provider.value, [])
        model_name = st.selectbox("Model", models, index=0) if models else ""

        temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05)

        if st.button("New conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.pop("_current_title", None)
            st.rerun()

        st.divider()
        _render_chat_history_section()

        st.divider()
        st.header("Statistics")
        if st.session_state.tool_usage:
            for tool_id, count in sorted(st.session_state.tool_usage.items()):
                st.metric(TOOL_LABELS.get(tool_id, tool_id), count)
        else:
            st.caption("No tool calls yet")

        st.divider()
        st.header("Examples")
        for ex in EXAMPLES:
            if st.button(ex, use_container_width=True):
                st.session_state.pending_example = ex
                st.rerun()

    return selected_provider, model_name, temperature
