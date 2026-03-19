from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent

from src.agent.llm import create_llm
from src.agent.prompts import SYSTEM_PROMPT
from src.settings import Settings
from src.tools import all_tools


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
        checkpointer=checkpointer,
    )
