# FIAP - Faculdade de Informática e Administração Paulista 

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Nome do projeto

🧠 Vida & Trabalho

https://www.youtube.com/watch?v=bEh9bC6_Zmg
https://github.com/lorenzo-leuck/ia-fase-7-gs

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/lorenzo-leuck/">Lorenzo Leuck</a>


## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/leonardoorabona/">Leonardo Orabona</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi</a>


## 📜 Descrição


**Plataforma inteligente de monitoramento de bem-estar e saúde mental no trabalho**

> Como a tecnologia pode tornar o trabalho mais humano, inclusivo e sustentável no futuro?

---

## 🎯 O Problema

- 77% dos profissionais já experimentaram burnout
- Falta de visibilidade sobre sinais precoces de problemas
- Abordagem reativa (ações apenas após crises)
- Soluções genéricas que não atendem necessidades individuais

## 💡 A Solução

**Vida & Trabalho** é uma plataforma que combina:
- ✅ Monitoramento contínuo de bem-estar
- ✅ Predição de riscos com Machine Learning
- ✅ Recomendações personalizadas via IA
- ✅ Análises estatísticas avançadas
- ✅ Segurança e privacidade total

---

## 🚀 Início Rápido

### Opção 1: Script Automático (Recomendado)
```bash
./run.sh
```

### Opção 2: Manual
```bash
# Setup único
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd streamlit_app
streamlit run app.py
```

### 🔐 Credenciais Demo (Sem Configuração!)
```
📧 maria@workwell.com / 🔑 123456
📧 joao@workwell.com / 🔑 123456
📧 ana@workwell.com / 🔑 123456
```

---

## ✨ Funcionalidades

### ✅ Check-in Diário
Registre seu bem-estar em 3 dimensões:
- 😊 **Humor** (1-10)
- ⚡ **Energia** (1-10)
- 😰 **Estresse** (1-10)

Receba análise instantânea de risco de burnout e recomendações personalizadas.

### ✅ Dashboard de Bem-estar
- Gráficos de evolução (últimos 30 dias)
- Análise de tendências
- Métricas consolidadas
- Visualizações interativas

### ✅ Recomendações Inteligentes
6 recomendações baseadas em Machine Learning:
1. Pausas Regulares
2. Meditação Guiada
3. Exercício Físico
4. Hidratação
5. Sono Adequado
6. Conexão Social

### ✅ Análises Avançadas
- Visão geral organizacional
- Distribuição de humor
- Bem-estar por departamento
- Fatores de impacto (correlações)
- Previsões de tendências

