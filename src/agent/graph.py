from langchain_core.messages import HumanMessage
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.base import BaseStore

from src.agent.llm import create_llm
from src.agent.prompts import SYSTEM_PROMPT
from src.settings import Settings, get_settings
from src.tools import all_tools

_MEMORY_NAMESPACE = ("user_memory", "{langgraph_user_id}")


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
    store: BaseStore,
    temperature: float = 0.1,
    model_name: str = "",
):
    llm = create_llm(settings, temperature=temperature, model_name=model_name)

    memory_tools = [
        create_manage_memory_tool(
            namespace=_MEMORY_NAMESPACE,
            instructions="Save important patient information: age, weight, medications, "
            "allergies, chronic conditions. Call when user shares personal medical data.",
            name="save_memory",
        ),
        create_search_memory_tool(
            namespace=_MEMORY_NAMESPACE,
            instructions="Search saved patient information to personalize advice. "
            "Call at the start of a conversation or when you need patient context.",
            name="search_memory",
        ),
    ]

    return create_react_agent(
        model=llm,
        tools=all_tools + memory_tools,
        prompt=SYSTEM_PROMPT,
        pre_model_hook=_trim_history,
        checkpointer=checkpointer,
        store=store,
    )
