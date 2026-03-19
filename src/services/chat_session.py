from src.db import get_session
from src.logging_config import get_logger
from src.repositories.chat_session import ChatSessionRepository

logger = get_logger("services.chat_session")


def generate_title(message: str) -> str:
    return message[:60].strip() + ("..." if len(message) > 60 else "")


def save_session(thread_id: str, title: str) -> None:
    with get_session() as session:
        repo = ChatSessionRepository(session)
        existing = repo.find_by_thread_id(thread_id)
        if not existing:
            repo.create(thread_id=thread_id, title=title)


def rename_session(thread_id: str, title: str) -> None:
    with get_session() as session:
        repo = ChatSessionRepository(session)
        repo.update_title(thread_id=thread_id, title=title)


def list_sessions(query: str = "") -> list[dict]:
    with get_session() as session:
        repo = ChatSessionRepository(session)
        entities = repo.list_recent(query=query)
        return [
            {
                "thread_id": e.thread_id,
                "title": e.title,
                "created_at": e.created_at,
                "updated_at": e.updated_at,
            }
            for e in entities
        ]


def delete_session(thread_id: str) -> None:
    with get_session() as session:
        repo = ChatSessionRepository(session)
        repo.delete(thread_id)


def restore_messages(checkpointer, thread_id: str) -> list[dict]:
    try:
        config = {"configurable": {"thread_id": thread_id}}
        state = checkpointer.get(config)
        if not state or "channel_values" not in state:
            return []

        messages = state["channel_values"].get("messages", [])
        restored = []
        for msg in messages:
            if msg.type == "tool":
                continue
            role = "assistant" if msg.type == "ai" else "user"
            content = msg.content if isinstance(msg.content, str) else str(msg.content)
            if content:
                restored.append({"role": role, "content": content})
        return restored
    except Exception as e:
        logger.warning("Failed to restore messages from checkpointer: %s", e)
        return []
