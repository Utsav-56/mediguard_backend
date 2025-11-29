# Intake App - MediGuard Backend

## Overview

The **Intake App** is the medication tracking system for MediGuard. It records and manages medicine intake events, allowing users to track when they take their medicines, monitor adherence, and view statistics about their medication habits.

### What is an Intake?

An **Intake** represents a single scheduled instance of taking a medicine. For example, if a user has "Paracetamol" scheduled at 8:00 AM and 8:00 PM daily, each of these scheduled times creates a separate intake record that can be marked as:

- **Pending** - Scheduled but not yet time
- **Taken** - User confirmed they took the medicine
- **Skipped** - User intentionally skipped this dose
- **Missed** - Time passed without taking the medicine

---

## Base URL

```
/intake/
```

---

## Authentication

All endpoints require **JWT Authentication**.

| Header          | Value                   |
| --------------- | ----------------------- |
| `Authorization` | `Bearer <access_token>` |

---

## Response Wrapper

All responses are automatically wrapped by `ResponseWrapperMiddleware`:

### Success Response Structure

```json
{
	"success": true,
	"response": {
		/* actual data */
	},
	"error": null
}
```

### Error Response Structure

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Error description",
		"details": {
			/* additional error info */
		}
	}
}
```

---

## Endpoints Summary

| Method | Endpoint                     | Description                             |
| ------ | ---------------------------- | --------------------------------------- |
| GET    | `/intake/list/`              | List all intakes with optional filters  |
| POST   | `/intake/list/`              | Create a new intake record              |
| GET    | `/intake/today/`             | Get all intakes scheduled for today     |
| GET    | `/intake/medicine/<id>/`     | Get all intakes for a specific medicine |
| POST   | `/intake/mark-taken/<id>/`   | Quick action: mark intake as taken      |
| POST   | `/intake/mark-skipped/<id>/` | Quick action: mark intake as skipped    |
| POST   | `/intake/generate/`          | Bulk generate intake records for dates  |
| GET    | `/intake/stats/`             | Get adherence statistics                |
| GET    | `/intake/<id>/`              | Get a specific intake record            |
| PUT    | `/intake/<id>/`              | Full update an intake record            |
| PATCH  | `/intake/<id>/`              | Partial update an intake record         |
| DELETE | `/intake/<id>/`              | Delete an intake record                 |

---

## Endpoints Detail

---

### 1. List All Intakes

Retrieves all intake records for the authenticated user with optional filtering.

| Property | Value           |
| -------- | --------------- |
| URL      | `/intake/list/` |
| Method   | `GET`           |
| Auth     | Required (JWT)  |

#### Query Parameters

| Parameter     | Type   | Required | Description                                               |
| ------------- | ------ | -------- | --------------------------------------------------------- |
| `date`        | string | No       | Filter by specific date (format: `YYYY-MM-DD`)            |
| `start_date`  | string | No       | Filter from date (format: `YYYY-MM-DD`)                   |
| `end_date`    | string | No       | Filter to date (format: `YYYY-MM-DD`)                     |
| `medicine_id` | int    | No       | Filter by specific medicine ID                            |
| `status`      | string | No       | Filter by status: `pending`, `taken`, `skipped`, `missed` |

#### Example Request

```bash
GET /intake/list/?date=2025-11-30&status=pending
Authorization: Bearer <token>
```

#### Success Response (200 OK)

```json
{
	"success": true,
	"response": [
		{
			"id": 1,
			"medicine": 1,
			"medicine_name": "Paracetamol",
			"medicine_dosage": 500,
			"medicine_amount": 2,
			"scheduled_date": "2025-11-30",
			"scheduled_time": "08:00:00",
			"status": "pending",
			"taken_at": null,
			"notes": null,
			"is_late": false,
			"delay_minutes": 0,
			"created_at": "2025-11-29T20:00:00Z",
			"updated_at": "2025-11-29T20:00:00Z"
		},
		{
			"id": 2,
			"medicine": 1,
			"medicine_name": "Paracetamol",
			"medicine_dosage": 500,
			"medicine_amount": 2,
			"scheduled_date": "2025-11-30",
			"scheduled_time": "20:00:00",
			"status": "pending",
			"taken_at": null,
			"notes": null,
			"is_late": false,
			"delay_minutes": 0,
			"created_at": "2025-11-29T20:00:00Z",
			"updated_at": "2025-11-29T20:00:00Z"
		}
	],
	"error": null
}
```

#### Error Response (400 Bad Request)

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Invalid date format. Use YYYY-MM-DD",
		"details": {
			"detail": "Invalid date format. Use YYYY-MM-DD"
		}
	}
}
```

