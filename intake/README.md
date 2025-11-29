# Intake App - MediGuard Backend

## Overview

The **Intake App** tracks medicine intake records for users. It records when medicines are scheduled to be taken, their actual intake status, and provides statistics on medication adherence.

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

## Endpoints Summary

| Method | Endpoint                     | Description                         |
| ------ | ---------------------------- | ----------------------------------- |
| GET    | `/intake/list/`              | List all intakes (with filters)     |
| POST   | `/intake/list/`              | Create a new intake record          |
| GET    | `/intake/today/`             | Get today's intakes                 |
| GET    | `/intake/medicine/<id>/`     | Get intakes for a specific medicine |
| POST   | `/intake/mark-taken/<id>/`   | Quick mark as taken                 |
| POST   | `/intake/mark-skipped/<id>/` | Quick mark as skipped               |
| POST   | `/intake/generate/`          | Bulk generate intake records        |
| GET    | `/intake/stats/`             | Get intake statistics               |
| GET    | `/intake/<id>/`              | Get specific intake                 |
| PUT    | `/intake/<id>/`              | Update an intake                    |
| PATCH  | `/intake/<id>/`              | Partial update an intake            |
| DELETE | `/intake/<id>/`              | Delete an intake                    |

---

## Endpoints

### 1. List All Intakes

Retrieves all intake records for the authenticated user with optional filtering.

| Property | Value           |
| -------- | --------------- |
| URL      | `/intake/list/` |
| Method   | `GET`           |
| Auth     | Required (JWT)  |

#### Query Parameters

| Parameter     | Type   | Description                                     |
| ------------- | ------ | ----------------------------------------------- |
| `date`        | string | Filter by specific date (YYYY-MM-DD)            |
| `start_date`  | string | Filter from date (YYYY-MM-DD)                   |
| `end_date`    | string | Filter to date (YYYY-MM-DD)                     |
| `medicine_id` | int    | Filter by specific medicine ID                  |
| `status`      | string | Filter by status (pending/taken/skipped/missed) |

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
			"scheduled_date": "2025-11-29",
			"scheduled_time": "08:00:00",
			"status": "taken",
			"taken_at": "2025-11-29T08:05:30Z",
			"notes": "Taken with breakfast",
			"is_late": true,
			"delay_minutes": 5,
			"created_at": "2025-11-28T20:00:00Z",
			"updated_at": "2025-11-29T08:05:30Z"
		}
	],
	"error": null
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

```json
{
	"medicine": 1,
	"scheduled_date": "2025-11-30",
	"scheduled_time": "08:00",
	"status": "pending",
	"notes": "Optional note"
}
```

#### Success Response (201 Created)

```json
{
	"success": true,
	"response": {
		"id": 2,
		"medicine": 1,
		"medicine_name": "Paracetamol",
		"medicine_dosage": 500,
		"medicine_amount": 2,
		"scheduled_date": "2025-11-30",
		"scheduled_time": "08:00:00",
		"status": "pending",
		"taken_at": null,
		"notes": "Optional note",
		"is_late": false,
		"delay_minutes": 0,
		"created_at": "2025-11-29T12:00:00Z",
		"updated_at": "2025-11-29T12:00:00Z"
	},
	"error": null
}
```

---

### 3. Get Today's Intakes

Quick endpoint to fetch all intakes scheduled for today.

| Property | Value            |
| -------- | ---------------- |
| URL      | `/intake/today/` |
| Method   | `GET`            |
| Auth     | Required (JWT)   |

#### Success Response (200 OK)

