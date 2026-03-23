import uuid

from langchain_core.language_models import BaseChatModel
from langgraph.store.base import BaseStore

from src.agent.prompts import MEMORY_EXTRACTION_PROMPT
from src.logging_config import get_logger

logger = get_logger("services.memory_extractor")


def extract_and_save_memory(
    llm: BaseChatModel,
    store: BaseStore,
    user_id: str,
    message: str,
    tools_used: list[str],
) -> None:
    if "save_memory" in tools_used:
        return

    try:
        response = llm.invoke(MEMORY_EXTRACTION_PROMPT.format(message=message))
        content = response.content.strip()

        if not content or content.upper() == "NONE":
            return

        store.put(
            ("user_memory", user_id),
            key=str(uuid.uuid4()),
            value={"content": content},
        )
        logger.info("Auto-saved memory for user %s: %s", user_id, content[:80])
    except Exception as e:
        logger.warning("Memory extraction failed: %s", e)