---

### 2. Create Intake Record

Create a new intake record manually.

| Property | Value           |
| -------- | --------------- |
| URL      | `/intake/list/` |
| Method   | `POST`          |
| Auth     | Required (JWT)  |

#### Request Body

| Field            | Type   | Required | Description                            |
| ---------------- | ------ | -------- | -------------------------------------- |
| `medicine`       | int    | Yes      | ID of the medicine                     |
| `scheduled_date` | string | Yes      | Date for intake (format: `YYYY-MM-DD`) |
| `scheduled_time` | string | Yes      | Time for intake (format: `HH:MM`)      |
| `status`         | string | No       | Status (default: `pending`)            |
| `taken_at`       | string | No       | Actual datetime taken (ISO 8601)       |
| `notes`          | string | No       | Optional notes                         |

#### Example Request

```json
{
	"medicine": 1,
	"scheduled_date": "2025-12-01",
	"scheduled_time": "08:00",
	"status": "pending",
	"notes": "Take with food"
}
```

#### Success Response (201 Created)

```json
{
	"success": true,
	"response": {
		"id": 3,
		"medicine": 1,
		"medicine_name": "Paracetamol",
		"medicine_dosage": 500,
		"medicine_amount": 2,
		"scheduled_date": "2025-12-01",
		"scheduled_time": "08:00:00",
		"status": "pending",
		"taken_at": null,
		"notes": "Take with food",
		"is_late": false,
		"delay_minutes": 0,
		"created_at": "2025-11-30T10:00:00Z",
		"updated_at": "2025-11-30T10:00:00Z"
	},
	"error": null
}
```

