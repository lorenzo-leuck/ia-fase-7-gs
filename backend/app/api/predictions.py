"""
Endpoints de Predições ML
Integração: Machine Learning + Redes Neurais + Python
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.wellbeing import WellbeingRecord
from app.ml.model_loader import get_burnout_predictor, get_lstm_analyzer

router = APIRouter()


class BurnoutPrediction(BaseModel):
    probability: float
    risk_level: str
    recommendations: List[str]
    confidence: float


class TimeSeriesPrediction(BaseModel):
    predictions: List[Dict]
    anomalies: List[Dict]


@router.get("/burnout", response_model=BurnoutPrediction)
async def predict_burnout(
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Prediz risco de burnout usando Machine Learning
    
    Integração:
    - Machine Learning: Random Forest + Gradient Boosting
    - Feature Engineering: Análise de tendências temporais
    - Banco de Dados: Consulta histórico do usuário
    """
    user_id = int(user['sub'])
    
    # Busca registros dos últimos 30 dias
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    records = db.query(WellbeingRecord).filter(
        WellbeingRecord.user_id == user_id,
        WellbeingRecord.created_at >= thirty_days_ago
    ).order_by(WellbeingRecord.created_at).all()
    
    if len(records) < 7:
        raise HTTPException(
            status_code=400,
            detail="Dados insuficientes. Registre pelo menos 7 dias de bem-estar."
        )
    
    # Converte para dict
    records_dict = [
        {
            'mood_score': r.mood_score,
            'energy_score': r.energy_score,
            'stress_score': r.stress_score,
            'sleep_quality': r.sleep_quality,
            'work_hours': r.work_hours,
            'created_at': r.created_at
        }
        for r in records
    ]
    
    # Predição usando ML
    predictor = get_burnout_predictor()
    probability, risk_level, recommendations = predictor.predict(records_dict)
    
    # Calcula confiança baseada na quantidade de dados
    confidence = min(len(records) / 30, 1.0)
    
    return {
        "probability": probability,
        "risk_level": risk_level,
        "recommendations": recommendations,
        "confidence": confidence
    }


@router.get("/timeseries", response_model=TimeSeriesPrediction)
async def predict_timeseries(
    days_ahead: int = 7,
    user: Dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Prediz tendências futuras usando Redes Neurais LSTM
    
    Integração:
    - Redes Neurais: LSTM para séries temporais
    - Deep Learning: TensorFlow/Keras
    - Análise de anomalias
    """
    user_id = int(user['sub'])
    
    # Busca registros dos últimos 60 dias
    sixty_days_ago = datetime.utcnow() - timedelta(days=60)
    records = db.query(WellbeingRecord).filter(
        WellbeingRecord.user_id == user_id,
        WellbeingRecord.created_at >= sixty_days_ago
    ).order_by(WellbeingRecord.created_at).all()
    
    if len(records) < 14:
        raise HTTPException(
            status_code=400,
            detail="Dados insuficientes. Registre pelo menos 14 dias."
        )
    
    # Converte para DataFrame
    import pandas as pd
    df = pd.DataFrame([
        {
            'mood_score': r.mood_score,
            'energy_score': r.energy_score,
            'stress_score': r.stress_score,
            'sleep_quality': r.sleep_quality,
            'created_at': r.created_at
        }
        for r in records
    ])
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.set_index('created_at')
    
    # Predição usando LSTM
    analyzer = get_lstm_analyzer()
    
    if not analyzer.is_trained:
        raise HTTPException(
            status_code=503,
            detail="Modelo LSTM em treinamento. Tente novamente em alguns minutos."
        )
    
    # Prediz próximos dias
    predictions_df = analyzer.predict_next_days(df, days_ahead=days_ahead)
    predictions = predictions_df.to_dict('records')
    
    # Detecta anomalias
    anomalies = analyzer.detect_anomalies(df)
    
    return {
        "predictions": predictions,
        "anomalies": anomalies
    }
