import uuid
from typing import Any

import streamlit as st
from st_keyup import st_keyup
from streamlit_js_eval import streamlit_js_eval

from src.agent.health import (
    check_anthropic,
    check_gigachat,
    check_ollama,
    check_openai,
    list_anthropic_models,
    list_gigachat_models,
    list_ollama_models,
    list_openai_models,
    pull_ollama_model,
)
from src.schemas.enums import LLMProvider
from src.services.chat_session import ChatSessionService
from src.settings import Settings, get_settings
from src.ui.constants import OLLAMA_MODEL_INFO, PROVIDER_MODELS

_COOKIE_MAX_AGE = 365 * 86400
_COOKIE_PROVIDER = "medassist_provider"
_COOKIE_MODEL = "medassist_model"
_COOKIE_TEMPERATURE = "medassist_temperature"


def _read_cookie(name: str) -> str | None:
    return st.context.cookies.get(name)


def _set_cookie(name: str, value: str) -> None:
    streamlit_js_eval(
        js_expressions=f"document.cookie = '{name}={value}; path=/; max-age={_COOKIE_MAX_AGE}; SameSite=Lax'",
        key=f"_set_{name}",
    )


_NO_KEY_ERRORS = {"API-ключ не задан", "Client ID / Secret не заданы"}

_PROVIDER_DISPLAY_NAMES: dict[LLMProvider, str] = {
    LLMProvider.OPENAI: "OpenAI",
    LLMProvider.ANTHROPIC: "Anthropic",
    LLMProvider.GIGACHAT: "GigaChat",
    LLMProvider.OLLAMA: "Ollama",
}


def _provider_label(status: tuple[bool, str], provider: LLMProvider) -> str:
    name = _PROVIDER_DISPLAY_NAMES.get(provider, provider.value)
    ok, err = status
    if ok:
        return f"{name} — connected \u2705"
    if err in _NO_KEY_ERRORS:
        return f"{name} — no key \u2b1c"
    return f"{name} — error \u274c"


def _check_provider(settings: Settings, provider: LLMProvider) -> tuple[bool, str]:
    timeout = settings.health_check_timeout

    if provider == LLMProvider.OPENAI:
        key = settings.openai_api_key.get_secret_value()
        if not key:
            return False, "API-ключ не задан"
        return check_openai(key, timeout=timeout, verify_ssl=settings.verify_ssl)

    if provider == LLMProvider.ANTHROPIC:
        key = settings.anthropic_api_key.get_secret_value()
        if not key:
            return False, "API-ключ не задан"
        return check_anthropic(key, timeout=timeout, verify_ssl=settings.verify_ssl)

    if provider == LLMProvider.GIGACHAT:
        creds = settings.gigachat_credentials
        if not creds:
            return False, "Client ID / Secret не заданы"
        return check_gigachat(
            creds,
            scope=settings.gigachat_scope,
            verify_ssl=settings.verify_ssl,
            timeout=timeout,
        )

    if provider == LLMProvider.OLLAMA:
        return check_ollama(settings.ollama_base_url, timeout=timeout)

    return False, "Unknown provider"


def _get_provider_models(
    settings: Settings, selected_provider: LLMProvider, available: bool
) -> list[str]:
    fallback = PROVIDER_MODELS.get(selected_provider.value, [])
    if not available:
        return fallback

    timeout = settings.health_check_timeout
    if selected_provider == LLMProvider.OPENAI:
        models = list_openai_models(
            settings.openai_api_key.get_secret_value(),
            timeout=timeout,
            verify_ssl=settings.verify_ssl,
        )
    elif selected_provider == LLMProvider.ANTHROPIC:
        models = list_anthropic_models(
            settings.anthropic_api_key.get_secret_value(),
            timeout=timeout,
            verify_ssl=settings.verify_ssl,
        )
    elif selected_provider == LLMProvider.GIGACHAT:
        models = list_gigachat_models(
            settings.gigachat_credentials,
            scope=settings.gigachat_scope,
            verify_ssl=settings.verify_ssl,
            timeout=timeout,
        )
    else:
        return fallback

    return models or fallback


def _render_ollama_model_selector(base_url: str) -> str:
    installed = list_ollama_models(base_url)
    compatible = [m for m in installed if m["tools"]]
    compatible_names = [m["name"] for m in compatible]

    if compatible:
        model_name = st.selectbox(
            "Model",
            compatible_names,
            index=0,
            format_func=lambda n: next(
                (
                    f"{m['name']} ({m['params']}, {m['size_gb']} GB)"
                    for m in compatible
                    if m["name"] == n
                ),
                n,
            ),
        )
    else:
        st.caption("No compatible models (need tool calling support)")
        model_name = ""

    all_installed_names = [m["name"] for m in installed]
    available_to_pull = [
        m for m in PROVIDER_MODELS["ollama"] if m not in all_installed_names
    ]
    with st.expander("Pull new model"):
        if available_to_pull:
            selected = st.selectbox(
                "Select model",
                available_to_pull,
                key="_ollama_pull_select",
                format_func=lambda m: f"{m} ({OLLAMA_MODEL_INFO[m]})"
                if m in OLLAMA_MODEL_INFO
                else m,
            )
            if st.button("Pull", key="_ollama_pull_btn", use_container_width=True):
                with st.spinner(f"Pulling {selected}..."):
                    success, err = pull_ollama_model(base_url, model_name=selected)
                if success:
                    st.success(f"{selected} installed")
                    list_ollama_models.clear()
                    st.rerun()
                else:
                    st.error(err)
        else:
            st.caption("All popular models installed")

    return model_name


