"""
Endpoints de Registros de Bem-Estar
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user, encrypt_data
from app.models.wellbeing import WellbeingRecord

router = APIRouter()


class WellbeingCreate(BaseModel):
    mood_score: int = Field(..., ge=1, le=10)
    energy_score: int = Field(..., ge=1, le=10)
    stress_score: int = Field(..., ge=1, le=10)
    sleep_quality: int = Field(..., ge=1, le=10)
    work_hours: float = Field(..., ge=0, le=24)
    notes: str = None


class WellbeingResponse(BaseModel):
    id: int
    mood_score: int
    energy_score: int
    stress_score: int
    sleep_quality: int
    work_hours: float
    overall_score: float
    sentiment_score: float = None
    created_at: datetime


@router.post("/", response_model=WellbeingResponse, status_code=201)
async def create_wellbeing_record(
    data: WellbeingCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cria registro diário de bem-estar
    
    Integração:
    - Banco de Dados: Armazena dados estruturados
    - Cybersecurity: Criptografa notas sensíveis
    - NLP: Analisa sentimento das notas
    """
    user_id = int(user['sub'])
    
    # Análise de sentimento das notas (se fornecidas)
    sentiment_score = None
    if data.notes:
        chatbot = get_chatbot()
        _, sentiment_score = chatbot.analyze_sentiment(data.notes)
        # Criptografa notas para privacidade
        encrypted_notes = encrypt_data(data.notes)
    else:
        encrypted_notes = None
    
    # Cria registro
    record = WellbeingRecord(
        user_id=user_id,
        mood_score=data.mood_score,
        energy_score=data.energy_score,
        stress_score=data.stress_score,
        sleep_quality=data.sleep_quality,
        work_hours=data.work_hours,
        notes=encrypted_notes,
        sentiment_score=sentiment_score
    )
    
    db.add(record)
    db.commit()
    db.refresh(record)
    
    return {
        "id": record.id,
        "mood_score": record.mood_score,
        "energy_score": record.energy_score,
        "stress_score": record.stress_score,
        "sleep_quality": record.sleep_quality,
        "work_hours": record.work_hours,
        "overall_score": record.overall_wellbeing_score,
        "sentiment_score": record.sentiment_score,
        "created_at": record.created_at
    }


@router.get("/history", response_model=List[WellbeingResponse])
async def get_wellbeing_history(
    days: int = 30,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retorna histórico de bem-estar do usuário"""
    user_id = int(user['sub'])
    
    start_date = datetime.utcnow() - timedelta(days=days)
    records = db.query(WellbeingRecord).filter(
        WellbeingRecord.user_id == user_id,
        WellbeingRecord.created_at >= start_date
    ).order_by(WellbeingRecord.created_at.desc()).all()
    
    return [
        {
            "id": r.id,
            "mood_score": r.mood_score,
            "energy_score": r.energy_score,
            "stress_score": r.stress_score,
            "sleep_quality": r.sleep_quality,
            "work_hours": r.work_hours,
            "overall_score": r.overall_wellbeing_score,
            "sentiment_score": r.sentiment_score,
            "created_at": r.created_at
        }
        for r in records
    ]
