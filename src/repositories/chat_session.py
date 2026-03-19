from typing import Optional

from sqlalchemy import cast, func, or_, select, String
from sqlalchemy.orm import Session

from src.models.chat_session import ChatSessionEntity


class ChatSessionRepository:
    def __init__(self, session: Session):
        self._session = session

    def create(self, thread_id: str, title: str) -> ChatSessionEntity:
        entity = ChatSessionEntity(thread_id=thread_id, title=title)
        self._session.add(entity)
        self._session.flush()
        return entity

    def find_by_thread_id(self, thread_id: str) -> Optional[ChatSessionEntity]:
        stmt = select(ChatSessionEntity).where(ChatSessionEntity.thread_id == thread_id)
        return self._session.execute(stmt).scalar_one_or_none()

    def update_title(self, thread_id: str, title: str) -> None:
        entity = self.find_by_thread_id(thread_id)
        if entity:
            entity.title = title

    def list_recent(self, limit: int = 50, query: str = "") -> list[ChatSessionEntity]:
        stmt = select(ChatSessionEntity)
        if query:
            q = query.strip()
            title_varchar = cast(ChatSessionEntity.title, String)
            stmt = stmt.where(
                or_(
                    ChatSessionEntity.title.ilike(f"%{q}%"),
                    func.word_similarity(func.lower(q), func.lower(title_varchar)) > 0.3,
                )
            )
        stmt = stmt.order_by(ChatSessionEntity.updated_at.desc()).limit(limit)
        return list(self._session.execute(stmt).scalars().all())

    def delete(self, thread_id: str) -> None:
        entity = self.find_by_thread_id(thread_id)
        if entity:
            self._session.delete(entity)
