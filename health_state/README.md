# Health State App

Track and monitor various health metrics using predefined templates. Store blood pressure, blood sugar, thyroid levels, and many more health indicators with structured data validation.

## Overview

The Health State app provides:

- **Predefined Templates**: Ready-to-use health metric templates with schema validation
- **Flexible Data Storage**: Store health records based on template schemas
- **Data Validation**: Automatic validation of data types, ranges, and required fields
- **Statistics & Insights**: Get statistics like min, max, average for your health records
- **Category Organization**: Templates organized by health categories

## Base URL

All endpoints are prefixed with `/health/`

## Authentication

All endpoints require JWT authentication. Include the token in the header:

```
Authorization: Bearer <access_token>
```

---

## Models

### HealthTemplate

Predefined templates defining what health metrics can be tracked.

| Field          | Type     | Description                                         |
| -------------- | -------- | --------------------------------------------------- |
| `id`           | Integer  | Primary key                                         |
| `name`         | String   | Template name (e.g., "Blood Pressure")              |
| `slug`         | String   | URL-friendly identifier (e.g., "blood-pressure")    |
| `description`  | Text     | Detailed description of the health metric           |
| `icon`         | String   | Icon identifier for UI                              |
| `category`     | String   | Category grouping (cardiovascular, metabolic, etc.) |
| `schema`       | JSON     | Field definitions with types, units, ranges         |
| `normal_range` | JSON     | Reference ranges for normal values                  |
| `is_active`    | Boolean  | Whether template is available                       |
| `created_at`   | DateTime | Creation timestamp                                  |
| `updated_at`   | DateTime | Last update timestamp                               |

#### Schema Format

```json
{
	"field_name": {
		"type": "int|float|string|boolean",
		"unit": "mmHg",
		"min": 0,
		"max": 300,
		"required": true,
		"label": "Display Name",
		"description": "Field description"
	}
}
```

### HealthRecord

User's health data entries based on templates.

| Field         | Type       | Description                 |
| ------------- | ---------- | --------------------------- |
| `id`          | Integer    | Primary key                 |
| `user`        | ForeignKey | Associated user             |
| `template`    | ForeignKey | Associated template         |
| `data`        | JSON       | Health metric values        |
| `recorded_at` | DateTime   | When measurement was taken  |
| `notes`       | Text       | Optional user notes         |
| `location`    | String     | Where measurement was taken |
| `created_at`  | DateTime   | Creation timestamp          |
| `updated_at`  | DateTime   | Last update timestamp       |

---

## API Endpoints

### Templates

#### 1. List All Templates

Get all active health templates.

**Endpoint:** `GET /health/templates/`

**Response (200 OK):**

```json
{
	"success": true,
	"response": [
		{
			"id": 1,
			"name": "Blood Pressure",
			"slug": "blood-pressure",
			"description": "Measure your systolic and diastolic blood pressure...",
			"icon": "heart-pulse",
			"category": "cardiovascular",
			"schema": {
				"systolic": {
					"type": "int",
					"unit": "mmHg",
					"min": 60,
					"max": 250,
					"required": true,
					"label": "Systolic (Upper)"
				},
				"diastolic": {
					"type": "int",
					"unit": "mmHg",
					"min": 40,
					"max": 150,
					"required": true,
					"label": "Diastolic (Lower)"
				},
				"pulse": {
					"type": "int",
					"unit": "bpm",
					"min": 30,
					"max": 220,
					"required": false,
					"label": "Pulse Rate"
				}
			},
			"normal_range": {
				"systolic": { "min": 90, "max": 120 },
				"diastolic": { "min": 60, "max": 80 }
			},
			"is_active": true
		}
	],
	"error": null
}
```

---

#### 2. Get Template Categories

Get all unique template categories.

**Endpoint:** `GET /health/templates/categories/`

**Response (200 OK):**

```json
{
	"success": true,
	"response": {
		"categories": [
			"cardiovascular",
			"metabolic",
			"thyroid",
			"body",
			"kidney",
			"liver",
			"blood",
			"vitamins"
		]
	},
	"error": null
}
```

---

#### 3. Get Template by ID

Get a specific template by its ID.

**Endpoint:** `GET /health/templates/{id}/`

**Response (200 OK):**

```json
{
  "success": true,
  "response": {
    "id": 1,
    "name": "Blood Pressure",
    "slug": "blood-pressure",
    "description": "Measure your systolic and diastolic blood pressure...",
    "icon": "heart-pulse",
    "category": "cardiovascular",
    "schema": {...},
    "normal_range": {...},
    "is_active": true
  },
  "error": null
}
```

