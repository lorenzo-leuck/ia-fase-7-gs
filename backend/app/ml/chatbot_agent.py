"""
Agente Conversacional Inteligente (Chatbot)
Integração: AICSS + NLP + Transformers + Python

Usa modelos de linguagem para:
- Análise de sentimento
- Suporte emocional
- Recomendações personalizadas
- Processamento de linguagem natural
"""

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from typing import Dict, List, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class WellbeingChatbot:
    """
    Chatbot inteligente para suporte de bem-estar
    
    Funcionalidades:
    - Análise de sentimento em tempo real
    - Respostas empáticas baseadas em contexto
    - Detecção de sinais de alerta
    - Recomendações personalizadas
    """
    
    def __init__(self):
        """
        Inicializa modelos de NLP
        
        Modelos usados:
        - Sentiment Analysis: distilbert-base-uncased-finetuned-sst-2-english
        - Para produção, considere modelos em português como neuralmind/bert-base-portuguese-cased
        """
        try:
            # Sentiment analyzer
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info("Chatbot NLP models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading NLP models: {e}")
            self.sentiment_analyzer = None
        
        # Respostas pré-definidas por categoria
        self.responses = {
            'stress': [
                "Entendo que você está se sentindo estressado. Que tal fazer uma pausa de 5 minutos para respirar profundamente?",
                "O estresse é comum, mas podemos trabalhar nisso juntos. Já tentou técnicas de mindfulness?",
                "Percebo que as coisas estão pesadas. Lembre-se: você não precisa resolver tudo hoje."
            ],
            'tired': [
                "Parece que você está cansado. Quando foi a última vez que tirou um tempo para descansar?",
                "Energia baixa pode ser sinal de que seu corpo precisa de cuidado. Como está seu sono?",
                "Que tal uma pausa? Às vezes, 10 minutos longe da tela fazem maravilhas."
            ],
            'anxious': [
                "Ansiedade é desafiadora. Vamos tentar focar no presente: o que você pode controlar agora?",
                "Entendo sua preocupação. Que tal escrever o que está te deixando ansioso?",
                "Respire comigo: inspire por 4 segundos, segure por 4, expire por 4. Repita 3 vezes."
            ],
            'sad': [
                "Sinto muito que você esteja se sentindo assim. Quer conversar sobre o que está acontecendo?",
                "Dias difíceis fazem parte, mas você não está sozinho. Como posso ajudar?",
                "Está tudo bem não estar bem. Que tal fazer algo que normalmente te traz alegria?"
            ],
            'positive': [
                "Que ótimo ouvir isso! Continue assim! 🌟",
                "Maravilha! Momentos positivos merecem ser celebrados!",
                "Isso é excelente! Você está no caminho certo!"
            ],
            'alert': [
                "⚠️ Percebo que você pode estar precisando de ajuda profissional. Considere conversar com um psicólogo.",
                "Seus sinais indicam que pode ser importante buscar apoio especializado. Posso te ajudar a encontrar recursos?",
                "Sua saúde mental é prioridade. Recomendo fortemente conversar com um profissional de saúde."
            ]
        }
        
        # Palavras-chave para detecção de categorias
        self.keywords = {
            'stress': ['estressado', 'pressão', 'sobrecarregado', 'overwhelmed', 'stress', 'pressure'],
            'tired': ['cansado', 'exausto', 'sem energia', 'tired', 'exhausted', 'fatigue'],
            'anxious': ['ansioso', 'preocupado', 'nervoso', 'anxious', 'worried', 'nervous'],
            'sad': ['triste', 'deprimido', 'down', 'sad', 'depressed', 'unhappy'],
            'alert': ['suicídio', 'morrer', 'acabar com tudo', 'suicide', 'kill myself', 'end it all']
        }
    
    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Analisa sentimento do texto
        
        Args:
            text: Texto do usuário
        
        Returns:
            Tuple (label, score) - ex: ('POSITIVE', 0.95)
        """
        if not self.sentiment_analyzer:
            return 'NEUTRAL', 0.5
        
        try:
            result = self.sentiment_analyzer(text[:512])[0]  # Limita a 512 tokens
            return result['label'], result['score']
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return 'NEUTRAL', 0.5
    
    def detect_category(self, text: str) -> str:
        """
        Detecta categoria da mensagem baseada em palavras-chave
        
        Args:
            text: Texto do usuário
        
        Returns:
            Categoria detectada
        """
        text_lower = text.lower()
        
        # Prioridade para alertas críticos
        for keyword in self.keywords['alert']:
            if keyword in text_lower:
                return 'alert'
        
        # Outras categorias
        for category, keywords in self.keywords.items():
            if category == 'alert':
                continue
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        # Se não detectou categoria específica, usa sentimento
        sentiment, score = self.analyze_sentiment(text)
        if sentiment == 'POSITIVE' and score > 0.7:
            return 'positive'
        elif sentiment == 'NEGATIVE' and score > 0.7:
            return 'sad'
        
        return 'general'
    
    def generate_response(self, user_message: str, user_context: Dict = None) -> Dict:
        """
        Gera resposta contextualizada para o usuário
        
        Args:
            user_message: Mensagem do usuário
            user_context: Contexto adicional (histórico, métricas, etc)
        
        Returns:
            Dict com resposta e metadados
        """
        # Análise de sentimento
        sentiment, sentiment_score = self.analyze_sentiment(user_message)
        
        # Detecta categoria
        category = self.detect_category(user_message)
        
        # Seleciona resposta apropriada
        if category in self.responses:
            import random
            response_text = random.choice(self.responses[category])
        else:
            response_text = "Entendo. Como posso ajudar você hoje?"
        
        # Adiciona contexto se disponível
        if user_context:
            response_text = self._add_context_to_response(
                response_text, 
                category, 
                user_context
            )
        
        return {
            'response': response_text,
            'sentiment': sentiment,
            'sentiment_score': float(sentiment_score),
            'category': category,
            'requires_attention': category == 'alert'
        }
    
    def _add_context_to_response(self, base_response: str, category: str, context: Dict) -> str:
        """
        Adiciona informações contextuais à resposta
        
        Args:
            base_response: Resposta base
            category: Categoria detectada
            context: Contexto do usuário (métricas recentes, etc)
        
        Returns:
            Resposta enriquecida
        """
        # Exemplo de contextualização
        if 'recent_stress' in context and context['recent_stress'] > 7:
            base_response += "\n\nNotei que seu nível de estresse tem estado alto nos últimos dias."
        
        if 'sleep_quality' in context and context['sleep_quality'] < 5:
            base_response += "\n\nSua qualidade de sono também parece estar comprometida. Isso pode estar afetando como você se sente."
        
        if 'burnout_risk' in context and context['burnout_risk'] > 0.7:
            base_response += "\n\n⚠️ Seus indicadores sugerem risco elevado de burnout. Recomendo conversar com seu gestor ou RH."
        
        return base_response
    
    def extract_metrics_from_text(self, text: str) -> Dict:
        """
        Extrai métricas mencionadas no texto
        
        Args:
            text: Texto do usuário
        
        Returns:
            Dict com métricas extraídas
        """
        metrics = {}
        
        # Padrões para extração
        patterns = {
            'hours_worked': r'trabalhei (\d+) horas?|worked (\d+) hours?',
            'sleep_hours': r'dormi (\d+) horas?|slept (\d+) hours?',
        }
        
        for metric, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                value = match.group(1) or match.group(2)
                metrics[metric] = int(value)
        
        return metrics
    
    def get_wellness_tips(self, category: str = 'general') -> List[str]:
        """
        Retorna dicas de bem-estar baseadas na categoria
        
        Args:
            category: Categoria de bem-estar
        
        Returns:
            Lista de dicas
        """
        tips = {
            'stress': [
                "🧘 Pratique 5 minutos de meditação",
                "🚶 Faça uma caminhada de 10 minutos",
                "📝 Escreva 3 coisas pelas quais é grato",
                "🎵 Ouça música relaxante",
                "💬 Converse com alguém de confiança"
            ],
            'tired': [
                "😴 Priorize 7-8 horas de sono",
                "💧 Mantenha-se hidratado",
                "🥗 Alimente-se de forma balanceada",
                "☕ Evite cafeína após 15h",
                "📱 Desligue telas 1h antes de dormir"
            ],
            'anxious': [
                "🫁 Pratique respiração 4-7-8",
                "📝 Liste suas preocupações e priorize",
                "🎯 Foque no que você pode controlar",
                "🧘 Experimente mindfulness",
                "💪 Exercícios físicos ajudam a reduzir ansiedade"
            ],
            'general': [
                "🌟 Estabeleça limites saudáveis",
                "⏰ Faça pausas regulares",
                "🎯 Defina metas realistas",
                "💬 Mantenha comunicação aberta",
                "🎨 Reserve tempo para hobbies"
            ]
        }
        
        return tips.get(category, tips['general'])
