import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv("DATABASE_URL", "postgresql://user_admin:password_123@db:5432/mini_gemini_db")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class ChatMessage(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(50), index=True)
    role = Column(String(20))
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_chat_sessions():
    db = SessionLocal()
    try:
        sessions = db.query(ChatMessage.session_id).distinct().all()
        return [s[0] for s in sessions if s[0]]
    finally:
        db.close()

def get_history_by_session(session_id):
    db = SessionLocal()
    try:
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.timestamp).all()
        # Transformamos em lista de dicts para evitar erros de 'Detached Instance'
        return [{"role": m.role, "content": m.content} for m in messages]
    finally:
        db.close()

def save_message(session_id, role, content):
    db = SessionLocal()
    try:
        new_msg = ChatMessage(session_id=session_id, role=role, content=content)
        db.add(new_msg)
        db.commit()
    finally:
        db.close()