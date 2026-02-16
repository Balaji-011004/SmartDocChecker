"""
SQLAlchemy declarative base.
Import all models here so Alembic can auto-detect them.
"""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