**Error Response (404 Not Found):**

```json
{
	"success": false,
	"response": null,
	"error": {
		"status_code": 404,
		"message": "Template not found"
	}
}
```

---

#### 4. Get Template by Slug

Get a specific template by its slug.

**Endpoint:** `GET /health/templates/slug/{slug}/`

**Response (200 OK):**

```json
{
  "success": true,
  "response": {
    "id": 1,
    "name": "Blood Pressure",
    "slug": "blood-pressure",
    ...
  },
  "error": null
}
```

---

### Health Records

#### 5. List User's Health Records

Get all health records for the authenticated user.

**Endpoint:** `GET /health/records/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `template` | string | Filter by template slug |
| `start_date` | date | Filter from date (YYYY-MM-DD) |
| `end_date` | date | Filter until date (YYYY-MM-DD) |

**Example:** `GET /health/records/?template=blood-pressure&start_date=2025-01-01`

**Response (200 OK):**

```json
{
	"success": true,
	"response": [
		{
			"id": 1,
			"template": {
				"id": 1,
				"name": "Blood Pressure",
				"slug": "blood-pressure",
				"category": "cardiovascular",
				"icon": "heart-pulse"
			},
			"data": {
				"systolic": 120,
				"diastolic": 80,
				"pulse": 72
			},
			"recorded_at": "2025-06-14T10:30:00Z",
			"notes": "Morning reading after breakfast",
			"location": "Home",
			"created_at": "2025-06-14T10:35:00Z"
		}
	],
	"error": null
}
```

---

#### 6. Create Health Record

Create a new health record.

**Endpoint:** `POST /health/records/`

**Request Body:**

```json
{
	"template_slug": "blood-pressure",
	"data": {
		"systolic": 118,
		"diastolic": 78,
		"pulse": 70
	},
	"recorded_at": "2025-06-14T09:00:00Z",
	"notes": "Feeling good today",
	"location": "Home"
}
```

**Response (201 Created):**

```json
{
	"success": true,
	"response": {
		"id": 2,
		"template": {
			"id": 1,
			"name": "Blood Pressure",
			"slug": "blood-pressure",
			"category": "cardiovascular",
			"icon": "heart-pulse"
		},
		"data": {
			"systolic": 118,
			"diastolic": 78,
			"pulse": 70
		},
		"recorded_at": "2025-06-14T09:00:00Z",
		"notes": "Feeling good today",
		"location": "Home",
		"created_at": "2025-06-14T09:05:00Z"
	},
	"error": null
}
```

**Validation Errors (400 Bad Request):**

```json
{
	"success": false,
	"response": null,
	"error": {
		"status_code": 400,
		"message": "Missing required field: systolic"
	}
}
```

```json
{
	"success": false,
	"response": null,
	"error": {
		"status_code": 400,
		"message": "Field 'systolic' value 300 exceeds maximum 250"
	}
}
```

---

#### 7. Get Health Record Detail

Get a specific health record by ID.

**Endpoint:** `GET /health/records/{id}/`

**Response (200 OK):**

```json
{
  "success": true,
  "response": {
    "id": 1,
    "template": {
      "id": 1,
      "name": "Blood Pressure",
      "slug": "blood-pressure",
      "category": "cardiovascular",
      "icon": "heart-pulse",
      "schema": {...},
      "normal_range": {...}
    },
    "data": {
      "systolic": 120,
      "diastolic": 80,
      "pulse": 72
    },
    "recorded_at": "2025-06-14T10:30:00Z",
    "notes": "Morning reading",
    "location": "Home",
    "created_at": "2025-06-14T10:35:00Z",
    "updated_at": "2025-06-14T10:35:00Z"
  },
  "error": null
}
```

---

#### 8. Update Health Record

Update an existing health record.

**Endpoint:** `PUT /health/records/{id}/`

**Request Body:**

```json
{
	"data": {
		"systolic": 115,
		"diastolic": 75,
		"pulse": 68
	},
	"notes": "Updated reading",
	"location": "Clinic"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "response": {
    "id": 1,
    "template": {...},
    "data": {
      "systolic": 115,
      "diastolic": 75,
      "pulse": 68
    },
    "recorded_at": "2025-06-14T10:30:00Z",
    "notes": "Updated reading",
    "location": "Clinic",
    "updated_at": "2025-06-14T11:00:00Z"
  },
  "error": null
}
```

---

#### 9. Delete Health Record

Delete a health record.

**Endpoint:** `DELETE /health/records/{id}/`

**Response (200 OK):**

```json
{
	"success": true,
	"response": {
		"message": "Health record deleted successfully"
	},
	"error": null
}
```

---

#### 10. Get Latest Records

Get the most recent health record for each template.

**Endpoint:** `GET /health/records/latest/`

**Response (200 OK):**

```json
{
	"success": true,
	"response": [
		{
			"template_name": "Blood Pressure",
			"template_slug": "blood-pressure",
			"category": "cardiovascular",
			"icon": "heart-pulse",
			"latest_record": {
				"id": 5,
				"data": {
					"systolic": 118,
					"diastolic": 78
				},
				"recorded_at": "2025-06-14T10:30:00Z"
			}
		},
		{
			"template_name": "Blood Sugar",
			"template_slug": "blood-sugar",
			"category": "metabolic",
			"icon": "droplet",
			"latest_record": {
				"id": 3,
				"data": {
					"glucose": 95,
					"measurement_time": "fasting"
				},
				"recorded_at": "2025-06-14T07:00:00Z"
			}
		}
	],
	"error": null
}
```

---

#### 11. Get Records by Template

Get all records for a specific template.

**Endpoint:** `GET /health/records/template/{slug}/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Max records to return (default: 50) |
| `start_date` | date | Filter from date |
| `end_date` | date | Filter until date |