#### Error Response (400 Bad Request)

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "You can only create intakes for your own medicines.",
		"details": {
			"medicine": ["You can only create intakes for your own medicines."]
		}
	}
}
```

---

### 3. Get Today's Intakes

Quickly fetch all intakes scheduled for today.

| Property | Value            |
| -------- | ---------------- |
| URL      | `/intake/today/` |
| Method   | `GET`            |
| Auth     | Required (JWT)   |

#### Example Request

```bash
GET /intake/today/
Authorization: Bearer <token>
```

#### Success Response (200 OK)

```json
{
	"success": true,
	"response": [
		{
			"id": 1,
			"medicine": 1,
			"medicine_name": "Paracetamol",
			"medicine_dosage": 500,
			"medicine_amount": 2,
			"scheduled_date": "2025-11-30",
			"scheduled_time": "08:00:00",
			"status": "taken",
			"taken_at": "2025-11-30T08:05:00Z",
			"notes": "Taken with breakfast",
			"is_late": true,
			"delay_minutes": 5,
			"created_at": "2025-11-29T20:00:00Z",
			"updated_at": "2025-11-30T08:05:00Z"
		},
		{
			"id": 2,
			"medicine": 1,
			"medicine_name": "Paracetamol",
			"medicine_dosage": 500,
			"medicine_amount": 2,
			"scheduled_date": "2025-11-30",
			"scheduled_time": "20:00:00",
			"status": "pending",
			"taken_at": null,
			"notes": null,
			"is_late": false,
			"delay_minutes": 0,
			"created_at": "2025-11-29T20:00:00Z",
			"updated_at": "2025-11-29T20:00:00Z"
		}
	],
	"error": null
}
```

---

### 4. Get Intakes by Medicine

Fetch all intake records for a specific medicine.

| Property | Value                             |
| -------- | --------------------------------- |
| URL      | `/intake/medicine/<medicine_id>/` |
| Method   | `GET`                             |
| Auth     | Required (JWT)                    |

#### URL Parameters

| Parameter     | Type | Description        |
| ------------- | ---- | ------------------ |
| `medicine_id` | int  | ID of the medicine |

#### Query Parameters

| Parameter    | Type   | Required | Description                             |
| ------------ | ------ | -------- | --------------------------------------- |
| `start_date` | string | No       | Filter from date (format: `YYYY-MM-DD`) |
| `end_date`   | string | No       | Filter to date (format: `YYYY-MM-DD`)   |

#### Example Request

```bash
GET /intake/medicine/1/?start_date=2025-11-01&end_date=2025-11-30
Authorization: Bearer <token>
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "response": [
        {
            "id": 1,
            "medicine": 1,
            "medicine_name": "Paracetamol",
            "scheduled_date": "2025-11-30",
            "scheduled_time": "08:00:00",
            "status": "taken",
            ...
        }
    ],
    "error": null
}
```

#### Error Response (404 Not Found)

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Medicine not found",
		"details": {
			"detail": "Medicine not found"
		}
	}
}
```

---

### 5. Mark Intake as Taken

Quick action to mark an intake as taken with the current timestamp.

| Property | Value                      |
| -------- | -------------------------- |
| URL      | `/intake/mark-taken/<id>/` |
| Method   | `POST`                     |
| Auth     | Required (JWT)             |

#### URL Parameters

| Parameter | Type | Description      |
| --------- | ---- | ---------------- |
| `id`      | int  | ID of the intake |

#### Request Body (Optional)

| Field   | Type   | Required | Description                     |
| ------- | ------ | -------- | ------------------------------- |
| `notes` | string | No       | Optional notes about the intake |

#### Example Request

```json
{
	"notes": "Taken with breakfast"
}
```

#### Success Response (200 OK)

```json
{
	"success": true,
	"response": {
		"id": 1,
		"medicine": 1,
		"medicine_name": "Paracetamol",
		"medicine_dosage": 500,
		"medicine_amount": 2,
		"scheduled_date": "2025-11-30",
		"scheduled_time": "08:00:00",
		"status": "taken",
		"taken_at": "2025-11-30T08:15:30Z",
		"notes": "Taken with breakfast",
		"is_late": true,
		"delay_minutes": 15,
		"created_at": "2025-11-29T20:00:00Z",
		"updated_at": "2025-11-30T08:15:30Z"
	},
	"error": null
}
```

---

### 6. Mark Intake as Skipped

Quick action to mark an intake as skipped.

| Property | Value                        |
| -------- | ---------------------------- |
| URL      | `/intake/mark-skipped/<id>/` |
| Method   | `POST`                       |
| Auth     | Required (JWT)               |

#### URL Parameters

| Parameter | Type | Description      |
| --------- | ---- | ---------------- |
| `id`      | int  | ID of the intake |

#### Request Body (Optional)

| Field   | Type   | Required | Description                       |
| ------- | ------ | -------- | --------------------------------- |
| `notes` | string | No       | Reason for skipping (recommended) |

#### Example Request

```json
{
	"notes": "Feeling nauseous, doctor advised to skip"
}
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "response": {
        "id": 1,
        "medicine": 1,
        "medicine_name": "Paracetamol",
        "scheduled_date": "2025-11-30",
        "scheduled_time": "08:00:00",
        "status": "skipped",
        "taken_at": null,
        "notes": "Feeling nauseous, doctor advised to skip",
        "is_late": false,
        "delay_minutes": 0,
        ...
    },
    "error": null
}
```

