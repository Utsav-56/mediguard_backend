# Alarm App - MediGuard Backend

## Overview

The **Alarm App** is a **read-only** API that provides alarm/schedule data derived from the user's medicines. It does not store its own data — instead, it dynamically generates alarm information based on the `Medicines` model.

> **Important**: Alarms cannot be created, updated, or deleted directly. To modify alarms, users must manage their medicines through the `/medicines/` endpoints.

---

## Base URL

```
/alarm/
```

---

## Authentication

All endpoints require **JWT Authentication**.

| Header          | Value                   |
| --------------- | ----------------------- |
| `Authorization` | `Bearer <access_token>` |

---

## Endpoints

### 1. List All Alarms

Retrieves all alarms for the authenticated user based on their medicines.

| Property | Value          |
| -------- | -------------- |
| URL      | `/alarm/list/` |
| Method   | `GET`          |
| Auth     | Required (JWT) |

#### Success Response (200 OK)

```json
{
	"success": true,
	"response": {
		"1": {
			"name": "Paracetamol",
			"days_of_week": [1, 2, 3, 4, 5, 6, 7],
			"time": ["08:00", "20:00"]
		},
		"2": {
			"name": "Vitamin D",
			"days_of_week": [1, 3, 5],
			"time": ["09:00"]
		}
	},
	"error": null
}
```

#### Response Fields

| Field                        | Type     | Description                                                                    |
| ---------------------------- | -------- | ------------------------------------------------------------------------------ |
| `<medicine_id>`              | `object` | Key is the medicine ID as a string                                             |
| `<medicine_id>.name`         | `string` | Name of the medicine                                                           |
| `<medicine_id>.days_of_week` | `array`  | Days when alarm should trigger (1=Sunday, 2=Monday, ..., 7=Saturday)           |
| `<medicine_id>.time`         | `array`  | Times when alarm should trigger in 24-hour format (e.g., `["08:00", "20:00"]`) |

#### Empty Response (No Medicines)

```json
{
	"success": true,
	"response": {},
	"error": null
}
```

#### Unauthorized Response (401)

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Authentication credentials were not provided.",
		"details": {
			"detail": "Authentication credentials were not provided."
		}
	}
}
```

---

### 2. Create Alarm (Not Allowed)

| Property | Value          |
| -------- | -------------- |
| URL      | `/alarm/list/` |
| Method   | `POST`         |
| Auth     | Required (JWT) |

#### Response (405 Method Not Allowed)

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "POST method not allowed. Alarms are generated from medicines.",
		"details": {
			"detail": "POST method not allowed. Alarms are generated from medicines."
		}
	}
}
```

---

### 3. Update Alarm (Not Allowed)

| Property | Value           |
| -------- | --------------- |
| URL      | `/alarm/<id>/`  |
| Method   | `PUT` / `PATCH` |
| Auth     | Required (JWT)  |

#### Response (405 Method Not Allowed)

**PUT:**

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "PUT method not allowed. Edit medicines to update alarms.",
		"details": {
			"detail": "PUT method not allowed. Edit medicines to update alarms."
		}
	}
}
```

**PATCH:**

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "PATCH method not allowed. Edit medicines to update alarms.",
		"details": {
			"detail": "PATCH method not allowed. Edit medicines to update alarms."
		}
	}
}
```

---

### 4. Delete Alarm (Not Allowed)

| Property | Value          |
| -------- | -------------- |
| URL      | `/alarm/<id>/` |
| Method   | `DELETE`       |
| Auth     | Required (JWT) |

#### Response (405 Method Not Allowed)

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "DELETE method not allowed. Delete medicines to remove alarms.",
		"details": {
			"detail": "DELETE method not allowed. Delete medicines to remove alarms."
		}
	}
}
```

---

## Response Wrapper Format

All responses are automatically wrapped by `ResponseWrapperMiddleware` in the following structure:

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

## Days of Week Mapping

| Value | Day       |
| ----- | --------- |
| 1     | Sunday    |
| 2     | Monday    |
| 3     | Tuesday   |
| 4     | Wednesday |
| 5     | Thursday  |
| 6     | Friday    |
| 7     | Saturday  |

---

## Time Format

- Times are stored and returned in **24-hour format**
- Format: `HH:MM` (e.g., `"08:00"`, `"14:30"`, `"20:00"`)

---

## How to Manage Alarms

Since alarms are derived from medicines, to manage alarms:

| Action              | How to Do It                                         |
| ------------------- | ---------------------------------------------------- |
| **Add an alarm**    | Create a new medicine via `POST /medicines/`         |
| **Edit an alarm**   | Update the medicine via `PUT/PATCH /medicines/<id>/` |
| **Delete an alarm** | Delete the medicine via `DELETE /medicines/<id>/`    |

---

## Error Codes Summary

| HTTP Code | Meaning               | When It Occurs                    |
| --------- | --------------------- | --------------------------------- |
| `200`     | OK                    | Successful GET request            |
| `401`     | Unauthorized          | Missing or invalid JWT token      |
| `405`     | Method Not Allowed    | POST, PUT, PATCH, DELETE requests |
| `500`     | Internal Server Error | Unexpected server error           |

---

## Example Usage (cURL)

### Get All Alarms

```bash
curl -X GET "http://localhost:8000/alarm/list/" \
  -H "Authorization: Bearer <your_access_token>"
```

### Attempting POST (Will Fail)

```bash
curl -X POST "http://localhost:8000/alarm/list/" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test"}'
```

---

## Data Source

Alarms are generated from the `Medicines` model with the following fields mapped:

| Alarm Field    | Medicine Field | Description                          |
| -------------- | -------------- | ------------------------------------ |
| `name`         | `name`         | Medicine name                        |
| `days_of_week` | `days_of_week` | JSON array of day numbers (1-7)      |
| `time`         | `time`         | JSON array of time strings ("HH:MM") |

---

## Related Apps

- **Medicines App** (`/medicines/`) - Manage medicines (which controls alarms)
- **Accounts App** (`/accounts/`) - User authentication

---

## File Structure

```
alarm/
├── __init__.py
├── admin.py
├── apps.py
├── models.py          # Empty (uses Medicines model)
├── tests.py
├── urls.py            # URL routing
├── views.py           # API views
├── README.md          # This file
└── migrations/
    └── __init__.py
```
