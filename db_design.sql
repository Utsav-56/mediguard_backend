-- ========================================================
-- USERS TABLE
-- ========================================================
CREATE TABLE users
(
    id            SERIAL PRIMARY KEY,
    full_name     TEXT        NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    phone         TEXT,
    profile_image TEXT,
    address       TEXT,
    date_of_birth DATE,
    gender        TEXT CHECK (gender IN ('male', 'female', 'other')),

    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========================================================
-- CARETAKERS TABLE
-- ========================================================
-- Caretakers can be anyone (family, doctor, nurse).
-- Redundancy is intentional — same person with different roles = separate entries.
-- ========================================================================
CREATE TABLE caretakers
(
    id              SERIAL PRIMARY KEY,
    full_name       TEXT        NOT NULL,
    email           TEXT        NOT NULL,
    phone           TEXT        NOT NULL,

    -- If WhatsApp number isn’t provided, backend defaults it to phone.
    whatsapp_number TEXT,
    profile_image   TEXT,
    relationship    TEXT, -- e.g. "mother", "doctor", "nurse"
    address         TEXT,
    note            TEXT, -- optional remarks

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========================================================
-- USER-CARETAKER RELATIONSHIP
-- ========================================================
CREATE TABLE user_caretakers
(
    id           SERIAL PRIMARY KEY,
    user_id      INTEGER     NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    caretaker_id INTEGER     NOT NULL REFERENCES caretakers (id) ON DELETE CASCADE,
    active       BOOLEAN     NOT NULL DEFAULT true,
    note         TEXT, -- e.g. "night shift caregiver"

    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========================================================
-- MEDICINES TABLE
-- ========================================================
CREATE TABLE medicines
(
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER     NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name        TEXT        NOT NULL,
    image       TEXT,
    brand       TEXT,                 -- e.g. "Tylenol"
    description TEXT,                 -- e.g. "500mg, pain reliever"
    start_date  DATE        NOT NULL, -- when regimen starts
    until       DATE,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========================================================
-- ENUM TYPE FOR MEDICINE FORM
-- ========================================================
CREATE TYPE med_type AS ENUM ('tablet', 'capsule', 'syrup', 'injection', 'powder', 'drops', 'other');

-- ========================================================
-- MEDICINE ATTRIBUTES
-- ========================================================
CREATE TABLE medicine_attributes
(
    id          SERIAL PRIMARY KEY,
    medicine_id INTEGER     NOT NULL REFERENCES medicines (id) ON DELETE CASCADE,
    user_id     INTEGER     NOT NULL REFERENCES users (id) ON DELETE CASCADE,

    type        med_type    NOT NULL,
    composition JSONB                DEFAULT '{}'::JSONB, -- e.g. {"paracetamol": "500mg", "caffeine": "30mg"}
    quantity    TEXT,                                     -- "1 tablet", "1 tsp"
    dose        TEXT,                                     -- "500mg"
    dose_unit   TEXT,                                     -- e.g. "mg", "ml"
    schedule_id INTEGER REFERENCES schedules (id),        -- linked later (nullable)

    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========================================================
-- SCHEDULES TABLE
-- ========================================================
CREATE TABLE schedules
(
    id          SERIAL PRIMARY KEY,
    medicine_id INTEGER     NOT NULL REFERENCES medicines (id) ON DELETE CASCADE,
    user_id     INTEGER     NOT NULL REFERENCES users (id) ON DELETE CASCADE,

    timezone    TEXT        NOT NULL DEFAULT 'Asia/Kathmandu',
    time        TIME        NOT NULL, -- e.g. 08:00
    date        DATE        NOT NULL, -- start or specific date
    end_date    DATE,                 -- optional
    instruction TEXT,                 -- e.g. "Half tablet with cold water"
    dose_amount NUMERIC,
    dose_unit   TEXT,
    dose        TEXT,                 -- textual "500mg" if no structured fields
    note        TEXT,

    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========================================================
-- REMINDERS TABLE
-- ========================================================
CREATE TYPE reminder_status AS ENUM ('pending','taken','missed','snoozed');

CREATE TABLE reminders
(
    id           SERIAL PRIMARY KEY,
    schedule_id  INTEGER         NOT NULL REFERENCES schedules (id) ON DELETE CASCADE,
    status       reminder_status NOT NULL DEFAULT 'pending',
    snooze_until TIMESTAMPTZ,
    triggered_at TIMESTAMPTZ, -- when reminder was sent
    resolved_at  TIMESTAMPTZ, -- when user acted

    created_at   TIMESTAMPTZ     NOT NULL DEFAULT now(),
    updated_at   TIMESTAMPTZ     NOT NULL DEFAULT now()
);

-- ========================================================
-- INTAKES TABLE
-- ========================================================
CREATE TYPE intake_status AS ENUM ('taken','missed');

CREATE TABLE intakes
(
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER       NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    medicine_id    INTEGER       NOT NULL REFERENCES medicines (id) ON DELETE CASCADE,
    schedule_id    INTEGER       REFERENCES schedules (id) ON DELETE SET NULL,
    reminder_id    INTEGER       REFERENCES reminders (id) ON DELETE SET NULL,
    status         intake_status NOT NULL,
    scheduled_time TIMESTAMPTZ,
    taken_at       TIMESTAMPTZ,
    recorded_by    TEXT                   DEFAULT 'user', -- could be caretaker or auto
    note           TEXT,

    created_at     TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- ========================================================
-- HEALTH METRICS TABLE
-- ========================================================
-- Flexible JSONB format to support any kind of metric.
-- 
CREATE TABLE health_metrics
(
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER     NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name        TEXT        NOT NULL, -- e.g. "blood_pressure", "blood_sugar"
    data        JSONB       NOT NULL, -- e.g. {"systolic": 120, "diastolic": 80}
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    note        TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ========================================================
-- METRIC READINGS TABLE
-- ========================================================
CREATE TABLE metric_readings
(
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER     NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    metric_id   INTEGER REFERENCES health_metrics (id),
    metric_key  TEXT        NOT NULL, -- redundancy for quick lookup
    recorded_at TIMESTAMPTZ NOT NULL,
    values      JSONB       NOT NULL, -- e.g. {"systolic":120,"diastolic":80,"notes":"after exercise"}
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
