from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.prebuilt import create_react_agent

from src.agent.llm import create_llm
from src.agent.prompts import SYSTEM_PROMPT
from src.settings import Settings
from src.tools import all_tools


def build_agent(settings: Settings, checkpointer: PostgresSaver, temperature: float = 0.1):
    """Construct the MedAssist ReAct agent graph.

    Uses LangGraph create_react_agent which internally builds:
    - call_model node: invokes LLM with bound tools
    - tool execution node: runs the selected tool
    - conditional edges: loops until LLM produces a final response

    The checkpointer enables persistent conversation memory via thread_id.
    """
    llm = create_llm(settings, temperature=temperature)

    return create_react_agent(
        model=llm,
        tools=all_tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,
    )