@st.dialog("Delete chat?")
def _confirm_delete(thread_id: str, title: str) -> None:
    st.markdown(f"This will delete **{title}**.")
    col_cancel, col_delete = st.columns(2)
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col_delete:
        if st.button("Delete", type="primary", use_container_width=True):
            ChatSessionService.delete(thread_id)
            if st.session_state.get("thread_id") == thread_id:
                st.session_state.thread_id = str(uuid.uuid4())
                st.session_state.messages = []
            st.rerun()


@st.dialog("Rename chat")
def _rename_dialog(thread_id: str, title: str) -> None:
    new_title = st.text_input("New title", value=title)
    col_cancel, col_save = st.columns(2)
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()
    with col_save:
        if (
            st.button("Save", type="primary", use_container_width=True)
            and new_title.strip()
        ):
            ChatSessionService.rename(thread_id=thread_id, title=new_title.strip())
            if (
                st.session_state.get("_current_title")
                and st.session_state.get("thread_id") == thread_id
            ):
                st.session_state._current_title = new_title.strip()
            st.rerun()


def _render_chat_history_section() -> None:
    limit = get_settings().max_visible_chats

    total = ChatSessionService.count()
    label = f"Chat History ({total})" if total > limit else "Chat History"
    st.header(label)

    search_query = st_keyup(
        "",
        placeholder="Search...",
        key="_chat_search",
        debounce=300,
    )
    sessions = ChatSessionService.list_recent(query=search_query, limit=limit)
    if not sessions:
        st.caption("No conversations found" if search_query else "No conversations yet")
        return

    for s in sessions:
        tid = s["thread_id"]
        col_title, col_menu = st.columns([5, 1], vertical_alignment="center")
        with col_title:
            if st.button(s["title"], key=f"sess_{tid}", use_container_width=True):
                st.session_state.thread_id = tid
                st.session_state.messages = []
                st.session_state.pop("agent", None)
                st.session_state._load_from_history = True
                st.rerun()
        with col_menu:
            with st.popover("\u22ee", use_container_width=True):
                if st.button(
                    "\u270f\ufe0f Rename", key=f"ren_{tid}", use_container_width=True
                ):
                    _rename_dialog(thread_id=tid, title=s["title"])
                if st.button(
                    "\U0001f5d1 Delete", key=f"del_{tid}", use_container_width=True
                ):
                    _confirm_delete(thread_id=tid, title=s["title"])


def _render_user_memory_section(store: Any) -> None:
    st.header("Patient Memory")
    user_id = st.session_state.get("_user_id", "default")

    try:
        items = store.search(("user_memory", user_id))
    except Exception:
        items = []

    if not items:
        st.caption("No saved patient data")
        return

    for item in items:
        val = item.value
        if isinstance(val, dict):
            content = val.get("content", {})
            if isinstance(content, dict):
                text = content.get("content", str(val))
            elif isinstance(content, str):
                text = content
            elif "data" in val:
                text = f"{item.key}: {val['data']}"
            else:
                text = str(val)
        else:
            text = str(val)

        col_fact, col_del = st.columns([5, 1], vertical_alignment="center")
        with col_fact:
            st.caption(text)
        with col_del:
            if st.button("\u2715", key=f"mem_del_{item.key}"):
                store.delete(("user_memory", user_id), key=item.key)
                st.rerun()

    if st.button("Clear all memory", use_container_width=True):
        for item in items:
            store.delete(("user_memory", user_id), key=item.key)
        st.rerun()


def render_sidebar(
    settings: Settings, store: Any = None
) -> tuple[LLMProvider, str, float]:
    with st.sidebar:
        st.header("Settings")

        providers = list(LLMProvider)
        statuses: dict[LLMProvider, tuple[bool, str]] = {}
        for p in providers:
            statuses[p] = _check_provider(settings, p)

        saved_provider = _read_cookie(_COOKIE_PROVIDER)
        try:
            default_idx = providers.index(LLMProvider(saved_provider))
        except (ValueError, KeyError):
            default_idx = providers.index(settings.default_llm_provider)

        selected_provider = st.selectbox(
            "LLM Provider",
            providers,
            index=default_idx,
            format_func=lambda p: _provider_label(statuses[p], provider=p),
        )

        ok, err = statuses[selected_provider]
        if not ok:
            st.warning(err)

        saved_model = _read_cookie(_COOKIE_MODEL)

        if selected_provider == LLMProvider.OLLAMA and ok:
            model_name = _render_ollama_model_selector(settings.ollama_base_url)
        else:
            models = _get_provider_models(
                settings, selected_provider=selected_provider, available=ok
            )
            if models:
                model_idx = models.index(saved_model) if saved_model in models else 0
                model_name = st.selectbox("Model", models, index=model_idx)
            else:
                model_name = ""

        saved_temp = _read_cookie(_COOKIE_TEMPERATURE)
        try:
            default_temp = float(saved_temp)
        except (TypeError, ValueError):
            default_temp = 0.1
        temperature = st.slider("Temperature", 0.0, 1.0, default_temp, 0.05)

        if selected_provider.value != saved_provider:
            _set_cookie(_COOKIE_PROVIDER, selected_provider.value)
        if model_name != saved_model:
            _set_cookie(_COOKIE_MODEL, model_name)
        if str(temperature) != saved_temp:
            _set_cookie(_COOKIE_TEMPERATURE, str(temperature))

        if st.button("New conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.session_state.pop("_current_title", None)
            st.rerun()

        st.divider()
        _render_chat_history_section()

        if store is not None:
            st.divider()
            _render_user_memory_section(store)

    return selected_provider, model_name, temperature
