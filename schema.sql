-- ============================================================
-- MediGuard PostgreSQL Database Schema
-- Generated: 2025-11-30
-- ============================================================
-- This schema includes all Django models from the following apps:
-- 1. accounts (User model - custom auth)
-- 2. medicines (Medicines model)
-- 3. intake (Intake model)
-- 4. health_state (HealthTemplate, HealthRecord models)
-- 5. alarm (no custom models)
-- 6. image_processer (no custom models)
-- 7. ping (no custom models)
-- ============================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- DROP EXISTING TABLES (in reverse order of dependencies)
-- ============================================================
DROP TABLE IF EXISTS health_state_healthrecord CASCADE;
DROP TABLE IF EXISTS health_state_healthtemplate CASCADE;
DROP TABLE IF EXISTS intake_intake CASCADE;
DROP TABLE IF EXISTS medicines_medicines CASCADE;
DROP TABLE IF EXISTS accounts_user_user_permissions CASCADE;
DROP TABLE IF EXISTS accounts_user_groups CASCADE;
DROP TABLE IF EXISTS accounts_user CASCADE;

-- Drop Django default tables if recreating
DROP TABLE IF EXISTS auth_permission CASCADE;
DROP TABLE IF EXISTS auth_group_permissions CASCADE;
DROP TABLE IF EXISTS auth_group CASCADE;
DROP TABLE IF EXISTS django_content_type CASCADE;
DROP TABLE IF EXISTS django_migrations CASCADE;
DROP TABLE IF EXISTS django_session CASCADE;
DROP TABLE IF EXISTS django_admin_log CASCADE;

-- ============================================================
-- DJANGO DEFAULT TABLES
-- ============================================================

-- Django Content Type (required for permissions)
CREATE TABLE django_content_type (
    id SERIAL PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

-- Django Migrations Tracking
CREATE TABLE django_migrations (
    id SERIAL PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Django Sessions
CREATE TABLE django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX django_session_expire_date_idx ON django_session(expire_date);

-- Auth Group
CREATE TABLE auth_group (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
);

-- Auth Permission
CREATE TABLE auth_permission (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INTEGER NOT NULL REFERENCES django_content_type(id) ON DELETE CASCADE,
    codename VARCHAR(100) NOT NULL,
    UNIQUE(content_type_id, codename)
);

-- Auth Group Permissions (Many-to-Many)
CREATE TABLE auth_group_permissions (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE(group_id, permission_id)
);

-- ============================================================
-- ACCOUNTS APP
-- ============================================================

-- Custom User Model
-- Replaces Django's default auth_user table
CREATE TABLE accounts_user (
    id SERIAL PRIMARY KEY,
    
    -- Authentication fields
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE NULL,
    
    -- PermissionsMixin fields
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Custom User fields
    email VARCHAR(254) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NULL,
    address TEXT NULL,
    profile_image VARCHAR(100) NULL,  -- Stores path: profile_images/user_<id>.<ext>
    
    -- Status fields
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE
);

-- Indexes for accounts_user
CREATE INDEX accounts_user_email_idx ON accounts_user(email);

-- User Groups (Many-to-Many relationship with auth_group)
CREATE TABLE accounts_user_groups (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    group_id INTEGER NOT NULL REFERENCES auth_group(id) ON DELETE CASCADE,
    UNIQUE(user_id, group_id)
);

CREATE INDEX accounts_user_groups_user_id_idx ON accounts_user_groups(user_id);
CREATE INDEX accounts_user_groups_group_id_idx ON accounts_user_groups(group_id);

-- User Permissions (Many-to-Many relationship with auth_permission)
CREATE TABLE accounts_user_user_permissions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES auth_permission(id) ON DELETE CASCADE,
    UNIQUE(user_id, permission_id)
);

CREATE INDEX accounts_user_user_permissions_user_id_idx ON accounts_user_user_permissions(user_id);
CREATE INDEX accounts_user_user_permissions_permission_id_idx ON accounts_user_user_permissions(permission_id);

-- ============================================================
-- MEDICINES APP
-- ============================================================

-- Medicines Model
CREATE TABLE medicines_medicines (
    id SERIAL PRIMARY KEY,
    
    -- Foreign Key to User
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    
    -- Medicine details
    name VARCHAR(255) NOT NULL,
    amount INTEGER NOT NULL DEFAULT 1,  -- Number of units to take at a time
    dosage INTEGER NULL,                -- Dosage in mg (e.g., 500 for 500mg)
    
    -- Schedule fields (stored as JSONB)
    days_of_week JSONB NOT NULL DEFAULT '[1, 2, 3, 4, 5, 6, 7]',  -- Days: 1=Sunday to 7=Saturday
    time JSONB NOT NULL DEFAULT '["20:00"]',                      -- Times in HH:MM format
    
    -- Optional fields
    image VARCHAR(100) NULL,  -- Stores path: medicines/medicine_<id>.<ext>
    help_message TEXT NULL,   -- User notes about the medicine
    
    -- Schedule duration
    start_date TIMESTAMP WITH TIME ZONE NULL,
    end_date TIMESTAMP WITH TIME ZONE NULL
);

-- Indexes for medicines_medicines
CREATE INDEX medicines_medicines_user_id_idx ON medicines_medicines(user_id);
CREATE INDEX medicines_medicines_name_idx ON medicines_medicines(name);

-- ============================================================
-- INTAKE APP
-- ============================================================

-- Intake Status Enum Type
DO $$ BEGIN
    CREATE TYPE intake_status AS ENUM ('pending', 'taken', 'skipped', 'missed');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Intake Model
CREATE TABLE intake_intake (
    id SERIAL PRIMARY KEY,
    
    -- Foreign Keys
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    medicine_id INTEGER NOT NULL REFERENCES medicines_medicines(id) ON DELETE CASCADE,
    
    -- Schedule fields
    scheduled_date DATE NOT NULL,
    scheduled_time TIME NOT NULL,
    
    -- Status (using VARCHAR to match Django's CharField choices)
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'taken', 'skipped', 'missed')),
    
    -- Actual intake time (only filled when status is 'taken')
    taken_at TIMESTAMP WITH TIME ZONE NULL,
    
    -- User notes
    notes TEXT NULL,
    
    -- Auto timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint: No duplicate intake for same user, medicine, date, and time
    UNIQUE(user_id, medicine_id, scheduled_date, scheduled_time)
);

