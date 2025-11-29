-- ============================================
-- Health State Templates - Initial Data
-- MediGuard Backend
-- ============================================
-- Run this SQL after Django migrations to populate 
-- predefined health metric templates.
-- 
-- Usage:
--   psql -d your_database -f health_templates.sql
-- OR
--   python manage.py dbshell < health_state/health_templates.sql
-- ============================================

-- Clear existing templates (optional - comment out if you want to preserve existing)
-- TRUNCATE TABLE health_state_healthtemplate RESTART IDENTITY CASCADE;

-- ============================================
-- CARDIOVASCULAR CATEGORY
-- ============================================

INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Blood Pressure',
    'blood-pressure',
    'Measure your systolic and diastolic blood pressure. Regular monitoring helps track cardiovascular health.',
    'heart-pulse',
    'cardiovascular',
    '{
        "systolic": {
            "type": "int",
            "unit": "mmHg",
            "min": 60,
            "max": 250,
            "required": true,
            "label": "Systolic (Upper)",
            "description": "Pressure when heart beats"
        },
        "diastolic": {
            "type": "int",
            "unit": "mmHg",
            "min": 40,
            "max": 150,
            "required": true,
            "label": "Diastolic (Lower)",
            "description": "Pressure between heartbeats"
        },
        "pulse": {
            "type": "int",
            "unit": "bpm",
            "min": 30,
            "max": 220,
            "required": false,
            "label": "Pulse Rate",
            "description": "Heart beats per minute"
        }
    }',
    '{
        "systolic": {"min": 90, "max": 120, "optimal": 115},
        "diastolic": {"min": 60, "max": 80, "optimal": 75},
        "pulse": {"min": 60, "max": 100, "optimal": 72}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Heart Rate',
    'heart-rate',
    'Track your resting heart rate. A lower resting heart rate generally indicates better cardiovascular fitness.',
    'heart',
    'cardiovascular',
    '{
        "bpm": {
            "type": "int",
            "unit": "bpm",
            "min": 30,
            "max": 220,
            "required": true,
            "label": "Heart Rate",
            "description": "Beats per minute"
        },
        "measurement_type": {
            "type": "string",
            "required": false,
            "label": "Measurement Type",
            "description": "resting, active, or post-exercise"
        }
    }',
    '{
        "bpm": {"min": 60, "max": 100, "optimal": 70}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Oxygen Saturation',
    'oxygen-saturation',
    'Monitor blood oxygen levels (SpO2). Important for respiratory health monitoring.',
    'lungs',
    'cardiovascular',
    '{
        "spo2": {
            "type": "int",
            "unit": "%",
            "min": 70,
            "max": 100,
            "required": true,
            "label": "SpO2 Level",
            "description": "Blood oxygen saturation percentage"
        },
        "pulse": {
            "type": "int",
            "unit": "bpm",
            "min": 30,
            "max": 220,
            "required": false,
            "label": "Pulse Rate",
            "description": "Heart beats per minute"
        }
    }',
    '{
        "spo2": {"min": 95, "max": 100, "optimal": 98},
        "pulse": {"min": 60, "max": 100, "optimal": 72}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


-- ============================================
-- METABOLIC CATEGORY
-- ============================================

INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Blood Sugar',
    'blood-sugar',
    'Track blood glucose levels. Essential for diabetes management and metabolic health.',
    'droplet',
    'metabolic',
    '{
        "glucose": {
            "type": "float",
            "unit": "mg/dL",
            "min": 20,
            "max": 600,
            "required": true,
            "label": "Blood Glucose",
            "description": "Blood sugar level"
        },
        "measurement_time": {
            "type": "string",
            "required": true,
            "label": "Measurement Time",
            "description": "fasting, before_meal, after_meal, bedtime, random"
        }
    }',
    '{
        "glucose": {
            "fasting": {"min": 70, "max": 100},
            "after_meal": {"min": 70, "max": 140},
            "random": {"min": 70, "max": 140}
        }
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'HbA1c',
    'hba1c',
    'Glycated hemoglobin test showing average blood sugar over 2-3 months. Key indicator for diabetes control.',
    'chart-line',
    'metabolic',
    '{
        "hba1c": {
            "type": "float",
            "unit": "%",
            "min": 3.0,
            "max": 20.0,
            "required": true,
            "label": "HbA1c Level",
            "description": "Glycated hemoglobin percentage"
        }
    }',
    '{
        "hba1c": {"min": 4.0, "max": 5.6, "prediabetes_max": 6.4, "diabetes_threshold": 6.5}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Cholesterol',
    'cholesterol',
    'Track your cholesterol levels including total, LDL, HDL, and triglycerides.',
    'flask',
    'metabolic',
    '{
        "total": {
            "type": "int",
            "unit": "mg/dL",
            "min": 50,
            "max": 500,
            "required": true,
            "label": "Total Cholesterol",
            "description": "Total cholesterol level"
        },
        "ldl": {
            "type": "int",
            "unit": "mg/dL",
            "min": 20,
            "max": 300,
            "required": false,
            "label": "LDL (Bad)",
            "description": "Low-density lipoprotein"
        },
        "hdl": {
            "type": "int",
            "unit": "mg/dL",
            "min": 10,
            "max": 150,
            "required": false,
            "label": "HDL (Good)",
            "description": "High-density lipoprotein"
        },
        "triglycerides": {
            "type": "int",
            "unit": "mg/dL",
            "min": 20,
            "max": 1000,
            "required": false,
            "label": "Triglycerides",
            "description": "Triglyceride level"
        }
    }',
    '{
        "total": {"max": 200, "borderline": 239},
        "ldl": {"optimal": 100, "borderline": 159},
        "hdl": {"min": 40, "optimal": 60},
        "triglycerides": {"max": 150, "borderline": 199}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


-- ============================================
-- THYROID CATEGORY
-- ============================================

INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Thyroid Panel',
    'thyroid-panel',
    'Complete thyroid function test including TSH, T3, and T4 levels.',
    'activity',
    'thyroid',
    '{
        "tsh": {
            "type": "float",
            "unit": "mIU/L",
            "min": 0.01,
            "max": 100.0,
            "required": true,
            "label": "TSH",
            "description": "Thyroid Stimulating Hormone"
        },
        "t3": {
            "type": "float",
            "unit": "ng/dL",
            "min": 20,
            "max": 400,
            "required": false,
            "label": "T3 (Triiodothyronine)",
            "description": "Active thyroid hormone"
        },
        "t4": {
            "type": "float",
            "unit": "μg/dL",
            "min": 0.5,
            "max": 25.0,
            "required": false,
            "label": "T4 (Thyroxine)",
            "description": "Main thyroid hormone"
        },
        "free_t3": {
            "type": "float",
            "unit": "pg/mL",
            "min": 0.5,
            "max": 10.0,
            "required": false,
            "label": "Free T3",
            "description": "Unbound T3"
        },
        "free_t4": {
            "type": "float",
            "unit": "ng/dL",
            "min": 0.1,
            "max": 5.0,
            "required": false,
            "label": "Free T4",
            "description": "Unbound T4"
        }
    }',
    '{
        "tsh": {"min": 0.4, "max": 4.0},
        "t3": {"min": 80, "max": 200},
        "t4": {"min": 4.5, "max": 12.5},
        "free_t3": {"min": 2.3, "max": 4.2},
        "free_t4": {"min": 0.8, "max": 1.8}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


-- ============================================
-- BODY METRICS CATEGORY
-- ============================================

INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Weight',
    'weight',
    'Track your body weight. Regular monitoring helps with fitness and health goals.',
    'scale',
    'body',
    '{
        "weight": {
            "type": "float",
            "unit": "kg",
            "min": 1,
            "max": 500,
            "required": true,
            "label": "Body Weight",
            "description": "Weight in kilograms"
        }
    }',
    null,
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Body Temperature',
    'body-temperature',
    'Monitor body temperature. Useful for tracking fever and general health.',
    'thermometer',
    'body',
    '{
        "temperature": {
            "type": "float",
            "unit": "°C",
            "min": 30.0,
            "max": 45.0,
            "required": true,
            "label": "Temperature",
            "description": "Body temperature in Celsius"
        },
        "measurement_site": {
            "type": "string",
            "required": false,
            "label": "Measurement Site",
            "description": "oral, axillary, rectal, ear, forehead"
        }
    }',
    '{
        "temperature": {"min": 36.1, "max": 37.2, "fever_threshold": 38.0}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'BMI',
    'bmi',
    'Body Mass Index calculator. Enter weight and height to calculate BMI.',
    'user',
    'body',
    '{
        "weight": {
            "type": "float",
            "unit": "kg",
            "min": 1,
            "max": 500,
            "required": true,
            "label": "Weight",
            "description": "Body weight in kg"
        },
        "height": {
            "type": "float",
            "unit": "cm",
            "min": 50,
            "max": 300,
            "required": true,
            "label": "Height",
            "description": "Height in centimeters"
        },
        "bmi": {
            "type": "float",
            "unit": "kg/m²",
            "min": 10,
            "max": 80,
            "required": false,
            "label": "BMI",
            "description": "Calculated Body Mass Index"
        }
    }',
    '{
        "bmi": {
            "underweight_max": 18.5,
            "normal_min": 18.5,
            "normal_max": 24.9,
            "overweight_max": 29.9,
            "obese_threshold": 30
        }
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


-- ============================================
-- KIDNEY FUNCTION CATEGORY
-- ============================================

INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Kidney Function',
    'kidney-function',
    'Track kidney health markers including creatinine, BUN, and eGFR.',
    'kidney',
    'kidney',
    '{
        "creatinine": {
            "type": "float",
            "unit": "mg/dL",
            "min": 0.1,
            "max": 20.0,
            "required": true,
            "label": "Creatinine",
            "description": "Serum creatinine level"
        },
        "bun": {
            "type": "float",
            "unit": "mg/dL",
            "min": 1,
            "max": 200,
            "required": false,
            "label": "BUN",
            "description": "Blood Urea Nitrogen"
        },
        "egfr": {
            "type": "int",
            "unit": "mL/min/1.73m²",
            "min": 1,
            "max": 150,
            "required": false,
            "label": "eGFR",
            "description": "Estimated Glomerular Filtration Rate"
        }
    }',
    '{
        "creatinine": {"min": 0.6, "max": 1.2},
        "bun": {"min": 7, "max": 20},
        "egfr": {"normal_min": 90, "mild_decrease": 60, "moderate_decrease": 30}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


-- ============================================
-- LIVER FUNCTION CATEGORY
-- ============================================

INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Liver Function',
    'liver-function',
    'Track liver health markers including ALT, AST, and bilirubin.',
    'liver',
    'liver',
    '{
        "alt": {
            "type": "int",
            "unit": "U/L",
            "min": 1,
            "max": 2000,
            "required": true,
            "label": "ALT (SGPT)",
            "description": "Alanine Aminotransferase"
        },
        "ast": {
            "type": "int",
            "unit": "U/L",
            "min": 1,
            "max": 2000,
            "required": false,
            "label": "AST (SGOT)",
            "description": "Aspartate Aminotransferase"
        },
        "bilirubin_total": {
            "type": "float",
            "unit": "mg/dL",
            "min": 0.1,
            "max": 30.0,
            "required": false,
            "label": "Total Bilirubin",
            "description": "Total bilirubin level"
        },
        "albumin": {
            "type": "float",
            "unit": "g/dL",
            "min": 1.0,
            "max": 6.0,
            "required": false,
            "label": "Albumin",
            "description": "Serum albumin level"
        }
    }',
    '{
        "alt": {"max": 40},
        "ast": {"max": 40},
        "bilirubin_total": {"max": 1.2},
        "albumin": {"min": 3.5, "max": 5.0}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