---

### 7. Bulk Generate Intakes

Generate intake records for a date range based on medicine schedules. This is useful for pre-populating intake records for upcoming days.

| Property | Value               |
| -------- | ------------------- |
| URL      | `/intake/generate/` |
| Method   | `POST`              |
| Auth     | Required (JWT)      |

#### Request Body

| Field          | Type       | Required | Description                                                 |
| -------------- | ---------- | -------- | ----------------------------------------------------------- |
| `start_date`   | string     | Yes      | Start date (format: `YYYY-MM-DD`)                           |
| `end_date`     | string     | Yes      | End date (format: `YYYY-MM-DD`)                             |
| `medicine_ids` | array[int] | No       | List of medicine IDs. If empty, generates for all medicines |

#### Validation Rules

- `start_date` must be before or equal to `end_date`
- Date range cannot exceed **30 days**
- Existing intake records are skipped (no duplicates created)
- Respects medicine's `days_of_week` schedule
- Respects medicine's `start_date` and `end_date` if set

#### Example Request

```json
{
	"start_date": "2025-12-01",
	"end_date": "2025-12-07",
	"medicine_ids": [1, 2]
}
```

#### Success Response (201 Created)

```json
{
	"success": true,
	"response": {
		"detail": "Intakes generated successfully",
		"created": 14,
		"skipped_existing": 2
	},
	"error": null
}
```

#### Error Response (400 Bad Request)

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Date range cannot exceed 30 days",
		"details": {
			"non_field_errors": ["Date range cannot exceed 30 days"]
		}
	}
}
```

---

### 8. Get Intake Statistics

Get adherence statistics for the user's medication intake.

| Property | Value            |
| -------- | ---------------- |
| URL      | `/intake/stats/` |
| Method   | `GET`            |
| Auth     | Required (JWT)   |

#### Query Parameters

| Parameter     | Type   | Required | Description                             |
| ------------- | ------ | -------- | --------------------------------------- |
| `start_date`  | string | No       | Filter from date (format: `YYYY-MM-DD`) |
| `end_date`    | string | No       | Filter to date (format: `YYYY-MM-DD`)   |
| `medicine_id` | int    | No       | Filter by specific medicine ID          |

#### Example Request

```bash
GET /intake/stats/?start_date=2025-11-01&end_date=2025-11-30
Authorization: Bearer <token>
```

#### Success Response (200 OK)

```json
{
	"success": true,
	"response": {
		"total_intakes": 60,
		"taken_count": 50,
		"missed_count": 5,
		"skipped_count": 3,
		"pending_count": 2,
		"adherence_rate": 86.21,
		"on_time_count": 45,
		"late_count": 5
	},
	"error": null
}
```

#### Statistics Explanation

| Field            | Type  | Description                                     |
| ---------------- | ----- | ----------------------------------------------- |
| `total_intakes`  | int   | Total number of intake records                  |
| `taken_count`    | int   | Number of intakes marked as "taken"             |
| `missed_count`   | int   | Number of intakes marked as "missed"            |
| `skipped_count`  | int   | Number of intakes marked as "skipped"           |
| `pending_count`  | int   | Number of intakes still "pending"               |
| `adherence_rate` | float | Percentage: `(taken / (total - pending)) * 100` |
| `on_time_count`  | int   | Number of taken intakes that were on time       |
| `late_count`     | int   | Number of taken intakes that were late          |

---

### 9. Get Specific Intake

Retrieve a single intake record by ID.

| Property | Value           |
| -------- | --------------- |
| URL      | `/intake/<id>/` |
| Method   | `GET`           |
| Auth     | Required (JWT)  |

#### URL Parameters

| Parameter | Type | Description      |
| --------- | ---- | ---------------- |
| `id`      | int  | ID of the intake |

#### Success Response (200 OK)

```json
{
	"success": true,
	"response": {
		"id": 1,
		"medicine": 1,
		"medicine_name": "Paracetamol",
		"medicine_dosage": 500,
		"medicine_amount": 2,
		"scheduled_date": "2025-11-30",
		"scheduled_time": "08:00:00",
		"status": "taken",
		"taken_at": "2025-11-30T08:05:00Z",
		"notes": "Taken with breakfast",
		"is_late": true,
		"delay_minutes": 5,
		"created_at": "2025-11-29T20:00:00Z",
		"updated_at": "2025-11-30T08:05:00Z"
	},
	"error": null
}
```

#### Error Response (404 Not Found)

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Intake not found",
		"details": {
			"detail": "Intake not found"
		}
	}
}
```

