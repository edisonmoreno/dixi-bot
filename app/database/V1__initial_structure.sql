-- =====================================================
-- EXTENSIONES
-- =====================================================
CREATE EXTENSION IF NOT EXISTS vector;
-- habilita gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;
-- =====================================================
-- FUNCIÓN PARA updated_at
-- =====================================================
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = NOW();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- =====================================================
-- TENANTS (empresas registradas)
-- =====================================================
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED', 'INACTIVE')),
    plan VARCHAR(50) DEFAULT 'FREE',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TRIGGER trg_tenants_updated BEFORE
UPDATE ON tenants FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- =====================================================
CREATE TABLE tenant_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    timezone VARCHAR(50) NOT NULL DEFAULT 'America/Bogota',
    business_hours JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TRIGGER trg_tenant_settings_updated BEFORE
UPDATE ON tenant_settings FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- =====================================================
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    instructions TEXT NOT NULL DEFAULT 'Eres un asistente profesional.',
    tone VARCHAR(30) DEFAULT 'Profesional',
    language VARCHAR(10) DEFAULT 'es',
    settings JSONB NOT NULL DEFAULT '{
        "provider": "openai",
        "model": "gemini-3.5-flash-lite",
        "temperature": 0.5,
        "timeout": 30,
        "max_tokens": 300,
        "max_retries": 2
    }',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TRIGGER trg_agents_updated BEFORE
UPDATE ON agents FOR EACH ROW EXECUTE FUNCTION set_updated_at();