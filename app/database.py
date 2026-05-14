import os
import datetime
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime,
    func,
)
from sqlalchemy.orm import declarative_base, sessionmaker


DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user_admin:password_123@db:5432/mini_gemini_db",
)

engine = create_engine(
    DB_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ChatMessage(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), index=True, nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_chat_sessions():
    db = SessionLocal()

    try:
        sessions = (
            db.query(
                ChatMessage.session_id,
                func.min(ChatMessage.content).label("first_message"),
                func.max(ChatMessage.timestamp).label("last_update"),
            )
            .filter(ChatMessage.role == "user")
            .group_by(ChatMessage.session_id)
            .order_by(func.max(ChatMessage.timestamp).desc())
            .all()
        )

        result = []

        for session_id, first_message, last_update in sessions:
            title = first_message[:35] + "..." if len(first_message) > 35 else first_message

            result.append(
                {
                    "session_id": session_id,
                    "title": title or f"Chat {session_id}",
                    "last_update": last_update,
                }
            )

        return result

    finally:
        db.close()


def get_history_by_session(session_id):
    db = SessionLocal()

    try:
        messages = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.timestamp.asc())
            .all()
        )

        return [
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        ]

    finally:
        db.close()


def save_message(session_id, role, content):
    db = SessionLocal()

    try:
        new_message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
        )

        db.add(new_message)
        db.commit()

    finally:
        db.close()


def delete_session(session_id):
    db = SessionLocal()

    try:
        db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
        db.commit()

    finally:
        db.close()


def count_messages_by_session(session_id):
    db = SessionLocal()

    try:
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .count()
        )

    finally:
        db.close()