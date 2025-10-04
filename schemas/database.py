from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv
load_dotenv()

# Now other imports
from fastapi import FastAPI
import os
...


DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL is None or not DATABASE_URL.strip():
    raise RuntimeError("DATABASE_URL is not set!")

# Handle different database types
if DATABASE_URL.startswith("postgresql"):
    # For PostgreSQL (Supabase) - require SSL
    engine = create_engine(
        DATABASE_URL,
        connect_args={"sslmode": "require"}
    )
else:
    # For SQLite - use check_same_thread=False
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class AgentInteraction(Base):
    __tablename__ = "agent_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_type = Column(String(50), index=True)  # Added length for PostgreSQL
    user_query = Column(Text)
    agent_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)
