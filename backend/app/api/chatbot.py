"""
Endpoints do Chatbot Inteligente
Integração: AICSS + NLP + Transformers
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.ml.model_loader import get_chatbot
from app.models.wellbeing import WellbeingRecord
from datetime import datetime, timedelta

router = APIRouter()


class ChatMessage(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    sentiment: str
    sentiment_score: float
    category: str
    requires_attention: bool
    tips: List[str]


@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Conversa com o chatbot inteligente
    
    Integração:
    - AICSS: Processamento cognitivo e semântico
    - NLP: Análise de sentimento com Transformers
    - Contexto: Usa histórico do usuário para personalização
    """
    user_id = int(user['sub'])
    
    # Busca contexto recente do usuário
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_records = db.query(WellbeingRecord).filter(
        WellbeingRecord.user_id == user_id,
        WellbeingRecord.created_at >= seven_days_ago
    ).all()
    
    # Prepara contexto
    context = {}
    if recent_records:
        context['recent_stress'] = sum(r.stress_score for r in recent_records) / len(recent_records)
        context['sleep_quality'] = sum(r.sleep_quality for r in recent_records) / len(recent_records)
        if recent_records[-1].burnout_risk_score:
            context['burnout_risk'] = recent_records[-1].burnout_risk_score
    
    # Gera resposta
    chatbot = get_chatbot()
    response_data = chatbot.generate_response(message.message, context)
    
    # Obtém dicas relacionadas
    tips = chatbot.get_wellness_tips(response_data['category'])
    
    return {
        **response_data,
        "tips": tips
    }


@router.get("/tips", response_model=List[str])
async def get_tips(category: str = "general"):
    """
    Retorna dicas de bem-estar por categoria
    """
    chatbot = get_chatbot()
    return chatbot.get_wellness_tips(category)
