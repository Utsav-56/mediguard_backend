-- ============================================================
-- MediGuard PostgreSQL Database Schema
-- Generated: 2025-11-30
-- Compatible with: PostgreSQL 12+
-- ============================================================

-- ============================================================
-- DROP EXISTING TABLES (in reverse dependency order)
-- ============================================================

DROP TABLE IF EXISTS health_state_healthrecord CASCADE;
DROP TABLE IF EXISTS health_state_healthtemplate CASCADE;
DROP TABLE IF EXISTS intake_intake CASCADE;
DROP TABLE IF EXISTS medicines_medicines CASCADE;
DROP TABLE IF EXISTS accounts_user_user_permissions CASCADE;
DROP TABLE IF EXISTS accounts_user_groups CASCADE;
DROP TABLE IF EXISTS accounts_user CASCADE;
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;
DROP TABLE IF EXISTS django_migrations CASCADE;
DROP TABLE IF EXISTS django_session CASCADE;
DROP TABLE IF EXISTS django_admin_log CASCADE;


-- ============================================================
-- DJANGO CORE TABLES
-- ============================================================

-- Content Type Table (required for permissions)
CREATE TABLE django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    CONSTRAINT django_content_type_app_label_model_unique UNIQUE (app_label, model)
);

-- Migrations Tracking Table
CREATE TABLE django_migrations (
    id BIGSERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Session Table
CREATE TABLE django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX django_session_expire_date_idx ON django_session (expire_date);

-- Auth Group Table
CREATE TABLE auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- Auth Permission Table
CREATE TABLE auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER NOT NULL,
    codename VARCHAR(100) NOT NULL,
    CONSTRAINT auth_permission_content_type_id_fk 
        FOREIGN KEY (content_type_id) 
        REFERENCES django_content_type (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT auth_permission_content_type_id_codename_unique 
        UNIQUE (content_type_id, codename)
);

CREATE INDEX auth_permission_content_type_id_idx ON auth_permission (content_type_id);

-- Auth Group Permissions (Many-to-Many)
CREATE TABLE auth_group_permissions (
    id BIGSERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    CONSTRAINT auth_group_permissions_group_id_fk 
        FOREIGN KEY (group_id) 
        REFERENCES auth_group (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT auth_group_permissions_permission_id_fk 
        FOREIGN KEY (permission_id) 
        REFERENCES auth_permission (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT auth_group_permissions_group_id_permission_id_unique 
        UNIQUE (group_id, permission_id)
);

CREATE INDEX auth_group_permissions_group_id_idx ON auth_group_permissions (group_id);
CREATE INDEX auth_group_permissions_permission_id_idx ON auth_group_permissions (permission_id);


-- ============================================================
-- ACCOUNTS APP
-- ============================================================

-- Custom User Table
CREATE TABLE accounts_user (
    id SERIAL PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    email VARCHAR(254) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NULL,
    address TEXT NULL,
    profile_image VARCHAR(100) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX accounts_user_email_idx ON accounts_user (email);

-- User Groups (Many-to-Many: accounts_user <-> auth_group)
CREATE TABLE accounts_user_groups (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    CONSTRAINT accounts_user_groups_user_id_fk 
        FOREIGN KEY (user_id) 
        REFERENCES accounts_user (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT accounts_user_groups_group_id_fk 
        FOREIGN KEY (group_id) 
        REFERENCES auth_group (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT accounts_user_groups_user_id_group_id_unique 
        UNIQUE (user_id, group_id)
);

CREATE INDEX accounts_user_groups_user_id_idx ON accounts_user_groups (user_id);
CREATE INDEX accounts_user_groups_group_id_idx ON accounts_user_groups (group_id);

-- User Permissions (Many-to-Many: accounts_user <-> auth_permission)
CREATE TABLE accounts_user_user_permissions (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    CONSTRAINT accounts_user_user_permissions_user_id_fk 
        FOREIGN KEY (user_id) 
        REFERENCES accounts_user (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT accounts_user_user_permissions_permission_id_fk 
        FOREIGN KEY (permission_id) 
        REFERENCES auth_permission (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT accounts_user_user_permissions_user_id_permission_id_unique 
        UNIQUE (user_id, permission_id)
);

CREATE INDEX accounts_user_user_permissions_user_id_idx ON accounts_user_user_permissions (user_id);
CREATE INDEX accounts_user_user_permissions_permission_id_idx ON accounts_user_user_permissions (permission_id);


-- ============================================================
-- MEDICINES APP
-- ============================================================

-- Medicines Table
CREATE TABLE medicines_medicines (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    amount INTEGER NOT NULL DEFAULT 1,
    dosage INTEGER NULL,
    days_of_week JSONB NOT NULL DEFAULT '[1, 2, 3, 4, 5, 6, 7]',
    time JSONB NOT NULL DEFAULT '["20:00"]',
    image VARCHAR(100) NULL,
    help_message TEXT NULL,
    start_date TIMESTAMP WITH TIME ZONE NULL,
    end_date TIMESTAMP WITH TIME ZONE NULL,
    CONSTRAINT medicines_medicines_user_id_fk 
        FOREIGN KEY (user_id) 
        REFERENCES accounts_user (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX medicines_medicines_user_id_idx ON medicines_medicines (user_id);
CREATE INDEX medicines_medicines_name_idx ON medicines_medicines (name);


-- ============================================================
-- INTAKE APP
-- ============================================================

-- Intake Table
CREATE TABLE intake_intake (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    scheduled_date DATE NOT NULL,
    scheduled_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    taken_at TIMESTAMP WITH TIME ZONE NULL,
    notes TEXT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT intake_intake_user_id_fk 
        FOREIGN KEY (user_id) 
        REFERENCES accounts_user (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT intake_intake_medicine_id_fk 
        FOREIGN KEY (medicine_id) 
        REFERENCES medicines_medicines (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT intake_intake_status_check 
        CHECK (status IN ('pending', 'taken', 'skipped', 'missed')),
    CONSTRAINT intake_intake_user_medicine_date_time_unique 
        UNIQUE (user_id, medicine_id, scheduled_date, scheduled_time)
);

CREATE INDEX intake_intake_user_id_idx ON intake_intake (user_id);
CREATE INDEX intake_intake_medicine_id_idx ON intake_intake (medicine_id);
CREATE INDEX intake_intake_scheduled_date_idx ON intake_intake (scheduled_date);
CREATE INDEX intake_intake_status_idx ON intake_intake (status);


-- ============================================================
-- HEALTH STATE APP
-- ============================================================

-- Health Template Table
CREATE TABLE health_state_healthtemplate (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL,
    icon VARCHAR(50) NULL,
    category VARCHAR(50) NULL,
    schema JSONB NOT NULL,
    normal_range JSONB NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX health_state_healthtemplate_slug_idx ON health_state_healthtemplate (slug);
CREATE INDEX health_state_healthtemplate_category_idx ON health_state_healthtemplate (category);
CREATE INDEX health_state_healthtemplate_is_active_idx ON health_state_healthtemplate (is_active);

-- Health Record Table
CREATE TABLE health_state_healthrecord (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    template_id INTEGER NOT NULL,
    data JSONB NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    notes TEXT NULL,
    location VARCHAR(255) NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT health_state_healthrecord_user_id_fk 
        FOREIGN KEY (user_id) 
        REFERENCES accounts_user (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT health_state_healthrecord_template_id_fk 
        FOREIGN KEY (template_id) 
        REFERENCES health_state_healthtemplate (id) 
        ON DELETE RESTRICT 
        DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX health_state_healthrecord_user_id_idx ON health_state_healthrecord (user_id);
CREATE INDEX health_state_healthrecord_template_id_idx ON health_state_healthrecord (template_id);
CREATE INDEX health_state_healthrecord_recorded_at_idx ON health_state_healthrecord (recorded_at);
CREATE INDEX health_state_healthrecord_user_template_idx ON health_state_healthrecord (user_id, template_id);


-- ============================================================
-- DJANGO ADMIN LOG TABLE
-- ============================================================

CREATE TABLE django_admin_log (
    id SERIAL PRIMARY KEY,
    action_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    object_id TEXT NULL,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL CHECK (action_flag >= 0),
    change_message TEXT NOT NULL,
    content_type_id INTEGER NULL,
    user_id INTEGER NOT NULL,
    CONSTRAINT django_admin_log_content_type_id_fk 
        FOREIGN KEY (content_type_id) 
        REFERENCES django_content_type (id) 
        ON DELETE SET NULL 
        DEFERRABLE INITIALLY DEFERRED,
    CONSTRAINT django_admin_log_user_id_fk 
        FOREIGN KEY (user_id) 
        REFERENCES accounts_user (id) 
        ON DELETE CASCADE 
        DEFERRABLE INITIALLY DEFERRED
);

CREATE INDEX django_admin_log_content_type_id_idx ON django_admin_log (content_type_id);
CREATE INDEX django_admin_log_user_id_idx ON django_admin_log (user_id);


-- ============================================================
-- TRIGGER FUNCTION FOR AUTO-UPDATING updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to intake_intake
CREATE TRIGGER set_timestamp_intake_intake
    BEFORE UPDATE ON intake_intake
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_timestamp();

-- Apply trigger to health_state_healthtemplate
CREATE TRIGGER set_timestamp_health_state_healthtemplate
    BEFORE UPDATE ON health_state_healthtemplate
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_timestamp();

-- Apply trigger to health_state_healthrecord
CREATE TRIGGER set_timestamp_health_state_healthrecord
    BEFORE UPDATE ON health_state_healthrecord
    FOR EACH ROW
    EXECUTE FUNCTION trigger_set_timestamp();


-- ============================================================
-- END OF SCHEMA
-- ============================================================
