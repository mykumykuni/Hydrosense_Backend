# HydroSense Backend — API Documentation

Base URL: `http://localhost:8000`

## Authentication

All endpoints (except `register` and `login`) require a JWT Bearer token:

```
Authorization: Bearer <access_token>
```

Tokens are obtained via `POST /api/users/login/`. Access tokens expire after **60 minutes**. Use the refresh endpoint to get a new one.

---

## Users

### `POST /api/users/register/`
Register a new user account. Status defaults to `pending` until approved by an admin.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "role": "operator"
}
```

---

### `POST /api/users/login/`
Obtain JWT access + refresh tokens.

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access": "<access_token>",
  "refresh": "<refresh_token>"
}
```

---

### `POST /api/users/token/refresh/`
Get a new access token using a refresh token.

**Body:**
```json
{ "refresh": "<refresh_token>" }
```

---

### `GET /api/users/profile/`
Get current user's profile. Requires auth.

### `PUT /PATCH /api/users/profile/`
Update current user's profile (`display_name`, `photo_data_url`, `phone`, `address`, `bio`, `position`, `emergency_contact`).

---

### `POST /api/users/change-password/`
Change password. Invalidates all existing tokens (sets `revoked_since`).

**Body:**
```json
{
  "old_password": "current",
  "new_password": "newpassword"
}
```

---

### `GET /api/users/`
List all users. **Admin only.**

---

### `POST /api/users/{id}/approve/`
Approve a pending user. **Admin only.**

### `POST /api/users/{id}/deactivate/`
Deactivate a user. Invalidates their tokens. **Admin only.**

---

## Sensors

### `GET /api/sensors/devices/`
List all sensor devices. Requires auth.

### `POST /api/sensors/devices/`
Register a new sensor device. Requires auth.

**Body:**
```json
{
  "device_id": "SENSOR-001",
  "name": "Pond A Sensor",
  "location": "Pond A - North",
  "is_active": true
}
```

### `GET /api/sensors/devices/{id}/`
### `PUT/PATCH /api/sensors/devices/{id}/`
### `DELETE /api/sensors/devices/{id}/`

---

### `GET /api/sensors/readings/`
List sensor readings. Requires auth. Supports filtering and ordering.

### `POST /api/sensors/readings/`
Ingest a new sensor reading. **Internal use only** — requires `X-Api-Key` header (FastAPI service).

**Headers:**
```
X-Api-Key: <INTERNAL_API_KEY>
```

**Body:**
```json
{
  "device_id": "SENSOR-001",
  "do": 6.5,
  "ph": 7.2,
  "temp": 29.5,
  "salinity": 30.1,
  "timestamp": "2026-05-31T10:00:00Z"
}
```

---

### `GET /api/sensors/thresholds/`
Get the current threshold configuration (singleton). Requires auth.

### `PUT/PATCH /api/sensors/thresholds/`
Update thresholds. **Admin only.**

**All threshold fields (with defaults):**

| Field | Default | Meaning |
|-------|---------|---------|
| `do_min` | 4.0 | DO safe lower (mg/L) |
| `do_max` | 9.0 | DO safe upper (mg/L) |
| `do_critical_min` | 1.4 | DO critical lower |
| `do_critical_max` | 12.0 | DO critical upper |
| `ph_min` | 6.0 | pH safe lower |
| `ph_max` | 8.0 | pH safe upper |
| `ph_critical_min` | 4.0 | pH critical lower |
| `ph_critical_max` | 10.0 | pH critical upper |
| `temp_min` | 28.0 | Temp safe lower (°C) |
| `temp_max` | 32.0 | Temp safe upper (°C) |
| `temp_critical_min` | 25.0 | Temp critical lower |
| `temp_critical_max` | 35.0 | Temp critical upper |
| `salinity_min` | 28.0 | Salinity safe lower (ppt) |
| `salinity_max` | 33.0 | Salinity safe upper (ppt) |
| `salinity_critical_min` | 20.0 | Salinity critical lower |
| `salinity_critical_max` | 40.0 | Salinity critical upper |

**Severity logic:**
- `Safe` — value within `[min, max]`
- `Warning` — value between `[critical_min, min)` or `(max, critical_max]`
- `Critical` — value below `critical_min` or above `critical_max`

---

## Alerts

### `GET /api/alerts/`
List alerts (newest first, max 300). Requires auth.

