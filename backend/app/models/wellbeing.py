"""
Modelo de Registros de Bem-Estar
Integração: Banco de Dados + Python + Machine Learning
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class WellbeingRecord(Base):
    """
    Registro diário de bem-estar do colaborador
    
    Dados coletados:
    - Humor (1-10)
    - Energia (1-10)
    - Estresse (1-10)
    - Qualidade do sono (1-10)
    - Horas de trabalho
    - Notas adicionais (criptografadas)
    
    Esses dados são usados para:
    1. Machine Learning: Predição de burnout
    2. Redes Neurais: Análise de séries temporais
    3. Analytics: Insights organizacionais
    """
    __tablename__ = "wellbeing_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Métricas de bem-estar (escala 1-10)
    mood_score = Column(Integer, nullable=False)  # Humor
    energy_score = Column(Integer, nullable=False)  # Energia
    stress_score = Column(Integer, nullable=False)  # Estresse
    sleep_quality = Column(Integer, nullable=False)  # Qualidade do sono
    
    # Contexto de trabalho
    work_hours = Column(Float, nullable=False)  # Horas trabalhadas no dia
    
    # Notas adicionais (criptografadas para privacidade)
    notes = Column(Text, nullable=True)
    
    # Análise de sentimento (processada por NLP)
    sentiment_score = Column(Float, nullable=True)  # -1 (negativo) a 1 (positivo)
    
    # Predição de risco (calculada por ML)
    burnout_risk_score = Column(Float, nullable=True)  # 0 a 1 (probabilidade)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="wellbeing_records")
    
    def __repr__(self):
        return f"<WellbeingRecord(id={self.id}, user_id={self.user_id}, date={self.created_at})>"
    
    @property
    def overall_wellbeing_score(self) -> float:
        """
        Calcula score geral de bem-estar (0-10)
        Fórmula ponderada considerando todos os fatores
        """
        # Pesos baseados em literatura de psicologia organizacional
        weights = {
            'mood': 0.25,
            'energy': 0.20,
            'stress': 0.25,  # Invertido (menos estresse = melhor)
            'sleep': 0.30
        }
        
        score = (
            self.mood_score * weights['mood'] +
            self.energy_score * weights['energy'] +
            (11 - self.stress_score) * weights['stress'] +  # Inverte estresse
            self.sleep_quality * weights['sleep']
        )
        
        return round(score, 2)
