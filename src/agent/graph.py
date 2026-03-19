from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent

from src.agent.llm import create_llm
from src.agent.prompts import SYSTEM_PROMPT
from src.settings import Settings, get_settings
from src.tools import all_tools


def _trim_history(state: dict) -> dict:
    max_messages = get_settings().max_history_messages
    messages = state.get("messages", [])
    if len(messages) <= max_messages:
        return {"llm_input_messages": messages}

    trimmed = messages[-max_messages:]
    for i, msg in enumerate(trimmed):
        if isinstance(msg, HumanMessage):
            trimmed = trimmed[i:]
            break

    return {"llm_input_messages": trimmed}


def build_agent(
    settings: Settings,
    checkpointer: PostgresSaver,
    temperature: float = 0.1,
    model_name: str = "",
):
    llm = create_llm(settings, temperature=temperature, model_name=model_name)

    return create_react_agent(
        model=llm,
        tools=all_tools,
        prompt=SYSTEM_PROMPT,
        pre_model_hook=_trim_history,
        checkpointer=checkpointer,
    )
