"""
Carregador de Modelos ML
Gerencia carregamento e cache de modelos treinados
"""

import os
import logging
from app.ml.burnout_predictor import BurnoutPredictor
from app.ml.lstm_analyzer import LSTMWellbeingAnalyzer
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global model instances (singleton pattern)
burnout_predictor = None
lstm_analyzer = None


def load_models():
    """
    Carrega todos os modelos ML na inicialização da aplicação
    """
    global burnout_predictor, lstm_analyzer
    
    try:
        # Burnout Predictor (ML)
        burnout_predictor = BurnoutPredictor()
        model_path = os.path.join(settings.MODEL_PATH, "burnout_model.pkl")
        if os.path.exists(model_path):
            burnout_predictor.load(model_path)
            logger.info("✅ Burnout predictor loaded")
        else:
            logger.warning("⚠️ Burnout model not found, will train on first use")
        
        # LSTM Analyzer (Neural Networks)
        lstm_analyzer = LSTMWellbeingAnalyzer()
        lstm_path = settings.MODEL_PATH
        if os.path.exists(os.path.join(lstm_path, "lstm_model.h5")):
            lstm_analyzer.load(lstm_path)
            logger.info("✅ LSTM analyzer loaded")
        else:
            logger.warning("⚠️ LSTM model not found, will train on first use")
        
    except Exception as e:
        logger.error(f"❌ Error loading models: {e}")


def get_burnout_predictor() -> BurnoutPredictor:
    """Retorna instância do preditor de burnout"""
    return burnout_predictor


def get_lstm_analyzer() -> LSTMWellbeingAnalyzer:
    """Retorna instância do analisador LSTM"""
    return lstm_analyzer
