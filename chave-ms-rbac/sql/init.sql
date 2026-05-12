-- AuthorizationDB schema do chave-ms-rbac.
-- Roles tratadas como strings opacas (catálogo); novas roles entram por
-- dados, não por código. Atribuições nunca são apagadas — marcamos
-- revoked_at para preservar auditoria.

CREATE TABLE IF NOT EXISTS roles (
    role_id     SERIAL PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id    INTEGER PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_role_assignments (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES user_roles(user_id),
    role_id     INTEGER NOT NULL REFERENCES roles(role_id),
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    assigned_by INTEGER,
    revoked_at  TIMESTAMPTZ
);

-- Garante no máximo uma atribuição ativa por (usuário, role).
CREATE UNIQUE INDEX IF NOT EXISTS uq_active_assignment
    ON user_role_assignments (user_id, role_id)
    WHERE revoked_at IS NULL;

-- Seed mínimo do catálogo.
INSERT INTO roles (name, description) VALUES
    ('admin', 'Administrador'),
    ('user',  'Usuário comum')
ON CONFLICT (name) DO NOTHING;
