#!/bin/bash

# Vida & Trabalho - Script para executar Backend e Frontend
# Global Solution FIAP - Fase 7

set -e

echo "🧠 Vida & Trabalho - Iniciando aplicação..."
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para limpar ao sair
cleanup() {
    echo ""
    echo -e "${YELLOW}Encerrando aplicação...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 não encontrado. Por favor, instale Python 3.11+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python encontrado: $(python3 --version)${NC}"
echo ""

# ============================================================================
# BACKEND
# ============================================================================

echo -e "${YELLOW}📦 Configurando Backend...${NC}"

if [ ! -d "backend/venv" ]; then
    echo "Criando ambiente virtual..."
    cd backend
    python3 -m venv venv
    cd ..
fi

echo "Ativando ambiente virtual e instalando dependências..."
source backend/venv/bin/activate
pip install -q -r requirements.txt
deactivate

echo -e "${GREEN}✅ Backend pronto${NC}"
echo ""

# ============================================================================
# FRONTEND
# ============================================================================

echo -e "${YELLOW}📦 Configurando Frontend...${NC}"

if [ ! -d "streamlit_app/venv" ]; then
    echo "Criando ambiente virtual..."
    cd streamlit_app
    python3 -m venv venv
    cd ..
fi

echo "Ativando ambiente virtual e instalando dependências..."
source streamlit_app/venv/bin/activate
pip install -q -r requirements.txt
deactivate

echo -e "${GREEN}✅ Frontend pronto${NC}"
echo ""

# ============================================================================
# EXECUTAR
# ============================================================================

echo -e "${GREEN}🚀 Iniciando aplicação...${NC}"
echo ""

# Iniciar Backend em background
echo -e "${YELLOW}Iniciando Backend (FastAPI)...${NC}"
source backend/venv/bin/activate
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..
deactivate

sleep 2

# Iniciar Frontend em background
echo -e "${YELLOW}Iniciando Frontend (Streamlit)...${NC}"
source streamlit_app/venv/bin/activate
cd streamlit_app
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 &
FRONTEND_PID=$!
cd ..
deactivate

echo ""
echo -e "${GREEN}✅ Aplicação iniciada com sucesso!${NC}"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}🎉 Vida & Trabalho está rodando!${NC}"
echo ""
echo "📊 Frontend (Streamlit):  http://localhost:8501"
echo "⚙️  Backend (FastAPI):    http://localhost:8000"
echo "📚 API Docs (Swagger):   http://localhost:8000/docs"
echo ""
echo "🔐 Credenciais Demo:"
echo "   📧 maria@workwell.com / 🔑 123456"
echo "   📧 joao@workwell.com / 🔑 123456"
echo "   📧 ana@workwell.com / 🔑 123456"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "Pressione Ctrl+C para encerrar..."
echo ""

# Aguardar processos
wait $BACKEND_PID $FRONTEND_PID
