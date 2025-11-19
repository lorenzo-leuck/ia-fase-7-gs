"""
Configurações da aplicação
Sem dependências de .env - Completamente autossuficiente
"""

from typing import List


class Settings:
    """
    Configurações da aplicação - Valores padrão sem .env
    Totalmente autossuficiente para demonstração
    """
    
    # Database (SQLite - sem dependências externas)
    DATABASE_URL: str = "sqlite:///./vida_trabalho.db"
    
    # Security (Cybersecurity)
    SECRET_KEY: str = "workwell-secret-key-2024-fiap-gs-phase7-secure"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "workwell-encryption-key-32-bytes-minimum-secure"
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://streamlit:8501"
    ]
    
    # ML Models
    MODEL_PATH: str = "./models"
    RETRAIN_INTERVAL_DAYS: int = 7
    
    # Monitoring
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting (Cybersecurity)
    RATE_LIMIT_PER_MINUTE: int = 60


# Singleton instance
settings = Settings()
