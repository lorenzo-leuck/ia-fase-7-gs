"""
Endpoints de Analytics
Integração: R + Python + Estatística
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict
import subprocess
import json
import os

from app.core.database import get_db
from app.core.security import get_current_user, require_role, anonymize_user_data
from app.models.wellbeing import WellbeingRecord
from app.core.config import settings

router = APIRouter()


class AnalyticsReport(BaseModel):
    summary: Dict
    correlations: Dict
    trends: Dict
    visualizations: List[str]


@router.get("/organizational", response_model=AnalyticsReport)
async def get_organizational_analytics(
    user: dict = Depends(require_role("manager")),
    db: Session = Depends(get_db)
):
    """
    Análises organizacionais agregadas (apenas gestores/RH)
    
    Integração:
    - R: Análises estatísticas avançadas
    - Python: Orquestração e processamento
    - Banco de Dados: Dados agregados e anonimizados
    - Cybersecurity: LGPD compliance (dados anonimizados)
    """
    
    # Busca dados agregados (anonimizados)
    all_records = db.query(WellbeingRecord).all()
    
    if len(all_records) < 10:
        raise HTTPException(
            status_code=400,
            detail="Dados insuficientes para análise organizacional"
        )
    
    # Prepara dados anonimizados para análise em R
    anonymized_data = []
    for record in all_records:
        anonymized_data.append({
            'user_hash': anonymize_user_data(record.user_id),
            'mood_score': record.mood_score,
            'energy_score': record.energy_score,
            'stress_score': record.stress_score,
            'sleep_quality': record.sleep_quality,
            'work_hours': record.work_hours,
            'date': record.created_at.isoformat()
        })
    
    # Salva dados temporários para R
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(anonymized_data, f)
        temp_file = f.name
    
    try:
        # Executa script R para análises estatísticas
        r_script_path = os.path.join(settings.R_SCRIPT_PATH, "organizational_analysis.R")
        
        if os.path.exists(r_script_path):
            result = subprocess.run(
                ['Rscript', r_script_path, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse resultado do R
                r_output = json.loads(result.stdout)
            else:
                # Fallback: análise básica em Python
                r_output = _basic_analytics(anonymized_data)
        else:
            # Fallback se R não disponível
            r_output = _basic_analytics(anonymized_data)
    
    finally:
        # Remove arquivo temporário
        os.unlink(temp_file)
    
    return r_output


def _basic_analytics(data: List[Dict]) -> Dict:
    """
    Análise básica em Python (fallback se R não disponível)
    """
    import pandas as pd
    import numpy as np
    
    df = pd.DataFrame(data)
    
    summary = {
        'total_records': len(df),
        'unique_users': df['user_hash'].nunique(),
        'avg_mood': float(df['mood_score'].mean()),
        'avg_energy': float(df['energy_score'].mean()),
        'avg_stress': float(df['stress_score'].mean()),
        'avg_sleep': float(df['sleep_quality'].mean()),
        'avg_work_hours': float(df['work_hours'].mean())
    }
    
    # Correlações
    correlations = df[['mood_score', 'energy_score', 'stress_score', 'sleep_quality', 'work_hours']].corr().to_dict()
    
    # Tendências (últimos 7 vs 30 dias)
    df['date'] = pd.to_datetime(df['date'])
    recent_7d = df[df['date'] >= df['date'].max() - pd.Timedelta(days=7)]
    
    trends = {
        'mood_trend': float(recent_7d['mood_score'].mean() - df['mood_score'].mean()),
        'stress_trend': float(recent_7d['stress_score'].mean() - df['stress_score'].mean())
    }
    
    return {
        'summary': summary,
        'correlations': correlations,
        'trends': trends,
        'visualizations': []
    }


@router.get("/personal")
async def get_personal_analytics(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Análises pessoais do usuário
    """
    user_id = int(user['sub'])
    
    records = db.query(WellbeingRecord).filter(
        WellbeingRecord.user_id == user_id
    ).all()
    
    if not records:
        return {
            'summary': {},
            'message': 'Nenhum registro encontrado'
        }
    
    import pandas as pd
    df = pd.DataFrame([
        {
            'mood': r.mood_score,
            'energy': r.energy_score,
            'stress': r.stress_score,
            'sleep': r.sleep_quality,
            'work_hours': r.work_hours
        }
        for r in records
    ])
    
    return {
        'summary': {
            'total_records': len(records),
            'avg_mood': float(df['mood'].mean()),
            'avg_energy': float(df['energy'].mean()),
            'avg_stress': float(df['stress'].mean()),
            'avg_sleep': float(df['sleep'].mean()),
            'avg_work_hours': float(df['work_hours'].mean())
        },
        'trends': {
            'mood_std': float(df['mood'].std()),
            'stress_std': float(df['stress'].std())
        }
    }