-- Indexes for intake_intake
CREATE INDEX intake_intake_user_id_idx ON intake_intake(user_id);
CREATE INDEX intake_intake_medicine_id_idx ON intake_intake(medicine_id);
CREATE INDEX intake_intake_scheduled_date_idx ON intake_intake(scheduled_date);
CREATE INDEX intake_intake_status_idx ON intake_intake(status);
CREATE INDEX intake_intake_scheduled_datetime_idx ON intake_intake(scheduled_date, scheduled_time);

-- ============================================================
-- HEALTH STATE APP
-- ============================================================

-- Health Template Model
-- Predefined templates for health metrics (admin-managed)
CREATE TABLE health_state_healthtemplate (
    id SERIAL PRIMARY KEY,
    
    -- Template identification
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    
    -- Description and display
    description TEXT NULL,
    icon VARCHAR(50) NULL,        -- Icon identifier for frontend
    category VARCHAR(50) NULL,    -- Category for grouping
    
    -- Schema definition (JSONB)
    -- Format: {"field_name": {"type": "int|float|string|boolean", "unit": "mmHg", "min": 0, "max": 300, "required": true}}
    schema JSONB NOT NULL,
    
    -- Normal ranges for reference (JSONB)
    normal_range JSONB NULL,
    
    -- Status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Auto timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for health_state_healthtemplate
CREATE INDEX health_state_healthtemplate_slug_idx ON health_state_healthtemplate(slug);
CREATE INDEX health_state_healthtemplate_category_idx ON health_state_healthtemplate(category);
CREATE INDEX health_state_healthtemplate_is_active_idx ON health_state_healthtemplate(is_active);

-- Health Record Model
-- User's health records based on templates
CREATE TABLE health_state_healthrecord (
    id SERIAL PRIMARY KEY,
    
    -- Foreign Keys
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    template_id INTEGER NOT NULL REFERENCES health_state_healthtemplate(id) ON DELETE RESTRICT,
    
    -- Health data (JSONB following template schema)
    data JSONB NOT NULL,
    
    -- When the measurement was taken
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Optional fields
    notes TEXT NULL,
    location VARCHAR(255) NULL,
    
    -- Auto timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for health_state_healthrecord
CREATE INDEX health_state_healthrecord_user_id_idx ON health_state_healthrecord(user_id);
CREATE INDEX health_state_healthrecord_template_id_idx ON health_state_healthrecord(template_id);
CREATE INDEX health_state_healthrecord_recorded_at_idx ON health_state_healthrecord(recorded_at);
CREATE INDEX health_state_healthrecord_user_template_idx ON health_state_healthrecord(user_id, template_id);

-- ============================================================
-- DJANGO ADMIN LOG (for admin panel tracking)
-- ============================================================

CREATE TABLE django_admin_log (
    id SERIAL PRIMARY KEY,
    action_time TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    object_id TEXT NULL,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT NOT NULL CHECK (action_flag >= 0),
    change_message TEXT NOT NULL,
    content_type_id INTEGER NULL REFERENCES django_content_type(id) ON DELETE SET NULL,
    user_id INTEGER NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE
);

CREATE INDEX django_admin_log_content_type_id_idx ON django_admin_log(content_type_id);
CREATE INDEX django_admin_log_user_id_idx ON django_admin_log(user_id);

-- ============================================================
-- TRIGGERS FOR AUTO-UPDATING updated_at TIMESTAMPS
-- ============================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for intake_intake
CREATE TRIGGER update_intake_intake_updated_at
    BEFORE UPDATE ON intake_intake
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for health_state_healthtemplate
CREATE TRIGGER update_health_state_healthtemplate_updated_at
    BEFORE UPDATE ON health_state_healthtemplate
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for health_state_healthrecord
CREATE TRIGGER update_health_state_healthrecord_updated_at
    BEFORE UPDATE ON health_state_healthrecord
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- SAMPLE DATA FOR HEALTH TEMPLATES (Optional - Comment out if not needed)
-- ============================================================

-- Blood Pressure Template
INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active)
VALUES (
    'Blood Pressure',
    'blood-pressure',
    'Record your systolic and diastolic blood pressure readings',
    'heart',
    'cardiovascular',
    '{
        "systolic": {"type": "int", "unit": "mmHg", "min": 70, "max": 250, "required": true},
        "diastolic": {"type": "int", "unit": "mmHg", "min": 40, "max": 150, "required": true},
        "pulse": {"type": "int", "unit": "bpm", "min": 30, "max": 220, "required": false}
    }',
    '{
        "systolic": {"min": 90, "max": 120, "label": "Normal"},
        "diastolic": {"min": 60, "max": 80, "label": "Normal"},
        "pulse": {"min": 60, "max": 100, "label": "Normal"}
    }',
    TRUE
) ON CONFLICT (slug) DO NOTHING;

