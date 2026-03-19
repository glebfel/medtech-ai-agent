import time
import uuid

import streamlit as st

from src.agent.graph import build_agent
from src.logging_config import get_logger
from src.services.chat_session import generate_title, restore_messages, save_session
from src.services.infrastructure import init_infrastructure
from src.ui.chat import process_response, render_chat_history, render_title_editor
from src.ui.sidebar import render_sidebar

logger = get_logger("main")


@st.cache_resource
def _init():
    return init_infrastructure()


def main() -> None:
    st.set_page_config(page_title="MedAssistAI", page_icon="\U0001f3e5", layout="wide")

    checkpointer, settings = _init()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "tool_usage" not in st.session_state:
        st.session_state.tool_usage = {}

    if st.session_state.pop("_load_from_history", False):
        st.session_state.messages = restore_messages(
            checkpointer, thread_id=st.session_state.thread_id,
        )

    provider, model_name, temperature = render_sidebar(settings)

    needs_rebuild = (
        "agent" not in st.session_state
        or st.session_state.get("_temperature") != temperature
        or st.session_state.get("_provider") != provider
        or st.session_state.get("_model") != model_name
    )
    if needs_rebuild:
        settings_override = settings.model_copy(update={"default_llm_provider": provider})
        st.session_state.agent = build_agent(
            settings_override, checkpointer=checkpointer, temperature=temperature, model_name=model_name,
        )
        st.session_state._temperature = temperature
        st.session_state._provider = provider
        st.session_state._model = model_name
        logger.info("Agent rebuilt: provider=%s, model=%s, temperature=%s", provider, model_name, temperature)

    agent = st.session_state.agent

    st.title("MedAssistAI")
    st.markdown(
        "<p style='font-size:1.1rem; color:gray; margin-top:-10px;'>"
        "AI Clinical Decision Support Assistant</p>",
        unsafe_allow_html=True,
    )

    render_title_editor()
    render_chat_history()

    pending = st.session_state.pop("pending_example", None)
    user_input = st.chat_input("Ask a medical question...")
    prompt = pending or user_input

    if prompt:
        prompt = prompt.strip()
        if not prompt:
            st.rerun()
        if len(prompt) > settings.max_input_length:
            st.warning(f"Message too long (max {settings.max_input_length} chars)")
            st.rerun()

        thread_id = st.session_state.thread_id
        logger.info("User message: thread_id=%s, provider=%s, model=%s, length=%d", thread_id, provider, model_name, len(prompt))

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        config = {"configurable": {"thread_id": thread_id}}

        with st.chat_message("assistant"):
            try:
                start = time.monotonic()
                with st.spinner("Analyzing..."):
                    result = agent.invoke(
                        {"messages": [{"role": "user", "content": prompt}]},
                        config=config,
                    )
                duration = time.monotonic() - start
                assistant_msg = process_response(result)
                logger.info(
                    "Agent response: thread_id=%s, duration=%.2fs, tools=%s",
                    thread_id, duration, assistant_msg.get("tools_used", []),
                )
            except Exception:
                logger.exception("Agent invocation failed: thread_id=%s, provider=%s, model=%s", thread_id, provider, model_name)
                err_msg = "An error occurred. Please try again or switch the model."
                st.error(err_msg)
                assistant_msg = {"role": "assistant", "content": err_msg}

        st.session_state.messages.append(assistant_msg)

        if len(st.session_state.messages) == 2:
            title = generate_title(prompt)
            save_session(thread_id=thread_id, title=title)
            st.session_state._current_title = title

        st.rerun()


if __name__ == "__main__":
    main()
