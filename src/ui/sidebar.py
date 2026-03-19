import uuid

import streamlit as st

from src.schemas.enums import LLMProvider
from src.settings import Settings
from src.ui.constants import EXAMPLES, TOOL_LABELS


def render_sidebar(settings: Settings) -> tuple[LLMProvider, float]:
    with st.sidebar:
        st.header("Settings")

        providers = [p.value for p in LLMProvider]
        default_idx = providers.index(settings.llm_provider.value)
        selected_provider = st.selectbox("LLM Provider", providers, index=default_idx)
        provider = LLMProvider(selected_provider)

        temperature = st.slider("Temperature", 0.0, 1.0, 0.1, 0.05)

        if st.button("New conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.thread_id = str(uuid.uuid4())
            st.rerun()

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

    return provider, temperature