-- Blood Sugar Template
INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active)
VALUES (
    'Blood Sugar',
    'blood-sugar',
    'Record your blood glucose levels',
    'droplet',
    'metabolic',
    '{
        "glucose_level": {"type": "float", "unit": "mg/dL", "min": 20, "max": 600, "required": true},
        "measurement_type": {"type": "string", "required": true}
    }',
    '{
        "glucose_level": {"fasting": {"min": 70, "max": 100}, "post_meal": {"min": 70, "max": 140}}
    }',
    TRUE
) ON CONFLICT (slug) DO NOTHING;

-- Body Temperature Template
INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active)
VALUES (
    'Body Temperature',
    'body-temperature',
    'Record your body temperature',
    'thermometer',
    'vital-signs',
    '{
        "temperature": {"type": "float", "unit": "°F", "min": 90, "max": 110, "required": true},
        "measurement_location": {"type": "string", "required": false}
    }',
    '{
        "temperature": {"min": 97.8, "max": 99.1, "label": "Normal"}
    }',
    TRUE
) ON CONFLICT (slug) DO NOTHING;

-- Weight Template
INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active)
VALUES (
    'Weight',
    'weight',
    'Record your body weight',
    'scale',
    'body-metrics',
    '{
        "weight": {"type": "float", "unit": "kg", "min": 1, "max": 500, "required": true}
    }',
    NULL,
    TRUE
) ON CONFLICT (slug) DO NOTHING;

-- Oxygen Saturation Template
INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active)
VALUES (
    'Oxygen Saturation',
    'oxygen-saturation',
    'Record your blood oxygen saturation level (SpO2)',
    'activity',
    'vital-signs',
    '{
        "spo2": {"type": "int", "unit": "%", "min": 50, "max": 100, "required": true}
    }',
    '{
        "spo2": {"min": 95, "max": 100, "label": "Normal"}
    }',
    TRUE
) ON CONFLICT (slug) DO NOTHING;

-- ============================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================

COMMENT ON TABLE accounts_user IS 'Custom user model replacing Django default auth_user. Stores user authentication and profile information.';
COMMENT ON COLUMN accounts_user.phone_number IS 'Phone number with validation: 7-13 digits, optional + prefix';
COMMENT ON COLUMN accounts_user.profile_image IS 'Path to profile image: profile_images/user_<id>.<ext>';

COMMENT ON TABLE medicines_medicines IS 'Stores medicine information and schedules for users';
COMMENT ON COLUMN medicines_medicines.days_of_week IS 'JSONB array of days (1=Sunday to 7=Saturday)';
COMMENT ON COLUMN medicines_medicines.time IS 'JSONB array of times in HH:MM format';

COMMENT ON TABLE intake_intake IS 'Records medicine intake events with status tracking';
COMMENT ON COLUMN intake_intake.status IS 'Intake status: pending, taken, skipped, or missed';

COMMENT ON TABLE health_state_healthtemplate IS 'Admin-managed templates defining health metric structures';
COMMENT ON COLUMN health_state_healthtemplate.schema IS 'JSONB schema defining fields, types, units, and validation rules';

COMMENT ON TABLE health_state_healthrecord IS 'User health records based on templates';
COMMENT ON COLUMN health_state_healthrecord.data IS 'JSONB health data following the associated template schema';

-- ============================================================
-- END OF SCHEMA
-- ============================================================