-- ============================================
-- BLOOD COUNT CATEGORY
-- ============================================

INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Hemoglobin',
    'hemoglobin',
    'Track hemoglobin levels. Important for detecting anemia and blood health.',
    'droplets',
    'blood',
    '{
        "hemoglobin": {
            "type": "float",
            "unit": "g/dL",
            "min": 3.0,
            "max": 25.0,
            "required": true,
            "label": "Hemoglobin",
            "description": "Hemoglobin concentration"
        }
    }',
    '{
        "hemoglobin": {
            "male_min": 13.5, "male_max": 17.5,
            "female_min": 12.0, "female_max": 16.0
        }
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


-- ============================================
-- VITAMINS & MINERALS CATEGORY
-- ============================================

INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Vitamin D',
    'vitamin-d',
    'Track Vitamin D levels. Essential for bone health and immune function.',
    'sun',
    'vitamins',
    '{
        "vitamin_d": {
            "type": "float",
            "unit": "ng/mL",
            "min": 1,
            "max": 200,
            "required": true,
            "label": "Vitamin D (25-OH)",
            "description": "25-hydroxyvitamin D level"
        }
    }',
    '{
        "vitamin_d": {"deficient_max": 20, "insufficient_max": 30, "sufficient_min": 30, "optimal": 50}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Vitamin B12',
    'vitamin-b12',
    'Track Vitamin B12 levels. Important for nerve function and red blood cell production.',
    'pill',
    'vitamins',
    '{
        "vitamin_b12": {
            "type": "float",
            "unit": "pg/mL",
            "min": 50,
            "max": 2000,
            "required": true,
            "label": "Vitamin B12",
            "description": "Serum B12 level"
        }
    }',
    '{
        "vitamin_b12": {"deficient_max": 200, "min": 200, "max": 900}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Iron Studies',
    'iron-studies',
    'Track iron levels including serum iron, ferritin, and TIBC.',
    'magnet',
    'vitamins',
    '{
        "serum_iron": {
            "type": "int",
            "unit": "μg/dL",
            "min": 10,
            "max": 500,
            "required": true,
            "label": "Serum Iron",
            "description": "Iron in blood serum"
        },
        "ferritin": {
            "type": "float",
            "unit": "ng/mL",
            "min": 1,
            "max": 2000,
            "required": false,
            "label": "Ferritin",
            "description": "Iron storage protein"
        },
        "tibc": {
            "type": "int",
            "unit": "μg/dL",
            "min": 100,
            "max": 600,
            "required": false,
            "label": "TIBC",
            "description": "Total Iron Binding Capacity"
        }
    }',
    '{
        "serum_iron": {"min": 60, "max": 170},
        "ferritin": {"male_min": 20, "male_max": 500, "female_min": 20, "female_max": 200},
        "tibc": {"min": 250, "max": 400}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


-- ============================================
-- URIC ACID
-- ============================================

INSERT INTO health_state_healthtemplate (name, slug, description, icon, category, schema, normal_range, is_active, created_at, updated_at)
VALUES (
    'Uric Acid',
    'uric-acid',
    'Track uric acid levels. High levels may indicate risk of gout or kidney stones.',
    'crystal',
    'metabolic',
    '{
        "uric_acid": {
            "type": "float",
            "unit": "mg/dL",
            "min": 1.0,
            "max": 20.0,
            "required": true,
            "label": "Uric Acid",
            "description": "Serum uric acid level"
        }
    }',
    '{
        "uric_acid": {"male_max": 7.0, "female_max": 6.0, "high_risk": 9.0}
    }',
    true,
    NOW(),
    NOW()
) ON CONFLICT (slug) DO UPDATE SET
    schema = EXCLUDED.schema,
    normal_range = EXCLUDED.normal_range,
    updated_at = NOW();


-- ============================================
-- Verify insertion
-- ============================================
SELECT id, name, slug, category FROM health_state_healthtemplate ORDER BY category, name;
