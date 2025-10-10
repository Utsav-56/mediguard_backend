# MedGuard Backend API Documentation

## Overview

MedGuard is a comprehensive medication tracking and health metrics management backend built with Django REST Framework. It provides a robust API for managing medicines, schedules, reminders, intakes, and health metrics with automatic reminder generation using Celery.

## Authentication

The API uses JWT (JSON Web Token) authentication via Djoser.

### Auth Endpoints

- `POST /api/auth/users/` - Register a new user
- `POST /api/auth/jwt/create/` - Login (get access & refresh tokens)
- `POST /api/auth/jwt/refresh/` - Refresh access token
- `POST /api/auth/jwt/verify/` - Verify token validity
- `GET /api/auth/users/me/` - Get current user profile
- `PUT /api/auth/users/me/` - Update current user profile

### Sample Registration

```json
POST /api/auth/users/
{
  "email": "john@example.com",
  "full_name": "John Doe",
  "password": "securepassword123",
  "phone_number": "+1234567890",
  "timezone": "Asia/Kathmandu"
}
```

### Sample Login

```json
POST /api/auth/jwt/create/
{
  "email": "john@example.com",
  "password": "securepassword123"
}

Response:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci..."
}
```

## API Endpoints

### User Management

- `GET /api/accounts/caretakers/` - List user's caretakers
- `POST /api/accounts/caretakers/` - Create and link new caretaker
- `POST /api/accounts/caretakers/link-existing/` - Link existing caretaker
- `PUT /api/accounts/caretakers/{id}/update-permissions/` - Update caretaker permissions
- `DELETE /api/accounts/caretakers/{id}/unlink/` - Unlink caretaker

### Medicine Management

- `GET /api/medicines/` - List user's medicines
- `POST /api/medicines/` - Create new medicine
- `GET /api/medicines/{id}/` - Get medicine details
- `PUT /api/medicines/{id}/` - Update medicine
- `DELETE /api/medicines/{id}/` - Delete medicine
- `GET /api/medicines/{id}/attributes/` - Get medicine attributes
- `GET /api/medicines/{id}/schedules/` - Get medicine schedules
- `GET /api/medicines/{id}/intakes/` - Get medicine intake history

### Medicine Attributes

- `GET /api/medicine-attributes/` - List attributes
- `POST /api/medicine-attributes/` - Create attribute
- `PUT /api/medicine-attributes/{id}/` - Update attribute
- `DELETE /api/medicine-attributes/{id}/` - Delete attribute

### Schedules & Reminders

- `GET /api/schedules/` - List schedules
- `POST /api/schedules/` - Create schedule (auto-generates reminders)
- `PUT /api/schedules/{id}/` - Update schedule
- `DELETE /api/schedules/{id}/` - Delete schedule

- `GET /api/reminders/` - List upcoming reminders
- `POST /api/reminders/{id}/snooze/` - Snooze reminder
- `POST /api/reminders/{id}/dismiss/` - Dismiss reminder

### Intake Tracking

- `GET /api/intakes/` - List intake records
- `POST /api/intakes/` - Record intake (taken/missed)
- `PUT /api/intakes/{id}/` - Update intake record
- `GET /api/intakes/stats/` - Get adherence statistics

### Health Metrics

- `GET /api/health-metrics/` - List health metrics
- `POST /api/health-metrics/` - Create health metric
- `GET /api/health-metrics/{id}/` - Get metric details
- `GET /api/health-metrics/{id}/readings/` - Get metric readings
- `GET /api/health-metrics/{id}/stats/` - Get metric statistics

### Metric Readings

- `GET /api/metric-readings/` - List readings
- `POST /api/metric-readings/` - Create reading
- `POST /api/metric-readings/bulk-create/` - Create multiple readings
- `GET /api/metric-readings/summary/` - Get readings summary

### Push Notifications

- `GET /api/push-subscriptions/` - List subscriptions
- `POST /api/push-subscriptions/` - Register device for notifications
- `POST /api/push-subscriptions/{id}/toggle-active/` - Toggle subscription

## Sample API Usage

### 1. Create Medicine

```json
POST /api/medicines/
Authorization: Bearer YOUR_ACCESS_TOKEN
{
  "name": "Paracetamol",
  "brand": "Crocin",
  "start_date": "2025-10-10",
  "until": "2025-10-20",
  "notes": "For fever and pain relief"
}
```

### 2. Create Medicine Attribute

```json
POST /api/medicine-attributes/
Authorization: Bearer YOUR_ACCESS_TOKEN
{
  "medicine": 1,
  "form": "tablet",
  "dose": 500,
  "dose_unit": "mg",
  "composition": {
    "active_ingredient": "Paracetamol",
    "strength": "500mg",
    "excipients": ["Microcrystalline cellulose", "Sodium starch glycolate"]
  }
}
```

### 3. Create Schedule with Recurrence

```json
POST /api/schedules/
Authorization: Bearer YOUR_ACCESS_TOKEN
{
  "medicine": 1,
  "time": "08:00:00",
  "date": "2025-10-10",
  "end_date": "2025-10-20",
  "rrule": "FREQ=DAILY;INTERVAL=1",
  "instruction": "After breakfast",
  "timezone": "Asia/Kathmandu"
}
```

