-- ============================================================
-- MediGuard MySQL/MariaDB Database Schema
-- Generated: 2025-11-30
-- Compatible with: MySQL 8.0+ / MariaDB 10.5+
-- ============================================================

-- ============================================================
-- DROP EXISTING TABLES (in reverse dependency order)
-- ============================================================


-- ============================================================
-- ACCOUNTS APP
-- ============================================================

-- Custom User Table
CREATE TABLE accounts_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    email VARCHAR(254) NOT NULL UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20) NULL,
    address TEXT NULL,
    profile_image VARCHAR(100) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    is_staff TINYINT(1) NOT NULL DEFAULT 0,
    KEY accounts_user_email_idx (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



-- ============================================================
-- MEDICINES APP
-- ============================================================

-- Medicines Table
CREATE TABLE medicines_medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    amount INT NOT NULL DEFAULT 1,
    dosage INT NULL,
    days_of_week JSON NOT NULL DEFAULT (JSON_ARRAY(1, 2, 3, 4, 5, 6, 7)),
    time JSON NOT NULL DEFAULT (JSON_ARRAY('20:00')),
    image VARCHAR(100) NULL,
    help_message TEXT NULL,
    start_date DATETIME(6) NULL,
    end_date DATETIME(6) NULL,
    KEY medicines_medicines_user_id_idx (user_id),
    KEY medicines_medicines_name_idx (name),
    CONSTRAINT medicines_medicines_user_id_fk 
        FOREIGN KEY (user_id) 
        REFERENCES accounts_user (id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- INTAKE APP
-- ============================================================

-- Intake Table
CREATE TABLE intake_intake (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    medicine_id INT NOT NULL,
    scheduled_date DATE NOT NULL,
    scheduled_time TIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    taken_at DATETIME(6) NULL,
    notes TEXT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY intake_intake_user_medicine_date_time_unique (user_id, medicine_id, scheduled_date, scheduled_time),
    KEY intake_intake_user_id_idx (user_id),
    KEY intake_intake_medicine_id_idx (medicine_id),
    KEY intake_intake_scheduled_date_idx (scheduled_date),
    KEY intake_intake_status_idx (status),
    CONSTRAINT intake_intake_status_check 
        CHECK (status IN ('pending', 'taken', 'skipped', 'missed')),
    CONSTRAINT intake_intake_user_id_fk 
        FOREIGN KEY (user_id) 
        REFERENCES accounts_user (id) 
        ON DELETE CASCADE,
    CONSTRAINT intake_intake_medicine_id_fk 
        FOREIGN KEY (medicine_id) 
        REFERENCES medicines_medicines (id) 
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- HEALTH STATE APP
-- ============================================================

-- Health Template Table
CREATE TABLE health_state_healthtemplate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT NULL,
    icon VARCHAR(50) NULL,
    category VARCHAR(50) NULL,
    `schema` JSON NOT NULL,
    normal_range JSON NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    KEY health_state_healthtemplate_slug_idx (slug),
    KEY health_state_healthtemplate_category_idx (category),
    KEY health_state_healthtemplate_is_active_idx (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Health Record Table
CREATE TABLE health_state_healthrecord (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    template_id INT NOT NULL,
    data JSON NOT NULL,
    recorded_at DATETIME(6) NOT NULL,
    notes TEXT NULL,
    location VARCHAR(255) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    KEY health_state_healthrecord_user_id_idx (user_id),
    KEY health_state_healthrecord_template_id_idx (template_id),
    KEY health_state_healthrecord_recorded_at_idx (recorded_at),
    KEY health_state_healthrecord_user_template_idx (user_id, template_id),
    CONSTRAINT health_state_healthrecord_user_id_fk 
        FOREIGN KEY (user_id) 
        REFERENCES accounts_user (id) 
        ON DELETE CASCADE,
    CONSTRAINT health_state_healthrecord_template_id_fk 
        FOREIGN KEY (template_id) 
        REFERENCES health_state_healthtemplate (id) 
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- END OF SCHEMA
-- ============================================================
