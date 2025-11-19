-- WorkWell AI Database Schema
-- Integração: Banco de Dados + PostgreSQL
-- 
-- Este script cria a estrutura do banco de dados para a plataforma WorkWell AI
-- Inclui: tabelas, índices, constraints, triggers e procedures

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Para busca textual eficiente

-- ============================================================================
-- TABLES
-- ============================================================================

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT valid_role CHECK (role IN ('user', 'manager', 'admin'))
);

-- Tabela de Registros de Bem-Estar
CREATE TABLE IF NOT EXISTS wellbeing_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Métricas de bem-estar (1-10)
    mood_score INTEGER NOT NULL CHECK (mood_score >= 1 AND mood_score <= 10),
    energy_score INTEGER NOT NULL CHECK (energy_score >= 1 AND energy_score <= 10),
    stress_score INTEGER NOT NULL CHECK (stress_score >= 1 AND stress_score <= 10),
    sleep_quality INTEGER NOT NULL CHECK (sleep_quality >= 1 AND sleep_quality <= 10),
    
    -- Contexto de trabalho
    work_hours DECIMAL(4,2) NOT NULL CHECK (work_hours >= 0 AND work_hours <= 24),
    
    -- Notas (criptografadas)
    notes TEXT,
    
    -- Análises computadas
    sentiment_score DECIMAL(3,2), -- -1 a 1
    burnout_risk_score DECIMAL(3,2), -- 0 a 1
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Sessões de Chat (para histórico do chatbot)
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    sentiment VARCHAR(50),
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de Alertas (para casos críticos)
CREATE TABLE IF NOT EXISTS alerts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_severity CHECK (severity IN ('low', 'medium', 'high', 'critical'))
);

-- ============================================================================
-- INDEXES (Performance)
-- ============================================================================

-- Índices para queries frequentes
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE INDEX IF NOT EXISTS idx_wellbeing_user_id ON wellbeing_records(user_id);
CREATE INDEX IF NOT EXISTS idx_wellbeing_created_at ON wellbeing_records(created_at);
CREATE INDEX IF NOT EXISTS idx_wellbeing_user_date ON wellbeing_records(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_chat_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_created_at ON chat_sessions(created_at);

CREATE INDEX IF NOT EXISTS idx_alerts_user_id ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_unresolved ON alerts(is_resolved) WHERE is_resolved = FALSE;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger para criar alerta automático em caso de risco alto
CREATE OR REPLACE FUNCTION check_burnout_risk()
RETURNS TRIGGER AS $$
BEGIN
    -- Se risco de burnout > 0.7, cria alerta
    IF NEW.burnout_risk_score > 0.7 THEN
        INSERT INTO alerts (user_id, alert_type, severity, message)
        VALUES (
            NEW.user_id,
            'burnout_risk',
            'high',
            'Risco elevado de burnout detectado. Recomenda-se intervenção.'
        );
    END IF;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER trigger_burnout_alert
    AFTER INSERT OR UPDATE OF burnout_risk_score ON wellbeing_records
    FOR EACH ROW
    WHEN (NEW.burnout_risk_score IS NOT NULL)
    EXECUTE FUNCTION check_burnout_risk();

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

-- Procedure para calcular estatísticas agregadas de um usuário
CREATE OR REPLACE FUNCTION get_user_statistics(p_user_id INTEGER, p_days INTEGER DEFAULT 30)
RETURNS TABLE (
    avg_mood DECIMAL,
    avg_energy DECIMAL,
    avg_stress DECIMAL,
    avg_sleep DECIMAL,
    avg_work_hours DECIMAL,
    total_records INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        ROUND(AVG(mood_score), 2) as avg_mood,
        ROUND(AVG(energy_score), 2) as avg_energy,
        ROUND(AVG(stress_score), 2) as avg_stress,
        ROUND(AVG(sleep_quality), 2) as avg_sleep,
        ROUND(AVG(work_hours), 2) as avg_work_hours,
        COUNT(*)::INTEGER as total_records
    FROM wellbeing_records
    WHERE user_id = p_user_id
        AND created_at >= CURRENT_TIMESTAMP - (p_days || ' days')::INTERVAL;
END;
$$ LANGUAGE plpgsql;

-- Procedure para obter usuários em risco
CREATE OR REPLACE FUNCTION get_users_at_risk(p_threshold DECIMAL DEFAULT 0.6)
RETURNS TABLE (
    user_id INTEGER,
    user_name VARCHAR,
    avg_risk DECIMAL,
    last_record_date TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.id,
        u.full_name,
        ROUND(AVG(w.burnout_risk_score), 2) as avg_risk,
        MAX(w.created_at) as last_record_date
    FROM users u
    INNER JOIN wellbeing_records w ON u.id = w.user_id
    WHERE w.created_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
        AND w.burnout_risk_score IS NOT NULL
    GROUP BY u.id, u.full_name
    HAVING AVG(w.burnout_risk_score) >= p_threshold
    ORDER BY avg_risk DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- VIEWS (para queries comuns)
-- ============================================================================

-- View de estatísticas diárias agregadas
CREATE OR REPLACE VIEW daily_org_statistics AS
SELECT
    DATE(created_at) as date,
    COUNT(DISTINCT user_id) as active_users,
    ROUND(AVG(mood_score), 2) as avg_mood,
    ROUND(AVG(energy_score), 2) as avg_energy,
    ROUND(AVG(stress_score), 2) as avg_stress,
    ROUND(AVG(sleep_quality), 2) as avg_sleep,
    ROUND(AVG(work_hours), 2) as avg_work_hours,
    COUNT(*) as total_records
FROM wellbeing_records
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================================================
-- SEED DATA (dados de exemplo para testes)
-- ============================================================================

-- Usuário admin padrão (senha: admin123)
INSERT INTO users (email, hashed_password, full_name, role, is_verified)
VALUES (
    'admin@workwell.ai',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEg7Iq',
    'Administrador Sistema',
    'admin',
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Usuário gestor de exemplo (senha: manager123)
INSERT INTO users (email, hashed_password, full_name, role, is_verified)
VALUES (
    'manager@workwell.ai',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEg7Iq',
    'Gestor RH',
    'manager',
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- Usuário colaborador de exemplo (senha: user123)
INSERT INTO users (email, hashed_password, full_name, role, is_verified)
VALUES (
    'user@workwell.ai',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzpLaEg7Iq',
    'João Silva',
    'user',
    TRUE
) ON CONFLICT (email) DO NOTHING;

-- ============================================================================
-- COMMENTS (documentação do schema)
-- ============================================================================

COMMENT ON TABLE users IS 'Tabela de usuários do sistema com autenticação e RBAC';
COMMENT ON TABLE wellbeing_records IS 'Registros diários de bem-estar dos colaboradores';
COMMENT ON TABLE chat_sessions IS 'Histórico de conversas com o chatbot';
COMMENT ON TABLE alerts IS 'Alertas automáticos para casos que requerem atenção';

COMMENT ON FUNCTION get_user_statistics IS 'Calcula estatísticas agregadas de bem-estar de um usuário';
COMMENT ON FUNCTION get_users_at_risk IS 'Retorna lista de usuários com risco elevado de burnout';
