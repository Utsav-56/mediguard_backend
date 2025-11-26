# Medicines App API Documentation

## Overview

The Medicines app provides a complete REST API for managing medicine schedules in the MediGuard system. Users can create, read, update, and delete their medicine records, including scheduling information such as dosage, timing, and frequency.

---

## Table of Contents

- [Response Structure](#response-structure)
- [Authentication](#authentication)
- [API Endpoints](#api-endpoints)
- [Data Models](#data-models)
- [Request & Response Examples](#request--response-examples)
- [Error Handling](#error-handling)
- [Field Validations](#field-validations)

---

## Response Structure

All API responses are wrapped in a consistent structure by the `ResponseWrapperMiddleware`. This ensures uniform handling of both success and error cases.

### Success Response Format

```json
{
	"success": true,
	"response": {
		// Your actual data here
	},
	"error": null
}
```

### Error Response Format

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Error message here",
		"details": {
			// Additional error details
		}
	}
}
```

### Response Fields

| Field           | Type              | Description                                              |
| --------------- | ----------------- | -------------------------------------------------------- |
| `success`       | Boolean           | `true` for 2xx status codes, `false` for errors          |
| `response`      | Object/Array/null | Contains the actual data on success, `null` on error     |
| `error`         | Object/null       | Contains error information on failure, `null` on success |
| `error.message` | String            | Human-readable error message                             |
| `error.details` | Object            | Detailed error information (validation errors, etc.)     |

---

## Authentication

All endpoints require authentication using Token-based authentication.

**Header Required:**

```
Authorization: Token YOUR_AUTH_TOKEN_HERE
```

**Unauthorized Response (401):**

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Auth token is needed for this endpoint (invalid request)",
		"details": {
			"detail": "Auth token is needed for this endpoint (invalid request)"
		}
	}
}
```

---

## API Endpoints

### Base URL

```
/medicines/
```

### Endpoint Summary

| Method | Endpoint                  | Description                                   |
| ------ | ------------------------- | --------------------------------------------- |
| GET    | `/medicines/list/`        | Retrieve all medicines for authenticated user |
| POST   | `/medicines/list/`        | Create a new medicine (alternative)           |
| POST   | `/medicines/add/`         | Create a new medicine                         |
| GET    | `/medicines/detail/<id>/` | Retrieve specific medicine details            |
| POST   | `/medicines/detail/<id>/` | Update specific medicine (alternative)        |
| PATCH  | `/medicines/update/<id>/` | Partially update specific medicine            |
| PUT    | `/medicines/update/<id>/` | Fully update specific medicine                |
| DELETE | `/medicines/delete/<id>/` | Delete specific medicine                      |

---

## Data Models

### Medicine Model

| Field          | Type               | Required       | Description                                                                                     |
| -------------- | ------------------ | -------------- | ----------------------------------------------------------------------------------------------- |
| `id`           | Integer            | Auto-generated | Unique identifier for the medicine                                                              |
| `user`         | ForeignKey         | Auto-assigned  | User who owns this medicine (from auth token)                                                   |
| `name`         | String (255)       | Yes            | Name of the medicine                                                                            |
| `amount`       | Integer            | Yes            | Number of units to be taken at a time (e.g., 2 tablets)                                         |
| `dosage`       | Integer            | Yes            | Dosage of the medicine (e.g., 500 for 500mg)                                                    |
| `time`         | JSON Array         | Yes            | Times of day when medicine is taken (e.g., ["08:00", "14:00", "20:00"]) in HH:MM 24-hour format |
| `days_of_week` | JSON Array         | Yes            | Days of week (1-7, where 1=Sunday, 7=Saturday)                                                  |
| `image`        | ImageField         | No             | Image of the medicine                                                                           |
| `image_url`    | String (Read-only) | No             | Full URL to the medicine image                                                                  |
| `help_message` | Text               | No             | Extra note for the user to remember                                                             |
| `start_date`   | DateTime           | No             | Start date of the medicine schedule (ISO 8601 format)                                           |
| `end_date`     | DateTime           | No             | End date of the medicine schedule (ISO 8601 format)                                             |

### Days of Week Reference

```
1 = Sunday
2 = Monday
3 = Tuesday
4 = Wednesday
5 = Thursday
6 = Friday
7 = Saturday
```

### Time Format

- **Format:** 24-hour time in "HH:MM" format
- **Examples:**
    - "08:00" (8:00 AM)
    - "14:30" (2:30 PM)
    - "20:00" (8:00 PM)
    - "00:00" (Midnight)

---

## Request & Response Examples

### 1. List All Medicines

**Endpoint:** `GET /medicines/list/`

**Headers:**

```
Authorization: Token abc123xyz456
```

**Request Body:** None

**Success Response (200 OK):**

```json
{
	"success": true,
	"response": [
		{
			"id": 1,
			"name": "Paracetamol",
			"amount": 2,
			"dosage": 500,
			"time": ["08:00", "14:00", "20:00"],
			"days_of_week": [1, 2, 3, 4, 5, 6, 7],
			"image_url": "http://localhost:8000/media/medicines/medicine_1.jpg",
			"help_message": "Take after meals with water",
			"start_date": "2025-11-26T08:00:00Z",
			"end_date": "2025-12-26T20:00:00Z"
		},
		{
			"id": 2,
			"name": "Vitamin D",
			"amount": 1,
			"dosage": 1000,
			"time": ["09:00"],
			"days_of_week": [1, 2, 3, 4, 5, 6, 7],
			"image_url": null,
			"help_message": "Take with breakfast",
			"start_date": "2025-11-20T09:00:00Z",
			"end_date": null
		}
	],
	"error": null
}
```

---

### 2. Create Medicine

**Endpoint:** `POST /medicines/add/` or `POST /medicines/list/`

**Headers:**

```
Authorization: Token abc123xyz456
Content-Type: application/json
```

**Request Body (Minimum Required):**

```json
{
	"name": "Aspirin",
	"amount": 1,
	"dosage": 100,
	"time": ["09:00"],
	"days_of_week": [1, 3, 5]
}
```

**Request Body (Full Example):**

```json
{
	"name": "Metformin",
	"amount": 1,
	"dosage": 500,
	"time": ["08:00", "20:00"],
	"days_of_week": [2, 3, 4, 5, 6],
	"help_message": "Take with food. Skip on weekends.",
	"start_date": "2025-11-26T08:00:00Z",
	"end_date": "2026-11-26T20:00:00Z"
}
```

**Success Response (201 Created):**

```json
{
	"success": true,
	"response": {
		"id": 3,
		"name": "Metformin",
		"amount": 1,
		"dosage": 500,
		"time": ["08:00", "20:00"],
		"days_of_week": [2, 3, 4, 5, 6],
		"image_url": null,
		"help_message": "Take with food. Skip on weekends.",
		"start_date": "2025-11-26T08:00:00Z",
		"end_date": "2026-11-26T20:00:00Z"
	},
	"error": null
}
```

**Error Response (400 Bad Request):**

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Bad Request",
		"details": {
			"name": ["This field is required."],
			"amount": ["This field is required."],
			"time": ["This field is required."]
		}
	}
}
```

---

### 3. Create Medicine with Image

**Endpoint:** `POST /medicines/add/`

**Headers:**

```
Authorization: Token abc123xyz456
Content-Type: multipart/form-data
```

**Request Body (Form Data):**

```
name: Ibuprofen
amount: 2
dosage: 200
time: ["08:00", "16:00"]
days_of_week: [1, 2, 3, 4, 5, 6, 7]
image: [binary file data]
help_message: Anti-inflammatory
start_date: 2025-11-26T08:00:00Z
```

**Success Response (201 Created):**

```json
{
	"success": true,
	"response": {
		"id": 4,
		"name": "Ibuprofen",
		"amount": 2,
		"dosage": 200,
		"time": ["08:00", "16:00"],
		"days_of_week": [1, 2, 3, 4, 5, 6, 7],
		"image_url": "http://localhost:8000/media/medicines/medicine_4.jpg",
		"help_message": "Anti-inflammatory",
		"start_date": "2025-11-26T08:00:00Z",
		"end_date": null
	},
	"error": null
}
```

---

### 4. Get Medicine Detail

**Endpoint:** `GET /medicines/detail/<id>/`

**Example:** `GET /medicines/detail/1/`

**Headers:**

```
Authorization: Token abc123xyz456
```

**Request Body:** None

**Success Response (200 OK):**

```json
{
	"success": true,
	"response": {
		"id": 1,
		"name": "Paracetamol",
		"amount": 2,
		"dosage": 500,
		"time": ["08:00", "14:00", "20:00"],
		"days_of_week": [1, 2, 3, 4, 5, 6, 7],
		"image_url": "http://localhost:8000/media/medicines/medicine_1.jpg",
		"help_message": "Take after meals with water",
		"start_date": "2025-11-26T08:00:00Z",
		"end_date": "2025-12-26T20:00:00Z"
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
		"message": "Medicine not found",
		"details": {
			"detail": "Medicine not found"
		}
	}
}
```

---

### 5. Update Medicine (Partial - PATCH)

**Endpoint:** `PATCH /medicines/update/<id>/`

**Example:** `PATCH /medicines/update/1/`

**Headers:**

```
Authorization: Token abc123xyz456
Content-Type: application/json
```

**Request Body (Update only specific fields):**

```json
{
	"time": ["09:00", "15:00", "21:00"],
	"help_message": "Updated: Take 1 hour after meals"
}
```

**Success Response (200 OK):**

```json
{
	"success": true,
	"response": {
		"id": 1,
		"name": "Paracetamol",
		"amount": 2,
		"dosage": 500,
		"time": ["09:00", "15:00", "21:00"],
		"days_of_week": [1, 2, 3, 4, 5, 6, 7],
		"image_url": "http://localhost:8000/media/medicines/medicine_1.jpg",
		"help_message": "Updated: Take 1 hour after meals",
		"start_date": "2025-11-26T08:00:00Z",
		"end_date": "2025-12-26T20:00:00Z"
	},
	"error": null
}
```

---

### 6. Update Medicine (Full - PUT)

**Endpoint:** `PUT /medicines/update/<id>/`

**Example:** `PUT /medicines/update/1/`

**Headers:**

```
Authorization: Token abc123xyz456
Content-Type: application/json
```

**Request Body (All required fields must be provided):**

```json
{
	"name": "Paracetamol Extended",
	"amount": 3,
	"dosage": 650,
	"time": ["10:00", "16:00"],
	"days_of_week": [2, 3, 4, 5, 6],
	"help_message": "Completely updated medicine info",
	"start_date": "2025-11-27T10:00:00Z",
	"end_date": "2025-12-27T16:00:00Z"
}
```

**Success Response (200 OK):**

```json
{
	"success": true,
	"response": {
		"id": 1,
		"name": "Paracetamol Extended",
		"amount": 3,
		"dosage": 650,
		"time": ["10:00", "16:00"],
		"days_of_week": [2, 3, 4, 5, 6],
		"image_url": "http://localhost:8000/media/medicines/medicine_1.jpg",
		"help_message": "Completely updated medicine info",
		"start_date": "2025-11-27T10:00:00Z",
		"end_date": "2025-12-27T16:00:00Z"
	},
	"error": null
}
```

---

### 7. Delete Medicine

**Endpoint:** `DELETE /medicines/delete/<id>/`

**Example:** `DELETE /medicines/delete/1/`

**Headers:**

```
Authorization: Token abc123xyz456
```

**Request Body:** None

**Success Response (204 No Content):**

```json
{
	"success": true,
	"response": {},
	"error": null
}
```

**Error Response (404 Not Found):**

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

## Common Usage Scenarios

### Scenario 1: Three Times Daily Medicine

```json
{
	"name": "Amoxicillin",
	"amount": 1,
	"dosage": 500,
	"time": ["08:00", "14:00", "20:00"],
	"days_of_week": [1, 2, 3, 4, 5, 6, 7],
	"help_message": "Complete the full course",
	"start_date": "2025-11-26T08:00:00Z",
	"end_date": "2025-12-03T20:00:00Z"
}
```

### Scenario 2: Once Daily Morning Vitamin

```json
{
	"name": "Multivitamin",
	"amount": 1,
	"dosage": 1,
	"time": ["09:00"],
	"days_of_week": [1, 2, 3, 4, 5, 6, 7],
	"help_message": "Take with breakfast"
}
```

### Scenario 3: Weekday Only Medication

```json
{
	"name": "Work Day Supplement",
	"amount": 2,
	"dosage": 250,
	"time": ["08:00"],
	"days_of_week": [2, 3, 4, 5, 6],
	"help_message": "Monday to Friday only",
	"start_date": "2025-11-26T08:00:00Z"
}
```

### Scenario 4: Twice Daily with Specific Days

```json
{
	"name": "Insulin",
	"amount": 1,
	"dosage": 10,
	"time": ["08:00", "20:00"],
	"days_of_week": [1, 2, 3, 4, 5, 6, 7],
	"help_message": "Take 30 minutes before meals",
	"start_date": "2025-11-26T08:00:00Z"
}
```

---

## cURL Examples

### Get All Medicines

```bash
curl -X GET http://localhost:8000/medicines/list/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Create New Medicine

```bash
curl -X POST http://localhost:8000/medicines/add/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Paracetamol",
    "amount": 2,
    "dosage": 500,
    "time": ["08:00", "14:00", "20:00"],
    "days_of_week": [1, 2, 3, 4, 5, 6, 7],
    "help_message": "Take after meals",
    "start_date": "2025-11-26T08:00:00Z"
  }'
```

### Create Medicine with Image

```bash
curl -X POST http://localhost:8000/medicines/add/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -F "name=Aspirin" \
  -F "amount=1" \
  -F "dosage=100" \
  -F 'time=["09:00"]' \
  -F 'days_of_week=[1,3,5]' \
  -F "image=@/path/to/medicine_image.jpg" \
  -F "help_message=Take with food"
```

### Get Specific Medicine

```bash
curl -X GET http://localhost:8000/medicines/detail/1/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

### Update Medicine (PATCH)

```bash
curl -X PATCH http://localhost:8000/medicines/update/1/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "time": ["09:00", "15:00", "21:00"],
    "help_message": "Updated instructions"
  }'
```

### Update Medicine (PUT)

```bash
curl -X PUT http://localhost:8000/medicines/update/1/ \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Medicine",
    "amount": 2,
    "dosage": 500,
    "time": ["10:00", "22:00"],
    "days_of_week": [1, 2, 3, 4, 5, 6, 7]
  }'
```

### Delete Medicine

```bash
curl -X DELETE http://localhost:8000/medicines/delete/1/ \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

---

## Python Requests Examples

### Setup

```python
import requests
import json

BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "your_auth_token_here"

headers = {
    "Authorization": f"Token {AUTH_TOKEN}",
    "Content-Type": "application/json"
}
```

### Create Medicine

```python
medicine_data = {
    "name": "Paracetamol",
    "amount": 2,
    "dosage": 500,
    "time": ["08:00", "14:00", "20:00"],
    "days_of_week": [1, 2, 3, 4, 5, 6, 7],
    "help_message": "Take after meals",
    "start_date": "2025-11-26T08:00:00Z"
}

response = requests.post(
    f"{BASE_URL}/medicines/add/",
    headers=headers,
    json=medicine_data
)

print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
```

### Get All Medicines

```python
response = requests.get(
    f"{BASE_URL}/medicines/list/",
    headers=headers
)

data = response.json()
if data['success']:
    medicines = data['response']
    for medicine in medicines:
        print(f"{medicine['id']}: {medicine['name']} - {medicine['dosage']}mg")
else:
    print(f"Error: {data['error']['message']}")
```

### Update Medicine

```python
update_data = {
    "time": ["09:00", "15:00", "21:00"],
    "help_message": "Updated: Take 1 hour after meals"
}

response = requests.patch(
    f"{BASE_URL}/medicines/update/1/",
    headers=headers,
    json=update_data
)

data = response.json()
if data['success']:
    print(f"Updated: {data['response']}")
else:
    print(f"Error: {data['error']['message']}")
```

### Delete Medicine

```python
response = requests.delete(
    f"{BASE_URL}/medicines/delete/1/",
    headers=headers
)

data = response.json()
print(f"Deleted: {data['success']}")
```

---

## Error Handling

### Common HTTP Status Codes

| Code | Status       | Description                               |
| ---- | ------------ | ----------------------------------------- |
| 200  | OK           | Request successful (GET, PATCH, PUT)      |
| 201  | Created      | Medicine created successfully (POST)      |
| 204  | No Content   | Medicine deleted successfully (DELETE)    |
| 400  | Bad Request  | Invalid request data or validation errors |
| 401  | Unauthorized | Missing or invalid authentication token   |
| 404  | Not Found    | Medicine with specified ID not found      |

**Note:** All responses (including errors) are wrapped in the standard response format with `success`, `response`, and `error` fields.

### Validation Error Example

**Response (400 Bad Request):**

```json
{
	"success": false,
	"response": null,
	"error": {
		"message": "Bad Request",
		"details": {
			"name": ["This field is required."],
			"amount": ["A valid integer is required."],
			"time": ["This field is required."],
			"days_of_week": ["This field is required."]
		}
	}
}
```

### Handling Wrapped Responses

When working with the API, always check the `success` field first:

```python
response = requests.get(f"{BASE_URL}/medicines/list/", headers=headers)
data = response.json()

if data['success']:
    # Success - data is in 'response' field
    medicines = data['response']
    print(medicines)
else:
    # Error - error info is in 'error' field
    print(f"Error: {data['error']['message']}")
    print(f"Details: {data['error']['details']}")
```

---

## Field Validations

### Required Fields

- `name` - Cannot be empty, max 255 characters
- `amount` - Must be a positive integer
- `dosage` - Must be a positive integer
- `time` - Must be a non-empty array of time strings in "HH:MM" format
- `days_of_week` - Must be a non-empty array of integers (1-7)

### Optional Fields

- `image` - Must be a valid image file (JPEG, PNG, etc.)
- `help_message` - Can be any text
- `start_date` - Must be a valid ISO 8601 datetime string
- `end_date` - Must be a valid ISO 8601 datetime string

### Time Format Validation

- Must be in 24-hour format: "HH:MM"
- Valid examples: "00:00", "08:30", "14:15", "23:59"
- Invalid examples: "8:00" (should be "08:00"), "25:00" (invalid hour)

### Days of Week Validation

- Must be integers from 1 to 7
- 1 = Sunday, 2 = Monday, ..., 7 = Saturday
- Can be a subset (e.g., [2, 4, 6] for Mon, Wed, Fri)

## Notes

1. **Response Wrapper**: All responses are wrapped in a consistent structure with `success`, `response`, and `error` fields. Always check the `success` field first before accessing data.

2. **User Isolation**: Users can only access their own medicines. The `user` field is automatically assigned from the authentication token.

3. **Image Handling**:
    - Images are stored in `MEDIA_ROOT/medicines/`
    - Use `multipart/form-data` when uploading images
    - The `image_url` field returns the full URL

4. **Date Format**: All datetime fields use ISO 8601 format (e.g., "2025-11-26T08:00:00Z")

5. **Time Array**: The `time` field can contain multiple time slots for medicines taken multiple times per day

6. **Days of Week**: Stored as integers where Sunday=1 and Saturday=7

7. **Partial Updates**: Use PATCH to update only specific fields, PUT requires all required fields

---

## Testing

To test the API locally:

1. Start the Django development server:

    ```bash
    python manage.py runserver
    ```

2. Obtain an authentication token (via login endpoint)

3. Use the examples above with your token

4. Check responses for proper data structure

---

## Support

For issues or questions, please contact the MediGuard Backend Team.

**Last Updated:** November 26, 2025
