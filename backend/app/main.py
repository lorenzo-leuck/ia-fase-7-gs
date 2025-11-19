"""
Vida & Trabalho - Backend API
Global Solution FIAP - Fase 7

Este é o ponto de entrada principal da API REST que integra:
- Machine Learning para predição de burnout
- Redes Neurais para análise de séries temporais
- NLP para análise de sentimentos
- Segurança com JWT e criptografia
- Banco de dados SQLite
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, users, wellbeing, predictions, analytics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter (Cybersecurity)
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação
    - Startup: Cria tabelas, carrega modelos ML
    - Shutdown: Limpa recursos
    """
    # Startup
    logger.info("🚀 Starting Vida & Trabalho Backend...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created")
    
    # Load ML models
    from app.ml.model_loader import load_models
    load_models()
    logger.info("✅ ML models loaded")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Vida & Trabalho Backend...")


# Initialize FastAPI app
app = FastAPI(
    title="Vida & Trabalho API",
    description="API para monitoramento de bem-estar e saúde mental no trabalho",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware (Security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers Middleware (Cybersecurity)
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """
    Adiciona headers de segurança em todas as respostas
    - X-Content-Type-Options: Previne MIME sniffing
    - X-Frame-Options: Previne clickjacking
    - X-XSS-Protection: Proteção contra XSS
    - Strict-Transport-Security: Força HTTPS
    """
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Endpoint de health check para monitoramento
    Usado por load balancers e ferramentas de monitoramento
    """
    return {
        "status": "healthy",
        "service": "WorkWell AI",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Endpoint raiz com informações da API
    """
    return {
        "message": "WorkWell AI - O Futuro do Trabalho",
        "description": "Plataforma inteligente de bem-estar no trabalho",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(wellbeing.router, prefix="/api/v1/wellbeing", tags=["Wellbeing"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Predictions"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para exceções não tratadas
    Registra o erro e retorna resposta genérica (não expõe detalhes internos)
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "Ocorreu um erro inesperado. Por favor, tente novamente."
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
