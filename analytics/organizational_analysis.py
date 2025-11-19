#!/usr/bin/env python3
"""
Vida & Trabalho - Análise Estatística Organizacional
Integração: Python + Estatística + Data Science

Este script realiza análises estatísticas avançadas sobre dados de bem-estar
organizacional, incluindo:
- Estatísticas descritivas
- Testes de hipótese
- Análise de correlação
- Modelagem preditiva
- Visualizações científicas
"""

import json
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from scipy import stats
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import base64
from io import BytesIO

warnings.filterwarnings('ignore')
sns.set_style("whitegrid")


def detect_outliers(x):
    """Detecta outliers usando IQR"""
    q1 = np.percentile(x, 25)
    q3 = np.percentile(x, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return (x < lower) | (x > upper)


def generate_visualizations(df):
    """Gera visualizações e salva como imagens PNG"""
    import os
    os.makedirs('analytics/output', exist_ok=True)
    visualizations = {}
    
    # 1. Evolução de Humor
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['date'], df['mood_score'], marker='o', linewidth=2, color='#2ecc71')
    ax.set_title('Evolução de Humor (30 dias)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Data')
    ax.set_ylabel('Humor (1-10)')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path = 'analytics/output/01_mood_evolution.png'
    plt.savefig(path, dpi=100, bbox_inches='tight')
    visualizations['mood_evolution'] = path
    plt.close()
    
    # 2. Distribuição de Estresse
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(df['stress_score'], bins=10, color='#e74c3c', alpha=0.7, edgecolor='black')
    ax.set_title('Distribuição de Estresse', fontsize=14, fontweight='bold')
    ax.set_xlabel('Nível de Estresse')
    ax.set_ylabel('Frequência')
    plt.tight_layout()
    path = 'analytics/output/02_stress_distribution.png'
    plt.savefig(path, dpi=100, bbox_inches='tight')
    visualizations['stress_distribution'] = path
    plt.close()
    
    # 3. Correlação (Heatmap)
    fig, ax = plt.subplots(figsize=(8, 6))
    numeric_cols = ['mood_score', 'energy_score', 'stress_score', 'sleep_quality', 'work_hours']
    corr = df[numeric_cols].corr()
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, ax=ax, cbar_kws={'label': 'Correlação'})
    ax.set_title('Matriz de Correlação', fontsize=14, fontweight='bold')
    plt.tight_layout()
    path = 'analytics/output/03_correlation_heatmap.png'
    plt.savefig(path, dpi=100, bbox_inches='tight')
    visualizations['correlation_heatmap'] = path
    plt.close()
    
    # 4. Scatter: Sono vs Estresse
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df['sleep_quality'], df['stress_score'], s=100, alpha=0.6, color='#3498db')
    ax.set_title('Relação: Qualidade do Sono vs Estresse', fontsize=14, fontweight='bold')
    ax.set_xlabel('Qualidade do Sono')
    ax.set_ylabel('Nível de Estresse')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path = 'analytics/output/04_sleep_stress_scatter.png'
    plt.savefig(path, dpi=100, bbox_inches='tight')
    visualizations['sleep_stress_scatter'] = path
    plt.close()
    
    return visualizations