**Response (200 OK):**

```json
{
  "success": true,
  "response": {
    "template": {
      "id": 1,
      "name": "Blood Pressure",
      "slug": "blood-pressure",
      "category": "cardiovascular",
      "normal_range": {...}
    },
    "records": [
      {
        "id": 5,
        "data": {"systolic": 118, "diastolic": 78},
        "recorded_at": "2025-06-14T10:30:00Z",
        "notes": null
      },
      {
        "id": 4,
        "data": {"systolic": 122, "diastolic": 82},
        "recorded_at": "2025-06-13T10:30:00Z",
        "notes": null
      }
    ],
    "count": 2
  },
  "error": null
}
```

---

#### 12. Get Statistics for Template

Get statistical analysis for a specific health metric.

**Endpoint:** `GET /health/records/stats/{slug}/`

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `days` | integer | Number of days to analyze (default: 30) |

**Response (200 OK):**

```json
{
	"success": true,
	"response": {
		"template": {
			"name": "Blood Pressure",
			"slug": "blood-pressure"
		},
		"period_days": 30,
		"total_records": 15,
		"statistics": {
			"systolic": {
				"min": 110,
				"max": 135,
				"avg": 120.5,
				"latest": 118
			},
			"diastolic": {
				"min": 70,
				"max": 88,
				"avg": 78.2,
				"latest": 78
			},
			"pulse": {
				"min": 65,
				"max": 85,
				"avg": 72.3,
				"latest": 70
			}
		},
		"normal_range": {
			"systolic": { "min": 90, "max": 120 },
			"diastolic": { "min": 60, "max": 80 }
		}
	},
	"error": null
}
```

---

#### 13. Get Health Summary

Get a complete health summary with latest readings across all templates.

**Endpoint:** `GET /health/records/summary/`

**Response (200 OK):**

```json
{
	"success": true,
	"response": {
		"total_records": 45,
		"templates_tracked": 5,
		"categories": {
			"cardiovascular": {
				"templates": [
					"blood-pressure",
					"heart-rate",
					"oxygen-saturation"
				],
				"record_count": 20
			},
			"metabolic": {
				"templates": ["blood-sugar", "cholesterol"],
				"record_count": 15
			}
		},
		"latest_by_category": {
			"cardiovascular": {
				"blood-pressure": {
					"data": { "systolic": 118, "diastolic": 78 },
					"recorded_at": "2025-06-14T10:30:00Z"
				}
			},
			"metabolic": {
				"blood-sugar": {
					"data": { "glucose": 95, "measurement_time": "fasting" },
					"recorded_at": "2025-06-14T07:00:00Z"
				}
			}
		}
	},
	"error": null
}
```

---

## Predefined Templates

The app comes with predefined templates for common health metrics:

### Cardiovascular

| Template          | Fields                     | Units     |
| ----------------- | -------------------------- | --------- |
| Blood Pressure    | systolic, diastolic, pulse | mmHg, bpm |
| Heart Rate        | bpm, measurement_type      | bpm       |
| Oxygen Saturation | spo2, pulse                | %, bpm    |

### Metabolic