---

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────┐
│  Frontend (Streamlit)                    │
│  - Dashboard interativo                  │
│  - Check-in de bem-estar                 │
│  - Recomendações personalizadas          │
│  - Análises avançadas                    │
│  🌐 http://localhost:8501                │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│  Backend (FastAPI)                       │
│  - API REST segura                       │
│  - Autenticação JWT                      │
│  - Processamento de dados                │
│  - Modelos ML integrados                 │
│  🌐 http://localhost:8000                │
│  📚 http://localhost:8000/docs           │
└──────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────┐
│  Database (SQLite)                       │
│  - Sem dependências externas             │
│  - Arquivo local: workwell.db            │
│  - SQLAlchemy ORM                        │
└──────────────────────────────────────────┘
```

---

## 🎓 Integração das 9 Disciplinas

### 1️⃣ AICSS (AI, Cognitive & Semantic Systems)
**Agente inteligente de recomendações**
- Análise semântica de bem-estar
- Recomendações contextualizadas
- Suporte emocional automatizado

### 2️⃣ Cybersecurity
**Segurança em primeiro lugar**
- Autenticação JWT com tokens seguros
- Criptografia de dados sensíveis
- Rate limiting contra ataques
- Headers de segurança (HSTS, X-Frame-Options, X-XSS-Protection)
- CORS configurado

### 3️⃣ Machine Learning
**Predição de burnout**
- Modelo de classificação baseado em heurística
- Clustering para identificar perfis de risco
- Feature engineering com dados temporais
- Análise de correlações

### 4️⃣ Redes Neurais
**Análise de séries temporais**
- LSTM-like para padrões de humor
- Detecção de tendências
- Ensemble de modelos
- Previsão de evolução

### 5️⃣ Linguagem R
**Análises estatísticas avançadas (em Python)**
- Testes de hipótese (scipy.stats)
- Correlações entre fatores
- Modelagem estatística
- Análise de outliers (IQR)

### 6️⃣ Python
**Backend e processamento**
- FastAPI para API REST
- Pandas/NumPy para análises
- scikit-learn para ML
- Automação de scripts
- Analytics com scipy

### 7️⃣ Computação em Nuvem
**Execução simplificada**
- Script run.sh para orquestração
- Ambientes virtuais Python
- Pronto para deploy em cloud
- Sem dependências de infra

### 8️⃣ Banco de Dados
**Dados estruturados e seguros**
- SQLite local (sem dependências)
- SQLAlchemy ORM
- Modelos relacionais normalizados
- Índices para performance

### 9️⃣ Formação Social
**Inclusão, ética e sustentabilidade**
- Interface acessível
- Transparência algorítmica
- Foco em bem-estar humano
- Sem viés discriminatório

---

## 🛠️ Tecnologias

### Frontend
- **Streamlit** - Interface interativa
- **Plotly** - Visualizações
- **Pandas/NumPy** - Processamento de dados

### Backend
- **FastAPI** - API REST
- **SQLAlchemy** - ORM
- **Pydantic** - Validação
- **scikit-learn** - Machine Learning

### Database
- **SQLite** - Banco local (sem dependências!)

### Execução
- **Python 3.11+** - Linguagem
- **run.sh** - Script de inicialização automática
- **requirements.txt** - Dependências consolidadas (raiz do projeto)
- **scipy** - Análises estatísticas
- **joblib** - Serialização de modelos

---


## 📁 Estrutura do Projeto

```
ia-fase-7-gs/
├── run.sh                    # Script para executar tudo
├── requirements.txt          # Dependências consolidadas
├── .env.example              # Exemplo de configuração
├── README.md                 # Este arquivo
│
├── backend/
│   ├── app/
│   │   ├── api/              # Endpoints
│   │   ├── models/           # Modelos de dados
│   │   ├── ml/               # Modelos ML
│   │   └── core/             # Config e DB
│   └── main.py
│
├── streamlit_app/
│   ├── app.py                # Interface principal
│   ├── sample_data.py        # Dados simulados + ML
│   └── .streamlit/
│       └── config.toml
│
├── analytics/
│   └── organizational_analysis.py  # Análises estatísticas (Python + scipy)
│
└── database/                 # Scripts de inicialização
```

---

## 🧪 Como Testar

### 1. Login
```
Email: maria@workwell.com
Senha: 123456
```

### 2. Check-in Diário
- Mude os sliders (humor, energia, estresse)
- Clique em "Enviar Check-in"
- Veja análise de burnout

### 3. Dashboard
- Veja gráficos de evolução
- Analise tendências
- Veja métricas

### 4. Recomendações
- Veja 6 recomendações personalizadas
- Categorizadas por impacto

### 5. Análises
- Veja visão organizacional
- Distribuição de humor
- Bem-estar por departamento

### 6. API
- Acesse http://localhost:8000/docs
- Teste os endpoints

---

## 📈 Métricas Esperadas

- ✅ Tempo de resposta: < 200ms
- ✅ Disponibilidade: 99.9%
- ✅ Taxa de erro: < 0.1%
- ✅ Engajamento: 85%+
- ✅ Precisão de predição: 85%+

---

## 🎯 Resultados Esperados

- ✅ Redução de 30% nos casos de burnout
- ✅ Aumento de 40% no engajamento
- ✅ Identificação precoce de 85% dos casos de risco
- ✅ ROI positivo em 6 meses
- ✅ NPS > 70

---

## 🔗 Links Úteis

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend (FastAPI)**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc

---


## 🎬 Demonstração Prática

### O que Mostrar (5-10 minutos)
1. **Login** - Credenciais demo
2. **Check-in** - Registrar bem-estar
3. **Análise** - Risco de burnout
4. **Recomendações** - Personalizadas
5. **Dashboard** - Gráficos e tendências
6. **Análises** - Visão organizacional

---

## 📦 Dependências

Todas as dependências estão consolidadas em `requirements.txt` na raiz do projeto:

```bash
pip install -r requirements.txt
```

**Principais pacotes:**
- FastAPI + Uvicorn (Backend)
- Streamlit + Plotly (Frontend)
- scikit-learn + pandas + numpy + scipy (Data Science)
- SQLAlchemy (ORM)
- python-jose + passlib + cryptography (Segurança)

---

## 🎓 Conclusão

**Vida & Trabalho** demonstra que a tecnologia pode tornar o trabalho mais humano, inclusivo e sustentável, integrando conhecimentos de todas as disciplinas do curso em uma solução prática e funcional.

**O trabalho do futuro será tão humano quanto as ideias que o constroem.** 🚀

