"""
Vida & Trabalho - Streamlit Frontend
Global Solution FIAP - Fase 7

Interface interativa para monitoramento de bem-estar e saúde mental no trabalho.
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional, Dict, Any

# Configuration (No .env needed - completely self-contained)
API_BASE_URL = "http://localhost:8000"
st.set_page_config(
    page_title="Vida & Trabalho",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "token" not in st.session_state:
    st.session_state.token = None


def make_api_call(endpoint: str, method: str = "GET", data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Helper function to make API calls"""
    headers = {}
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    timeout = 10
    response = None
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers, timeout=timeout)
        
        if response and response.status_code == 200:
            return response.json()
        elif response:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.RequestException as e:
        st.error(f"Connection error: {str(e)}")
        return None
    
    return None


def login_page():
    """Login page - Demo com dados simulados"""
    st.title("🧠 Vida & Trabalho")
    st.subheader("Bem-estar e Saúde Mental no Trabalho")
    st.markdown("---")
    
    # Demo users (sem necessidade de backend)
    demo_users = {
        "maria@workwell.com": "123456",
        "joao@workwell.com": "123456",
        "ana@workwell.com": "123456",
    }
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🔐 Login Demo")
        st.info("Use qualquer email/senha abaixo para entrar (demo)")
        email = st.text_input("Email", value="maria@workwell.com", key="login_email")
        password = st.text_input("Senha", type="password", value="123456", key="login_password")
        
        if st.button("Entrar", key="login_btn", use_container_width=True):
            if email in demo_users and password == demo_users[email]:
                st.session_state.token = "demo-token-" + email
                st.session_state.user_id = 1
                st.session_state.user_email = email
                st.success("✅ Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("❌ Email ou senha inválidos")
    
    with col2:
        st.markdown("### 📋 Usuários Demo")
        st.info("**Credenciais de demonstração:**")
        for user_email in demo_users.keys():
            st.text(f"📧 {user_email}")
        st.text("🔑 Senha: 123456")


def dashboard_page():
    """Main dashboard page - Com dados simulados"""
    from sample_data import (
        generate_sample_checkins,
        generate_recommendations,
        get_burnout_prediction,
        get_trend_analysis,
        generate_sample_analytics
    )
    
    # Header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        st.markdown(f"👤 {st.session_state.get('user_email', 'User')}")
    with col3:
        if st.button("🚪 Logout", key="logout_btn"):
            st.session_state.token = None
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.rerun()
    
    st.title("📊 Dashboard de Bem-estar")
    st.markdown("*Demonstração com dados simulados - Sem dependências externas*")
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "✅ Check-in Diário",
        "📈 Meu Bem-estar",
        "💡 Recomendações",
        "📊 Análises"
    ])
    
    with tab1:
        st.subheader("✅ Check-in de Hoje")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mood = st.slider("😊 Como está seu humor?", 1, 10, 7)
        
        with col2:
            energy = st.slider("⚡ Seu nível de energia?", 1, 10, 6)
        
        with col3:
            stress = st.slider("😰 Seu nível de estresse?", 1, 10, 4)
        
        notes = st.text_area("📝 Notas (opcional)", placeholder="Como foi seu dia?", height=100)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("✅ Enviar Check-in", use_container_width=True):
                # Análise de risco de burnout
                prediction = get_burnout_prediction(mood, energy, stress)
                
                st.success("✅ Check-in registrado com sucesso!")
                st.markdown("---")
                st.subheader("📊 Análise Instantânea")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Risco de Burnout", f"{prediction['risk_score']:.0%}")
                with col_b:
                    st.metric("Nível", prediction['level'])
                with col_c:
                    st.info(f"💡 {prediction['advice']}")
        
        with col_btn2:
            if st.button("📊 Ver Histórico", use_container_width=True):
                st.info("Histórico de check-ins disponível na aba 'Meu Bem-estar'")
    
    with tab2:
        st.subheader("📈 Seu Bem-estar (Últimos 30 dias)")
        
        # Generate sample data for visualization
        checkins = generate_sample_checkins(30)
        df = pd.DataFrame(checkins)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Gráfico de evolução
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['mood'], mode='lines+markers', name='😊 Humor', line=dict(color='#FF6B6B')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['energy'], mode='lines+markers', name='⚡ Energia', line=dict(color='#4ECDC4')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['stress'], mode='lines+markers', name='😰 Estresse', line=dict(color='#FFE66D')))
        
        fig.update_layout(
            title="📊 Evolução do Bem-estar",
            xaxis_title="Data",
            yaxis_title="Pontuação (1-10)",
            hovermode='x unified',
            height=400,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Análise de tendências
        trend = get_trend_analysis(checkins)
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("😊 Humor Médio", f"{df['mood'].mean():.1f}/10", f"{trend['mood_change']:+.1f}")
        with col2:
            st.metric("⚡ Energia Média", f"{df['energy'].mean():.1f}/10", f"{trend['energy_change']:+.1f}")
        with col3:
            st.metric("😰 Estresse Médio", f"{df['stress'].mean():.1f}/10", f"{trend['stress_change']:+.1f}")
        
        st.markdown("---")
        st.subheader("📈 Tendências")
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            st.info(f"Humor: {trend['mood_trend']}")
        with col_t2:
            st.info(f"Energia: {trend['energy_trend']}")
        with col_t3:
            st.warning(f"Estresse: {trend['stress_trend']}")
    
    with tab3:
        st.subheader("💡 Recomendações Personalizadas")
        st.markdown("*Baseadas em análise de bem-estar e Machine Learning*")
        
        recommendations = generate_recommendations()
        
        for i, rec in enumerate(recommendations, 1):
            with st.container():
                col_icon, col_content = st.columns([0.5, 3])
                with col_icon:
                    if rec['impact'] == 'Muito Alto':
                        st.markdown("🔴")
                    elif rec['impact'] == 'Alto':
                        st.markdown("🟠")
                    else:
                        st.markdown("🟡")
                with col_content:
                    st.markdown(f"**{i}. {rec['title']}**")
                    st.markdown(f"_{rec['description']}_")
                    st.caption(f"📂 {rec['category']} | 💪 Impacto: {rec['impact']}")
    
    with tab4:
        st.subheader("📊 Análises Avançadas")
        st.markdown("*Integração: Análise de Dados + Machine Learning + Python*")
        
        # Get analytics data
        analytics = generate_sample_analytics()
        
        # Overview metrics
        st.markdown("### 📈 Visão Geral Organizacional")
        col_a1, col_a2, col_a3, col_a4 = st.columns(4)
        with col_a1:
            st.metric("👥 Usuários Ativos", analytics['total_users'])
        with col_a2:
            st.metric("😊 Humor Médio", f"{analytics['avg_mood']:.1f}/10")
        with col_a3:
            st.metric("🔴 Risco de Burnout", f"{analytics['burnout_risk']:.0%}")
        with col_a4:
            st.metric("📊 Engajamento", f"{analytics['engagement_rate']:.0%}")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Distribuição de Humor")
            checkins = generate_sample_checkins(30)
            mood_dist = [c['mood'] for c in checkins]
            fig_hist = px.histogram(
                x=mood_dist,
                nbins=10,
                title="Distribuição de Humor (Últimos 30 dias)",
                labels={"x": "Pontuação", "count": "Frequência"},
                color_discrete_sequence=['#FF6B6B']
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        
        with col2:
            st.markdown("### 🏢 Bem-estar por Departamento")
            dept_data = pd.DataFrame([
                {'Departamento': k, 'Humor Médio': v['avg_mood'], 'Risco': v['risk']}
                for k, v in analytics['departments'].items()
            ])
            fig_dept = px.bar(
                dept_data,
                x='Departamento',
                y='Humor Médio',
                color='Risco',
                title="Bem-estar por Departamento",
                color_continuous_scale='RdYlGn'
            )
            st.plotly_chart(fig_dept, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🎯 Fatores de Impacto no Bem-estar")
        correlation_data = pd.DataFrame({
            'Fator': ['Sono', 'Exercício', 'Socialização', 'Trabalho Remoto', 'Pausas'],
            'Correlação': [0.85, 0.72, 0.68, 0.55, 0.62]
        })
        fig_corr = px.bar(
            correlation_data,
            x='Fator',
            y='Correlação',
            title="Fatores que Afetam Bem-estar (Correlação)",
            color='Correlação',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_corr, use_container_width=True)


def main():
    """Main app logic"""
    if st.session_state.token is None:
        login_page()
    else:
        dashboard_page()


if __name__ == "__main__":
    main()
