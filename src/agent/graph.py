from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langgraph.graph.state import CompiledStateGraph
from langmem import create_manage_memory_tool, create_search_memory_tool
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.base import BaseStore
from pydantic import BaseModel, Field

from src.agent.llm import create_llm
from src.agent.prompts import SYSTEM_PROMPT
from src.logging_config import get_logger
from src.schemas.enums import LLMProvider
from src.settings import Settings, get_settings
from src.tools import all_tools

logger = get_logger("agent.graph")

_MEMORY_NAMESPACE = ("user_memory", "{langgraph_user_id}")


class _SearchMemoryGigaChatArgs(BaseModel):
    query: str = Field(description="Search query for patient memories")
    limit: int = Field(default=10, description="Maximum number of results")
    offset: int = Field(default=0, description="Result offset")


class _SaveMemoryGigaChatArgs(BaseModel):
    content: str = Field(default="", description="Memory content to save")
    action: str = Field(
        default="create", description="Action: create, update, or delete"
    )
    id: str = Field(default="", description="Memory ID (required for update/delete)")


def _trim_history(state: dict) -> dict:
    messages = state.get("messages", [])

    trimmed = trim_messages(
        messages,
        max_tokens=get_settings().max_context_tokens,
        token_counter=count_tokens_approximately,
        strategy="last",
        start_on="human",
        include_system=True,
        allow_partial=False,
    )

    if len(trimmed) < len(messages):
        logger.info(
            "Context trimmed: %d → %d messages",
            len(messages),
            len(trimmed),
        )

    return {"llm_input_messages": trimmed}


def build_agent(
    settings: Settings,
    checkpointer: PostgresSaver,
    store: BaseStore,
    temperature: float = 0.1,
    model_name: str = "",
) -> CompiledStateGraph:
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

    if settings.default_llm_provider == LLMProvider.GIGACHAT:
        for tool in memory_tools:
            if tool.name == "search_memory":
                tool.args_schema = _SearchMemoryGigaChatArgs
            elif tool.name == "save_memory":
                tool.args_schema = _SaveMemoryGigaChatArgs

    return create_react_agent(
        model=llm,
        tools=all_tools + memory_tools,
        prompt=SYSTEM_PROMPT,
        pre_model_hook=_trim_history,
        checkpointer=checkpointer,
        store=store,
    )
