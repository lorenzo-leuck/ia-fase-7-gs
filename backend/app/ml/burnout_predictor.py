"""
Preditor de Burnout usando Machine Learning
Integração: Machine Learning + Python + Banco de Dados

Modelos implementados:
1. Random Forest Classifier - Classificação de risco
2. Gradient Boosting - Predição de probabilidade
3. Feature engineering com dados temporais
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class BurnoutPredictor:
    """
    Preditor de Burnout usando ensemble de modelos ML
    
    Features utilizadas:
    - Métricas de bem-estar (mood, energy, stress, sleep)
    - Tendências temporais (últimos 7, 14, 30 dias)
    - Variabilidade (desvio padrão)
    - Horas de trabalho
    - Padrões de declínio
    """
    
    def __init__(self):
        self.rf_model = None
        self.gb_model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
    
    def engineer_features(self, records: List[Dict]) -> pd.DataFrame:
        """
        Feature engineering a partir dos registros de bem-estar
        
        Args:
            records: Lista de registros de bem-estar
        
        Returns:
            DataFrame com features engineered
        """
        df = pd.DataFrame(records)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.sort_values('created_at')
        
        features = {}
        
        # Features básicas (últimos 7 dias)
        recent = df.tail(7)
        features['avg_mood_7d'] = recent['mood_score'].mean()
        features['avg_energy_7d'] = recent['energy_score'].mean()
        features['avg_stress_7d'] = recent['stress_score'].mean()
        features['avg_sleep_7d'] = recent['sleep_quality'].mean()
        features['avg_work_hours_7d'] = recent['work_hours'].mean()
        
        # Variabilidade (indicador de instabilidade emocional)
        features['std_mood_7d'] = recent['mood_score'].std()
        features['std_energy_7d'] = recent['energy_score'].std()
        features['std_stress_7d'] = recent['stress_score'].std()
        
        # Tendências (últimos 14 dias vs últimos 7 dias)
        if len(df) >= 14:
            previous = df.tail(14).head(7)
            features['mood_trend'] = features['avg_mood_7d'] - previous['mood_score'].mean()
            features['energy_trend'] = features['avg_energy_7d'] - previous['energy_score'].mean()
            features['stress_trend'] = features['avg_stress_7d'] - previous['stress_score'].mean()
        else:
            features['mood_trend'] = 0
            features['energy_trend'] = 0
            features['stress_trend'] = 0
        
        # Features de longo prazo (30 dias)
        if len(df) >= 30:
            long_term = df.tail(30)
            features['avg_mood_30d'] = long_term['mood_score'].mean()
            features['avg_stress_30d'] = long_term['stress_score'].mean()
            features['avg_work_hours_30d'] = long_term['work_hours'].mean()
        else:
            features['avg_mood_30d'] = features['avg_mood_7d']
            features['avg_stress_30d'] = features['avg_stress_7d']
            features['avg_work_hours_30d'] = features['avg_work_hours_7d']
        
        # Score composto de risco
        features['risk_composite'] = (
            (10 - features['avg_mood_7d']) * 0.3 +
            (10 - features['avg_energy_7d']) * 0.2 +
            features['avg_stress_7d'] * 0.3 +
            (10 - features['avg_sleep_7d']) * 0.2
        )
        
        # Horas extras consistentes (risco)
        features['overtime_risk'] = max(0, features['avg_work_hours_7d'] - 8) / 4
        
        return pd.DataFrame([features])
    
    def train(self, X: pd.DataFrame, y: np.ndarray) -> Dict[str, float]:
        """
        Treina os modelos de ML
        
        Args:
            X: Features
            y: Labels (0 = sem risco, 1 = risco de burnout)
        
        Returns:
            Métricas de performance
        """
        logger.info("Treinando modelos de predição de burnout...")
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Normalização
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Random Forest
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'
        )
        self.rf_model.fit(X_train_scaled, y_train)
        
        # Gradient Boosting
        self.gb_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.gb_model.fit(X_train_scaled, y_train)
        
        # Avaliação
        rf_pred = self.rf_model.predict(X_test_scaled)
        gb_pred = self.gb_model.predict(X_test_scaled)
        
        # Ensemble (média das probabilidades)
        rf_proba = self.rf_model.predict_proba(X_test_scaled)[:, 1]
        gb_proba = self.gb_model.predict_proba(X_test_scaled)[:, 1]
        ensemble_proba = (rf_proba + gb_proba) / 2
        ensemble_pred = (ensemble_proba >= 0.5).astype(int)
        
        # Métricas
        metrics = {
            'rf_auc': roc_auc_score(y_test, rf_proba),
            'gb_auc': roc_auc_score(y_test, gb_proba),
            'ensemble_auc': roc_auc_score(y_test, ensemble_proba)
        }
        
        self.feature_names = X.columns.tolist()
        self.is_trained = True
        
        logger.info(f"Modelos treinados com sucesso! AUC Ensemble: {metrics['ensemble_auc']:.3f}")
        
        return metrics
    
    def predict(self, records: List[Dict]) -> Tuple[float, str, List[str]]:
        """
        Prediz risco de burnout para um usuário
        
        Args:
            records: Registros de bem-estar do usuário
        
        Returns:
            Tuple (probabilidade, nível_risco, recomendações)
        """
        if not self.is_trained:
            logger.warning("Modelo não treinado, retornando predição padrão")
            return 0.5, "medium", ["Modelo em treinamento"]
        
        # Feature engineering
        X = self.engineer_features(records)
        X_scaled = self.scaler.transform(X)
        
        # Ensemble prediction
        rf_proba = self.rf_model.predict_proba(X_scaled)[0, 1]
        gb_proba = self.gb_model.predict_proba(X_scaled)[0, 1]
        probability = (rf_proba + gb_proba) / 2
        
        # Classificação de risco
        if probability < 0.3:
            risk_level = "low"
        elif probability < 0.6:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        # Recomendações baseadas nas features
        recommendations = self._generate_recommendations(X.iloc[0].to_dict(), probability)
        
        return float(probability), risk_level, recommendations
    
    def _generate_recommendations(self, features: Dict, probability: float) -> List[str]:
        """
        Gera recomendações personalizadas baseadas nas features
        """
        recommendations = []
        
        if features['avg_stress_7d'] > 7:
            recommendations.append("Seu nível de estresse está elevado. Considere técnicas de relaxamento.")
        
        if features['avg_sleep_7d'] < 6:
            recommendations.append("Qualidade do sono abaixo do ideal. Priorize 7-8 horas de sono.")
        
        if features['avg_work_hours_7d'] > 9:
            recommendations.append("Horas de trabalho acima do recomendado. Tente estabelecer limites.")
        
        if features['avg_mood_7d'] < 5:
            recommendations.append("Humor baixo detectado. Considere conversar com um profissional.")
        
        if features['avg_energy_7d'] < 5:
            recommendations.append("Energia baixa. Avalie sua alimentação e atividade física.")
        
        if probability > 0.7:
            recommendations.append("⚠️ Risco alto de burnout. Recomendamos buscar apoio profissional.")
        
        if not recommendations:
            recommendations.append("Continue mantendo seus hábitos saudáveis! 🌟")
        
        return recommendations
    
    def save(self, path: str):
        """Salva modelos treinados"""
        joblib.dump({
            'rf_model': self.rf_model,
            'gb_model': self.gb_model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }, path)
        logger.info(f"Modelos salvos em {path}")
    
    def load(self, path: str):
        """Carrega modelos treinados"""
        data = joblib.load(path)
        self.rf_model = data['rf_model']
        self.gb_model = data['gb_model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.is_trained = data['is_trained']
        logger.info(f"Modelos carregados de {path}")
