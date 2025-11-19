"""
Configuração do banco de dados SQLite
Integração: Banco de Dados + Python
Sem dependências externas - Completamente autossuficiente
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create database engine (SQLite - no external dependencies)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency para obter sessão do banco de dados
    Usado em endpoints FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