---

### 10. Update Intake (Full)

Full update of an intake record.

| Property | Value           |
| -------- | --------------- |
| URL      | `/intake/<id>/` |
| Method   | `PUT`           |
| Auth     | Required (JWT)  |

#### Request Body

| Field      | Type   | Required | Description                                      |
| ---------- | ------ | -------- | ------------------------------------------------ |
| `status`   | string | Yes      | Status: `pending`, `taken`, `skipped`, `missed`  |
| `taken_at` | string | No       | Actual datetime taken (auto-set if status=taken) |
| `notes`    | string | No       | Optional notes                                   |

#### Example Request

```json
{
	"status": "taken",
	"notes": "Taken 15 minutes late"
}
```

#### Success Response (200 OK)

```json
{
    "success": true,
    "response": {
        "id": 1,
        "medicine": 1,
        "medicine_name": "Paracetamol",
        "status": "taken",
        "taken_at": "2025-11-30T08:15:00Z",
        "notes": "Taken 15 minutes late",
        ...
    },
    "error": null
}
```

---

### 11. Update Intake (Partial)

Partial update of an intake record.

| Property | Value           |
| -------- | --------------- |
| URL      | `/intake/<id>/` |
| Method   | `PATCH`         |
| Auth     | Required (JWT)  |

#### Request Body

Only include fields you want to update:

```json
{
	"notes": "Added a note"
}
```

#### Success Response (200 OK)

Same as PUT response.

---

### 12. Delete Intake

Delete an intake record.

| Property | Value           |
| -------- | --------------- |
| URL      | `/intake/<id>/` |
| Method   | `DELETE`        |
| Auth     | Required (JWT)  |

#### Success Response (200 OK)

```json
{
	"success": true,
	"response": {
		"detail": "Intake deleted successfully"
	},
	"error": null
}
```

---

## Data Model

### Intake Model Fields

| Field            | Type     | Description                                    |
| ---------------- | -------- | ---------------------------------------------- |
| `id`             | int      | Unique identifier (auto-generated)             |
| `user`           | FK       | Reference to User (auto-set from JWT)          |
| `medicine`       | FK       | Reference to Medicine                          |
| `scheduled_date` | date     | Date when medicine is scheduled                |
| `scheduled_time` | time     | Time when medicine is scheduled (HH:MM:SS)     |
| `status`         | string   | `pending` / `taken` / `skipped` / `missed`     |
| `taken_at`       | datetime | Actual datetime when taken (null if not taken) |
| `notes`          | text     | Optional user notes                            |
| `created_at`     | datetime | Record creation timestamp                      |
| `updated_at`     | datetime | Last update timestamp                          |

### Computed Fields (Read-Only)

| Field             | Type    | Description                                     |
| ----------------- | ------- | ----------------------------------------------- |
| `medicine_name`   | string  | Name of the associated medicine                 |
| `medicine_dosage` | int     | Dosage of the medicine (e.g., 500 for 500mg)    |
| `medicine_amount` | int     | Amount/units to take (e.g., 2 tablets)          |
| `is_late`         | boolean | Whether medicine was taken after scheduled time |
| `delay_minutes`   | int     | Minutes late (0 if on time or not taken)        |

