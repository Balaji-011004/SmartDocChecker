"""
SQLAlchemy engine and session factory.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,  # health-check connections for PostgreSQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