| Template    | Fields                         | Units |
| ----------- | ------------------------------ | ----- |
| Blood Sugar | glucose, measurement_time      | mg/dL |
| HbA1c       | hba1c                          | %     |
| Cholesterol | total, ldl, hdl, triglycerides | mg/dL |
| Uric Acid   | uric_acid                      | mg/dL |

### Thyroid

| Template      | Fields                        | Units               |
| ------------- | ----------------------------- | ------------------- |
| Thyroid Panel | tsh, t3, t4, free_t3, free_t4 | mIU/L, ng/dL, μg/dL |

### Body Metrics

| Template         | Fields                        | Units         |
| ---------------- | ----------------------------- | ------------- |
| Weight           | weight                        | kg            |
| Body Temperature | temperature, measurement_site | °C            |
| BMI              | weight, height, bmi           | kg, cm, kg/m² |

### Organ Function

| Template        | Fields                             | Units            |
| --------------- | ---------------------------------- | ---------------- |
| Kidney Function | creatinine, bun, egfr              | mg/dL, mL/min    |
| Liver Function  | alt, ast, bilirubin_total, albumin | U/L, mg/dL, g/dL |

### Blood & Vitamins

| Template     | Fields                     | Units        |
| ------------ | -------------------------- | ------------ |
| Hemoglobin   | hemoglobin                 | g/dL         |
| Vitamin D    | vitamin_d                  | ng/mL        |
| Vitamin B12  | vitamin_b12                | pg/mL        |
| Iron Studies | serum_iron, ferritin, tibc | μg/dL, ng/mL |

---

## Data Validation

When creating or updating health records, the following validations are performed:

1. **Required Fields**: All fields marked as `required: true` must be provided
2. **Type Validation**: Values must match the expected type (int, float, string, boolean)
3. **Range Validation**: Numeric values must be within `min` and `max` bounds
4. **Template Validation**: Template must exist and be active

### Validation Error Examples

**Missing required field:**

```json
{
	"success": false,
	"response": null,
	"error": {
		"status_code": 400,
		"message": "Missing required field: systolic"
	}
}
```

**Value out of range:**

```json
{
	"success": false,
	"response": null,
	"error": {
		"status_code": 400,
		"message": "Field 'systolic' value 300 exceeds maximum 250"
	}
}
```

**Invalid type:**

```json
{
	"success": false,
	"response": null,
	"error": {
		"status_code": 400,
		"message": "Field 'systolic' expected type int, got str"
	}
}
```

---

## Importing Templates (SQL)

If you need to import predefined templates directly into PostgreSQL:

```bash
# Using psql
psql -d your_database -f health_state/health_templates.sql

# Or using Django shell
python manage.py dbshell < health_state/health_templates.sql
```

The SQL file uses `ON CONFLICT ... DO UPDATE` to safely update existing templates without duplicates.

---

## Response Wrapper

All responses are wrapped by `ResponseWrapperMiddleware`:

```json
{
  "success": true | false,
  "response": <actual_data> | null,
  "error": null | {
    "status_code": <http_status>,
    "message": "<error_message>"
  }
}
```

---

## Error Codes

| Code | Description                                    |
| ---- | ---------------------------------------------- |
| 400  | Bad Request - Validation error, missing fields |
| 401  | Unauthorized - Missing or invalid token        |
| 403  | Forbidden - Not owner of the record            |
| 404  | Not Found - Template or record doesn't exist   |
| 500  | Server Error - Internal error                  |

---

## Quick Start Examples

### Track Blood Pressure

```bash
# Get the template
curl -X GET "http://localhost:8000/health/templates/slug/blood-pressure/" \
  -H "Authorization: Bearer <token>"

# Create a reading
curl -X POST "http://localhost:8000/health/records/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "template_slug": "blood-pressure",
    "data": {"systolic": 120, "diastolic": 80, "pulse": 72},
    "recorded_at": "2025-06-14T09:00:00Z",
    "notes": "Morning reading"
  }'

# Get statistics
curl -X GET "http://localhost:8000/health/records/stats/blood-pressure/?days=30" \
  -H "Authorization: Bearer <token>"
```

### Track Blood Sugar

```bash
# Create a fasting glucose reading
curl -X POST "http://localhost:8000/health/records/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "template_slug": "blood-sugar",
    "data": {"glucose": 95, "measurement_time": "fasting"},
    "recorded_at": "2025-06-14T07:00:00Z"
  }'
```

---

## Related Apps

- **[Medicines](../medicines/README.md)** - Track your medications
- **[Intake](../intake/README.md)** - Log medicine consumption
- **[Alarm](../alarm/README.md)** - Set medication reminders