---

## Status Values

| Status    | Description                                     | `taken_at` |
| --------- | ----------------------------------------------- | ---------- |
| `pending` | Scheduled but not yet time for intake           | `null`     |
| `taken`   | User confirmed they took the medicine           | Auto-set   |
| `skipped` | User intentionally skipped this dose            | `null`     |
| `missed`  | Time passed without taking (system/user marked) | `null`     |

---

## Typical Workflow

### 1. Setup: Generate Intakes for the Week

```bash
POST /intake/generate/
{
    "start_date": "2025-12-01",
    "end_date": "2025-12-07"
}
```

### 2. Daily: Check Today's Intakes

```bash
GET /intake/today/
```

### 3. User Action: Mark as Taken

```bash
POST /intake/mark-taken/1/
{
    "notes": "Taken with lunch"
}
```

### 4. Weekly: Check Adherence Stats

```bash
GET /intake/stats/?start_date=2025-11-24&end_date=2025-11-30
```

---

## Error Codes Summary

| HTTP Code | Meaning               | When It Occurs                     |
| --------- | --------------------- | ---------------------------------- |
| `200`     | OK                    | Successful GET, PUT, PATCH, DELETE |
| `201`     | Created               | Successful POST                    |
| `400`     | Bad Request           | Invalid data or validation error   |
| `401`     | Unauthorized          | Missing or invalid JWT token       |
| `404`     | Not Found             | Intake or medicine not found       |
| `500`     | Internal Server Error | Unexpected server error            |

---

## cURL Examples

### Get Today's Intakes

```bash
curl -X GET "http://localhost:8000/intake/today/" \
  -H "Authorization: Bearer <token>"
```

### Mark as Taken

```bash
curl -X POST "http://localhost:8000/intake/mark-taken/1/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Taken with breakfast"}'
```

### Generate Weekly Intakes

```bash
curl -X POST "http://localhost:8000/intake/generate/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"start_date": "2025-12-01", "end_date": "2025-12-07"}'
```

### Get Statistics

```bash
curl -X GET "http://localhost:8000/intake/stats/?start_date=2025-11-01&end_date=2025-11-30" \
  -H "Authorization: Bearer <token>"
```

### List with Filters

```bash
curl -X GET "http://localhost:8000/intake/list/?status=pending&medicine_id=1" \
  -H "Authorization: Bearer <token>"
```

---

## File Structure

```
intake/
├── __init__.py
├── admin.py           # Admin panel configuration
├── apps.py            # App configuration
├── models.py          # Intake model definition
├── serializers.py     # DRF serializers
├── tests.py           # Unit tests
├── urls.py            # URL routing
├── views.py           # API views
├── README.md          # This documentation
└── migrations/
    ├── __init__.py
    └── 0001_initial.py
```

---

## Related Apps

| App       | Base URL     | Description                            |
| --------- | ------------ | -------------------------------------- |
| Medicines | `/medicine/` | Manage medicines (source of schedules) |
| Alarm     | `/alarm/`    | View medicine alarm schedules          |
| Accounts  | `/auth/`     | User authentication (JWT)              |

---

## Notes

1. **Unique Constraint**: Each combination of `user + medicine + scheduled_date + scheduled_time` must be unique. Attempting to create duplicates will fail.

2. **Auto `taken_at`**: When marking status as `taken`, if `taken_at` is not provided, it automatically sets to the current datetime.

3. **Clear `taken_at`**: When changing status to `pending`, `skipped`, or `missed`, `taken_at` is automatically cleared to `null`.

4. **Days of Week**: The generate endpoint respects the medicine's `days_of_week` setting (1=Sunday, 7=Saturday).

5. **Date Range Limit**: The generate endpoint limits date ranges to 30 days to prevent abuse.