```json
{
    "success": true,
    "response": [
        {
            "id": 1,
            "medicine": 1,
            "medicine_name": "Paracetamol",
            "scheduled_date": "2025-11-29",
            "scheduled_time": "08:00:00",
            "status": "pending",
            ...
        },
        {
            "id": 2,
            "medicine": 1,
            "medicine_name": "Paracetamol",
            "scheduled_date": "2025-11-29",
            "scheduled_time": "20:00:00",
            "status": "pending",
            ...
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

#### Query Parameters

| Parameter    | Type   | Description                   |
| ------------ | ------ | ----------------------------- |
| `start_date` | string | Filter from date (YYYY-MM-DD) |
| `end_date`   | string | Filter to date (YYYY-MM-DD)   |

---

### 5. Mark Intake as Taken

Quick action to mark an intake as taken with current timestamp.

| Property | Value                      |
| -------- | -------------------------- |
| URL      | `/intake/mark-taken/<id>/` |
| Method   | `POST`                     |
| Auth     | Required (JWT)             |

#### Request Body (Optional)

```json
{
	"notes": "Taken with food"
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
        "taken_at": "2025-11-29T08:15:30Z",
        "is_late": true,
        "delay_minutes": 15,
        ...
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

#### Request Body (Optional)

```json
{
	"notes": "Feeling nauseous, doctor advised to skip"
}
```

---

### 7. Bulk Generate Intakes

Generate intake records for a date range based on medicine schedules.

| Property | Value               |
| -------- | ------------------- |
| URL      | `/intake/generate/` |
| Method   | `POST`              |
| Auth     | Required (JWT)      |

#### Request Body

```json
{
	"start_date": "2025-12-01",
	"end_date": "2025-12-07",
	"medicine_ids": [1, 2]
}
```

> **Note**: `medicine_ids` is optional. If omitted, generates for all user medicines.

#### Validation Rules

- `start_date` must be before or equal to `end_date`
- Date range cannot exceed **30 days**
- Existing intake records are skipped (not duplicated)

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

---

### 8. Get Intake Statistics

Get adherence statistics for the user's intakes.

| Property | Value            |
| -------- | ---------------- |
| URL      | `/intake/stats/` |
| Method   | `GET`            |
| Auth     | Required (JWT)   |

#### Query Parameters

| Parameter     | Type   | Description                   |
| ------------- | ------ | ----------------------------- |
| `start_date`  | string | Filter from date (YYYY-MM-DD) |
| `end_date`    | string | Filter to date (YYYY-MM-DD)   |
| `medicine_id` | int    | Filter by specific medicine   |

#### Success Response (200 OK)

```json
{
	"success": true,
	"response": {
		"total_intakes": 50,
		"taken_count": 40,
		"missed_count": 5,
		"skipped_count": 3,
		"pending_count": 2,
		"adherence_rate": 83.33,
		"on_time_count": 35,
		"late_count": 5
	},
	"error": null
}
```

#### Statistics Explanation

| Field            | Description                                   |
| ---------------- | --------------------------------------------- |
| `total_intakes`  | Total number of intake records                |
| `taken_count`    | Number of intakes marked as taken             |
| `missed_count`   | Number of intakes marked as missed            |
| `skipped_count`  | Number of intakes marked as skipped           |
| `pending_count`  | Number of pending intakes                     |
| `adherence_rate` | Percentage: `taken / (total - pending) * 100` |
| `on_time_count`  | Taken intakes that were on time               |
| `late_count`     | Taken intakes that were late                  |

---

### 9. Get Specific Intake

Retrieve a single intake record by ID.

| Property | Value           |
| -------- | --------------- |
| URL      | `/intake/<id>/` |
| Method   | `GET`           |
| Auth     | Required (JWT)  |

---

### 10. Update Intake

Update an intake record.

| Property | Value           |
| -------- | --------------- |
| URL      | `/intake/<id>/` |
| Method   | `PUT` / `PATCH` |
| Auth     | Required (JWT)  |

#### Request Body

```json
{
	"status": "taken",
	"taken_at": "2025-11-29T08:30:00Z",
	"notes": "Updated note"
}
```

---

### 11. Delete Intake

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

### Intake Fields

| Field            | Type     | Description                                    |
| ---------------- | -------- | ---------------------------------------------- |
| `id`             | int      | Unique identifier (auto-generated)             |
| `user`           | FK       | Reference to User                              |
| `medicine`       | FK       | Reference to Medicine                          |
| `scheduled_date` | date     | Date when medicine is scheduled                |
| `scheduled_time` | time     | Time when medicine is scheduled (HH:MM)        |
| `status`         | string   | pending / taken / skipped / missed             |
| `taken_at`       | datetime | Actual datetime when taken (null if not taken) |
| `notes`          | text     | Optional user notes                            |
| `created_at`     | datetime | Record creation timestamp                      |
| `updated_at`     | datetime | Last update timestamp                          |

### Computed Fields (Read-Only)

| Field             | Type    | Description                              |
| ----------------- | ------- | ---------------------------------------- |
| `medicine_name`   | string  | Name of the associated medicine          |
| `medicine_dosage` | int     | Dosage of the medicine                   |
| `medicine_amount` | int     | Amount/units of the medicine             |
| `is_late`         | boolean | Whether medicine was taken late          |
| `delay_minutes`   | int     | Minutes late (0 if on time or not taken) |

---

## Status Values

| Status    | Description                                     |
| --------- | ----------------------------------------------- |
| `pending` | Scheduled but not yet time for intake           |
| `taken`   | User marked the medicine as taken               |
| `skipped` | User intentionally skipped this intake          |
| `missed`  | Time passed without taking (system/user marked) |

---

## Error Responses

### 400 Bad Request

```json
{
    "success": false,
    "response": null,
    "error": {
        "message": "Invalid date format. Use YYYY-MM-DD",
        "details": { ... }
    }
}
```

### 401 Unauthorized

```json
{
    "success": false,
    "response": null,
    "error": {
        "message": "Authentication credentials were not provided.",
        "details": { ... }
    }
}
```

### 404 Not Found

```json
{
    "success": false,
    "response": null,
    "error": {
        "message": "Intake not found",
        "details": { ... }
    }
}
```

---

## Example Usage (cURL)

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

### Get Statistics for Last Month

```bash
curl -X GET "http://localhost:8000/intake/stats/?start_date=2025-11-01&end_date=2025-11-30" \
  -H "Authorization: Bearer <token>"
```

---

## Workflow

### Typical Usage Flow

1. **Generate Intakes**: Use `/intake/generate/` to create intake records for upcoming days
2. **View Today's Intakes**: Use `/intake/today/` to see what medicines are scheduled
3. **Mark as Taken/Skipped**: Use quick actions when user takes or skips medicine
4. **View Statistics**: Use `/intake/stats/` to see adherence reports

---

## File Structure

```
intake/
├── __init__.py
├── admin.py           # Admin panel configuration
├── apps.py
├── models.py          # Intake model definition
├── serializers.py     # DRF serializers
├── tests.py
├── urls.py            # URL routing
├── views.py           # API views
├── README.md          # This file
└── migrations/
    └── __init__.py
```

---

## Related Apps

- **Medicines App** (`/medicine/`) - Manage medicines (source of intake schedules)
- **Alarm App** (`/alarm/`) - View medicine alarm schedules
- **Accounts App** (`/accounts/`) - User authentication