def main():
    """Função principal de análise"""
    
    if len(sys.argv) < 2:
        raise ValueError("Erro: Arquivo de dados não fornecido")
    
    data_file = sys.argv[1]
    
    # Carrega dados JSON
    with open(data_file, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    df['date'] = pd.to_datetime(df['date'])
    
    # ========================================================================
    # 1. ESTATÍSTICAS DESCRITIVAS
    # ========================================================================
    
    summary_stats = {
        'total_records': len(df),
        'unique_users': df['user_hash'].nunique() if 'user_hash' in df.columns else 0,
        
        # Médias
        'avg_mood': round(df['mood_score'].mean(), 2),
        'avg_energy': round(df['energy_score'].mean(), 2),
        'avg_stress': round(df['stress_score'].mean(), 2),
        'avg_sleep': round(df['sleep_quality'].mean(), 2),
        'avg_work_hours': round(df['work_hours'].mean(), 2),
        
        # Desvios padrão
        'sd_mood': round(df['mood_score'].std(), 2),
        'sd_stress': round(df['stress_score'].std(), 2),
        
        # Percentis
        'p25_stress': float(np.percentile(df['stress_score'], 25)),
        'p75_stress': float(np.percentile(df['stress_score'], 75)),
        
        # Indicadores de risco
        'high_stress_pct': round(sum(df['stress_score'] >= 8) / len(df) * 100, 1),
        'low_mood_pct': round(sum(df['mood_score'] <= 4) / len(df) * 100, 1),
        'overtime_pct': round(sum(df['work_hours'] > 9) / len(df) * 100, 1)
    }
    
    # ========================================================================
    # 2. ANÁLISE DE CORRELAÇÃO
    # ========================================================================
    
    numeric_vars = df[['mood_score', 'energy_score', 'stress_score', 'sleep_quality', 'work_hours']]
    cor_matrix = numeric_vars.corr()
    
    correlations = cor_matrix.to_dict()
    
    # ========================================================================
    # 3. TESTES DE HIPÓTESE
    # ========================================================================
    
    hypothesis_tests = {}
    
    overtime_group = df[df['work_hours'] > 9]['stress_score']
    normal_group = df[df['work_hours'] <= 9]['stress_score']
    
    if len(overtime_group) > 0 and len(normal_group) > 0:
        t_stat, p_value = stats.ttest_ind(overtime_group, normal_group)
        
        hypothesis_tests['overtime_stress'] = {
            'hypothesis': 'Horas extras aumentam o estresse',
            'p_value': round(p_value, 4),
            'significant': bool(p_value < 0.05),
            'mean_overtime': round(overtime_group.mean(), 2),
            'mean_normal': round(normal_group.mean(), 2)
        }
    
    # ========================================================================
    # 4. ANÁLISE DE TENDÊNCIAS TEMPORAIS
    # ========================================================================
    
    df['week'] = df['date'].dt.to_period('W')
    weekly_trends = df.groupby('week').agg({
        'mood_score': 'mean',
        'stress_score': 'mean',
        'energy_score': 'mean'
    }).round(2)
    
    trends = {
        'mood_trend': 0,
        'stress_trend': 0,
        'energy_trend': 0,
        'trend_direction': 'insufficient_data'
    }
    
    if len(weekly_trends) >= 8:
        recent_weeks = weekly_trends.tail(4)
        previous_weeks = weekly_trends.iloc[-8:-4]
        
        trends = {
            'mood_trend': round(recent_weeks['mood_score'].mean() - previous_weeks['mood_score'].mean(), 2),
            'stress_trend': round(recent_weeks['stress_score'].mean() - previous_weeks['stress_score'].mean(), 2),
            'energy_trend': round(recent_weeks['energy_score'].mean() - previous_weeks['energy_score'].mean(), 2),
            'trend_direction': 'improving' if recent_weeks['mood_score'].mean() > previous_weeks['mood_score'].mean() else 'declining'
        }
    
    # ========================================================================
    # 5. MODELAGEM PREDITIVA (Regressão Linear)
    # ========================================================================
    
    predictive_model = {}
    
    if len(df) >= 30:
        X = df[['energy_score', 'stress_score', 'sleep_quality', 'work_hours']].dropna()
        y = df.loc[X.index, 'mood_score']
        
        if len(X) > 0:
            model = LinearRegression()
            model.fit(X, y)
            r_squared = model.score(X, y)
            
            predictive_model = {
                'r_squared': round(r_squared, 3),
                'adj_r_squared': round(1 - (1 - r_squared) * (len(X) - 1) / (len(X) - X.shape[1] - 1), 3),
                'interpretation': 'Modelo explica bem a variação no humor' if r_squared > 0.5 else 'Outros fatores não medidos influenciam o humor'
            }
    else:
        predictive_model = {'message': 'Dados insuficientes para modelagem'}
    
    # ========================================================================
    # 6. IDENTIFICAÇÃO DE OUTLIERS
    # ========================================================================
    
    stress_outliers = detect_outliers(df['stress_score'].values)
    work_hours_outliers = detect_outliers(df['work_hours'].values)
    
    outliers = {
        'n_stress_outliers': int(sum(stress_outliers)),
        'n_work_hours_outliers': int(sum(work_hours_outliers))
    }
    
    # ========================================================================
    # 7. RECOMENDAÇÕES BASEADAS EM DADOS
    # ========================================================================
    
    recommendations = []
    
    if summary_stats['high_stress_pct'] > 30:
        recommendations.append('⚠️ Mais de 30% dos registros indicam estresse alto. Considere programas de gestão de estresse.')
    
    if summary_stats['overtime_pct'] > 40:
        recommendations.append('⚠️ Mais de 40% dos registros indicam horas extras. Revise políticas de carga de trabalho.')
    
    if summary_stats['avg_sleep'] < 6.5:
        recommendations.append('⚠️ Qualidade de sono abaixo do ideal. Promova educação sobre higiene do sono.')
    
    if trends['trend_direction'] == 'declining':
        recommendations.append('📉 Tendência de declínio detectada. Intervenções preventivas são recomendadas.')
    
    if len(recommendations) == 0:
        recommendations.append('✅ Indicadores organizacionais dentro de parâmetros saudáveis.')
    
    # ========================================================================
    # 8. VISUALIZAÇÕES
    # ========================================================================
    
    visualizations = generate_visualizations(df)
    
    # ========================================================================
    # 9. OUTPUT JSON
    # ========================================================================
    
    result = {
        'summary': summary_stats,
        'correlations': correlations,
        'hypothesis_tests': hypothesis_tests,
        'trends': trends,
        'predictive_model': predictive_model,
        'outliers': outliers,
        'recommendations': recommendations,
        'visualizations': visualizations,
        'metadata': {
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'python_version': '3.11+',
            'n_records_analyzed': len(df)
        }
    }
    
    # Converte para JSON e imprime
    print(json.dumps(result, indent=None))


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        error_result = {
            'error': True,
            'message': str(e)
        }
        print(json.dumps(error_result))
        sys.exit(1)