### 4. Record Intake

```json
POST /api/intakes/
Authorization: Bearer YOUR_ACCESS_TOKEN
{
  "medicine": 1,
  "schedule": 1,
  "status": "taken",
  "scheduled_time": "2025-10-10T02:15:00Z",
  "taken_at": "2025-10-10T02:17:00Z",
  "note": "Taken with water after breakfast"
}
```

### 5. Create Health Metric Reading

```json
POST /api/metric-readings/
Authorization: Bearer YOUR_ACCESS_TOKEN
{
  "metric_key": "blood_pressure",
  "recorded_at": "2025-10-10T08:30:00Z",
  "systolic": 120,
  "diastolic": 80,
  "heart_rate": 72,
  "notes": "Morning reading, feeling good"
}
```

### 6. Blood Sugar Reading

```json
POST /api/metric-readings/
Authorization: Bearer YOUR_ACCESS_TOKEN
{
  "metric_key": "blood_sugar",
  "recorded_at": "2025-10-10T08:30:00Z",
  "glucose_level": 95.5,
  "values": {
    "test_type": "fasting",
    "meter_reading": "95.5 mg/dL"
  },
  "notes": "Fasting glucose - normal range"
}
```

## Features

### 1. Medicine Management

- Comprehensive medicine information storage
- Flexible attributes with JSON composition data
- Image upload support for medicine photos
- Start and end date tracking

### 2. Advanced Scheduling

- Support for complex recurrence rules (RRULE RFC5545)
- Timezone-aware scheduling
- Automatic reminder generation
- Dose overrides per schedule

### 3. Smart Reminders

- Celery-powered background reminder processing
- Snooze and dismiss functionality
- Automatic next occurrence scheduling
- Status tracking (pending, triggered, taken, missed)

### 4. Health Metrics

- Dynamic health metric definitions
- Common metrics: Blood Pressure, Blood Sugar, Weight, Heart Rate
- Flexible JSON storage for custom metrics
- Statistical analysis endpoints

### 5. Caretaker Support

- Link multiple caretakers to a user
- Granular permission system
- Caretaker can confirm intakes and view metrics

### 6. Audit & Compliance

- Complete audit trail for critical actions
- Data retention policies
- User data export capabilities

## Background Tasks (Celery)

The system uses Celery for background processing:

1. **Reminder Generation** - `expand_schedule_rrule`
2. **Reminder Processing** - `process_due_reminders` (runs every minute)
3. **Push Notifications** - `send_push_notification`
4. **Data Cleanup** - `cleanup_old_intakes`

To start Celery worker:

```bash
cd d:\college_projects\mediguard_backend
uv run celery -A main_app worker --loglevel=info
```

To start Celery Beat (scheduler):

```bash
cd d:\college_projects\mediguard_backend
uv run celery -A main_app beat --loglevel=info
```

## Development Setup

1. **Install Dependencies**:

    ```bash
    cd d:\college_projects\mediguard_backend
    uv install
    ```

2. **Environment Variables**:
   Create a `.env` file:

    ```env
    SECRET_KEY=your-secret-key-here
    DATABASE_URL=postgresql://user:password@localhost:5432/mediguard
    REDIS_URL=redis://localhost:6379/0
    DEBUG=True
    ```

3. **Database Setup**:

    ```bash
    uv run manage.py migrate
    uv run manage.py createsuperuser
    ```

4. **Start Services**:

    ```bash
    # Terminal 1: Django
    uv run manage.py runserver

    # Terminal 2: Redis
    redis-server

    # Terminal 3: Celery Worker
    uv run celery -A main_app worker --loglevel=info

    # Terminal 4: Celery Beat
    uv run celery -A main_app beat --loglevel=info
    ```

## Production Deployment

See the specifications document for complete production deployment instructions including:

- Docker containerization
- PostgreSQL configuration
- Redis setup
- Nginx reverse proxy
- SSL/TLS configuration
- Environment variable management

## API Response Format

All endpoints return JSON responses with consistent formatting:

### Success Response

```json
{
  "data": { ... },
  "message": "Success"
}
```

### Error Response

```json
{
  "error": "Error message",
  "details": { ... }
}
```

### Paginated Response

```json
{
  "count": 100,
  "next": "http://api.example.com/medicines/?page=3",
  "previous": "http://api.example.com/medicines/?page=1",
  "results": [ ... ]
}
```

## Testing

Run tests with:

```bash
uv run manage.py test
```

For specific app tests:

```bash
uv run manage.py test medicines
uv run manage.py test accounts
uv run manage.py test health_metrics
```

## Admin Interface

Access the Django admin at `http://127.0.0.1:8000/admin/` with superuser credentials to:

- Manage users and caretakers
- View medicines and schedules
- Monitor reminders and intakes
- Analyze health metrics
- Check audit logs

## Support

For technical support or feature requests, please refer to the project specifications or contact the development team.