### `POST /api/alerts/`
Create a manual alert. Requires auth.

**Body:**
```json
{
  "severity": "warning",
  "title": "Manual alert",
  "message": "Unusual smell detected near Pond B",
  "source": "manual-operator"
}
```

Severity choices: `critical`, `warning`, `info`

---

### `POST /api/alerts/{id}/mark-read/`
Mark an alert as read by the current user.

### `POST /api/alerts/{id}/resolve/`
Mark an alert as resolved. **Admin only.**

### `DELETE /api/alerts/clear-all/`
Delete all alerts. **Admin only.** Logged to audit trail.

---

## Reports

### `GET /api/reports/`
List reports. Operators see their own; admins see all.

### `POST /api/reports/`
Submit a new report. Requires auth.

**Body:**
```json
{
  "type": "water_quality",
  "priority": "high",
  "message": "pH readings consistently above 8.0 for the past 3 hours"
}
```

Type choices: `equipment`, `water_quality`, `general`, `custom`
Priority choices: `low`, `medium`, `high`, `urgent`
Subject is auto-set for standard types; provide `subject` manually for `custom`.

### `GET /api/reports/{id}/`
### `PUT/PATCH /api/reports/{id}/`
### `DELETE /api/reports/{id}/`

---

### `GET /api/reports/replies/`
List report replies.

### `POST /api/reports/replies/`
Add a reply to a report. **Admin only.** Applicable to `general` and `custom` type reports.

**Body:**
```json
{
  "report": 5,
  "message": "Acknowledged. Checking calibration."
}
```

---

## Audit Log

### `GET /api/audit/`
Read-only audit trail. **Admin only.** Max 200 entries.

Logged actions: `clear_all_alerts`, `resolve_alert`, `create_manual_alert`, `update_threshold`, `set_history_window`, `set_announcement`, `clear_announcement`, `add_announcement_to_history`, `approve_user`, `deactivate_user`

---

## Shift Logs

### `GET /api/shifts/`
List shift logs. Requires auth.

### `POST /api/shifts/`
Create a shift log note. Requires auth. Max 1000 characters. Max 100 entries total.

**Body:**
```json
{
  "note": "End of shift. All parameters normal. Feeding completed at 17:00."
}
```

### `GET /api/shifts/{id}/`
### `PUT/PATCH /api/shifts/{id}/`
### `DELETE /api/shifts/{id}/`

---

## WebSocket

**Endpoint:** `ws://localhost:8000/ws/?token=<access_token>`

Authentication is via JWT query param. Only `active` users with valid (non-revoked) tokens can connect. Disconnects with code `4001` on auth failure.

### Client → Server

```json
{ "type": "ping" }
```
Response: `{ "type": "pong" }`

### Server → Client

**On new sensor reading:**
```json
{
  "type": "sensor.reading",
  "data": {
    "id": 42,
    "device_id": "SENSOR-001",
    "do": 6.5,
    "ph": 7.2,
    "temp": 29.5,
    "salinity": 30.1,
    "ts": 1748686800000
  }
}
```

**On new alert:**
```json
{
  "type": "alert.new",
  "data": {
    "id": 7,
    "uid": "1748686800000-abc123",
    "severity": "critical",
    "title": "DO Critical",
    "message": "Dissolved oxygen dropped below 1.4 mg/L",
    "source": "do",
    "resolved": false,
    "ts": 1748686800000
  }
}
```

**On alert resolved:**
```json
{
  "type": "alert.resolved",
  "data": { "...same fields...", "resolved": true }
}
```

---

## FastAPI Sensor Ingestion

Base URL: `http://localhost:8001`

### `POST /sensor-data/`
Receive a reading from an IoT device and forward it to Django.

**Body:**
```json
{
  "device_id": "SENSOR-001",
  "do": 6.5,
  "ph": 7.2,
  "temp": 29.5,
  "salinity": 30.1,
  "timestamp": "2026-05-31T10:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Reading forwarded",
  "device_id": "SENSOR-001"
}
```

### `GET /health`
Health check endpoint.

---

## Error Responses

| Status | Meaning |
|--------|---------|
| `400` | Validation error — check request body |
| `401` | Missing or invalid JWT token |
| `403` | Authenticated but insufficient permissions |
| `404` | Resource not found |
| `500` | Server error |

Auth errors return:
```json
{ "detail": "Authentication credentials were not provided." }
```
