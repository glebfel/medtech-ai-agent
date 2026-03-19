import os
import uuid

import streamlit as st
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

from src.agent.graph import build_agent
from src.agent.memory import create_checkpointer
from src.db import get_session, init_engine
from src.db.seed import seed_if_empty
from src.logging_config import get_logger, setup_logging
from src.settings import get_settings
from src.ui.chat import process_response, render_chat_history
from src.ui.sidebar import render_sidebar

logger = get_logger("main")


def _run_migrations(database_url: str) -> None:
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations applied")


@st.cache_resource
def _init_infrastructure():
    load_dotenv()
    settings = get_settings()

    setup_logging(settings.log_level)

    if settings.langchain_tracing_v2 and settings.langchain_api_key.get_secret_value():
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key.get_secret_value()
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
        logger.info("LangSmith tracing enabled (project=%s)", settings.langchain_project)

    _run_migrations(settings.database_url)

    init_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
    )
    with get_session() as session:
        seed_if_empty(session, settings.data_dir)

    checkpointer = create_checkpointer(settings.database_url).__enter__()
    checkpointer.setup()

    logger.info("Infrastructure initialized, LLM provider=%s", settings.llm_provider.value)
    return checkpointer, settings


def main() -> None:
    st.set_page_config(page_title="MedAssist", page_icon="\U0001f3e5", layout="wide")

    checkpointer, settings = _init_infrastructure()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "tool_usage" not in st.session_state:
        st.session_state.tool_usage = {}

    provider, temperature = render_sidebar(settings)

    needs_rebuild = (
        "agent" not in st.session_state
        or st.session_state.get("_temperature") != temperature
        or st.session_state.get("_provider") != provider
    )
    if needs_rebuild:
        settings_override = settings.model_copy(update={"llm_provider": provider})
        st.session_state.agent = build_agent(settings_override, checkpointer, temperature)
        st.session_state._temperature = temperature
        st.session_state._provider = provider

    agent = st.session_state.agent

    st.title("MedAssist")
    st.caption(
        "AI Clinical Decision Support Assistant | "
        "Not a substitute for professional medical judgment"
    )

    render_chat_history()

    pending = st.session_state.pop("pending_example", None)
    user_input = st.chat_input("Ask a medical question...")
    prompt = pending or user_input

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        config = {"configurable": {"thread_id": st.session_state.thread_id}}

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": prompt}]},
                    config=config,
                )
            assistant_msg = process_response(result)

        st.session_state.messages.append(assistant_msg)
        st.rerun()


if __name__ == "__main__":
    main()
