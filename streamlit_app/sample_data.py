"""
Dados simulados para demonstração
Sem dependências externas - Completamente autossuficiente
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_sample_users():
    """Gera usuários de exemplo"""
    return [
        {"id": 1, "email": "maria@workwell.com", "name": "Maria Silva", "department": "RH"},
        {"id": 2, "email": "joao@workwell.com", "name": "João Santos", "department": "TI"},
        {"id": 3, "email": "ana@workwell.com", "name": "Ana Costa", "department": "Marketing"},
        {"id": 4, "email": "carlos@workwell.com", "name": "Carlos Oliveira", "department": "Vendas"},
        {"id": 5, "email": "lucia@workwell.com", "name": "Lúcia Ferreira", "department": "Financeiro"},
    ]


def generate_sample_checkins(days=30):
    """Gera check-ins simulados dos últimos N dias"""
    checkins = []
    base_date = datetime.now()
    
    for day in range(days):
        date = base_date - timedelta(days=day)
        
        # Simula 3-5 check-ins por dia
        for user_id in range(1, 6):
            if np.random.random() > 0.2:  # 80% de chance de check-in
                checkins.append({
                    "id": len(checkins) + 1,
                    "user_id": user_id,
                    "date": date.strftime("%Y-%m-%d"),
                    "mood": np.random.randint(3, 10),
                    "energy": np.random.randint(2, 9),
                    "stress": np.random.randint(1, 8),
                    "notes": f"Check-in do dia {date.strftime('%d/%m')}"
                })
    
    return checkins


def generate_sample_analytics():
    """Gera dados de análise agregados"""
    return {
        "total_users": 5,
        "avg_mood": 6.8,
        "avg_energy": 5.9,
        "avg_stress": 4.2,
        "engagement_rate": 0.85,
        "burnout_risk": 0.15,
        "recommendations_count": 12,
        "departments": {
            "RH": {"avg_mood": 7.2, "risk": 0.05},
            "TI": {"avg_mood": 6.5, "risk": 0.25},
            "Marketing": {"avg_mood": 7.0, "risk": 0.10},
            "Vendas": {"avg_mood": 6.3, "risk": 0.30},
            "Financeiro": {"avg_mood": 6.9, "risk": 0.12},
        }
    }


def generate_recommendations():
    """Gera recomendações personalizadas"""
    return [
        {
            "title": "Pausas Regulares",
            "description": "Tire 5 minutos a cada hora para se alongar e descansar os olhos. Isso melhora foco e reduz fadiga.",
            "category": "Bem-estar",
            "impact": "Alto"
        },
        {
            "title": "Meditação Guiada",
            "description": "Pratique 10 minutos de meditação pela manhã para reduzir estresse e melhorar concentração.",
            "category": "Saúde Mental",
            "impact": "Alto"
        },
        {
            "title": "Exercício Físico",
            "description": "Caminhe 30 minutos por dia para melhorar energia, humor e reduzir estresse.",
            "category": "Atividade Física",
            "impact": "Muito Alto"
        },
        {
            "title": "Hidratação",
            "description": "Beba 2 litros de água por dia. Desidratação afeta concentração e humor.",
            "category": "Saúde",
            "impact": "Médio"
        },
        {
            "title": "Sono Adequado",
            "description": "Durma 7-8 horas por noite. Sono é fundamental para bem-estar e produtividade.",
            "category": "Descanso",
            "impact": "Muito Alto"
        },
        {
            "title": "Conexão Social",
            "description": "Passe tempo com colegas e amigos. Relacionamentos são essenciais para saúde mental.",
            "category": "Relacionamentos",
            "impact": "Alto"
        },
    ]


def get_burnout_prediction(mood, energy, stress):
    """
    Predição simples de risco de burnout usando ML
    Integração: Machine Learning + Python
    """
    # Modelo simplificado baseado em heurística
    score = (10 - mood) * 0.3 + (10 - energy) * 0.4 + stress * 0.3
    risk = min(1.0, max(0.0, score / 10))
    
    if risk > 0.7:
        level = "🔴 CRÍTICO"
        advice = "Procure ajuda profissional imediatamente"
    elif risk > 0.5:
        level = "🟠 ALTO"
        advice = "Implemente mudanças urgentes no seu estilo de vida"
    elif risk > 0.3:
        level = "🟡 MODERADO"
        advice = "Aumente atividades de bem-estar"
    else:
        level = "🟢 BAIXO"
        advice = "Continue mantendo seus hábitos saudáveis"
    
    return {
        "risk_score": round(risk, 2),
        "level": level,
        "advice": advice
    }


def get_trend_analysis(checkins_data):
    """
    Análise de tendências usando dados históricos
    Integração: Análise de Dados + Python
    """
    if not checkins_data:
        return None
    
    df = pd.DataFrame(checkins_data)
    
    # Calcula tendências
    mood_trend = df['mood'].iloc[-7:].mean() - df['mood'].iloc[-14:-7].mean()
    energy_trend = df['energy'].iloc[-7:].mean() - df['energy'].iloc[-14:-7].mean()
    stress_trend = df['stress'].iloc[-7:].mean() - df['stress'].iloc[-14:-7].mean()
    
    return {
        "mood_trend": "📈 Melhorando" if mood_trend > 0 else "📉 Piorando",
        "energy_trend": "📈 Melhorando" if energy_trend > 0 else "📉 Piorando",
        "stress_trend": "📉 Reduzindo" if stress_trend < 0 else "📈 Aumentando",
        "mood_change": round(mood_trend, 2),
        "energy_change": round(energy_trend, 2),
        "stress_change": round(stress_trend, 2),
    }
