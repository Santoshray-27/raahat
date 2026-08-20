# RAAHAT — API Contracts & Integration Guide

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Team:** Solution Savvy  
**Primary goal:** Establish a single source of truth for API contracts so React, Flutter, FastAPI, AI/RAG, Google services, PostgreSQL, Firebase Authentication, voice, offline-pack generation, and future agentic actions integrate without payload mismatches.

---

# 1. Purpose

This document defines:

- API endpoints
- HTTP methods
- URL structure
- authentication rules
- request payloads
- response payloads
- validation schemas
- enums
- error formats
- pagination conventions
- timestamps
- coordinates
- IDs
- frontend/backend responsibilities
- Flutter/backend responsibilities
- AI/RAG contracts
- offline-pack contracts
- voice contracts
- agentic-action contracts
- integration rules
- versioning
- testing strategy

## Golden rule

> **Frontend and Flutter must never invent their own payload shape. FastAPI schemas are the source of truth.**

If a field changes, update this contract and all clients together.

---

# 2. Technology Context

```text
React Web
    │
    │ HTTPS + JSON
    ▼
FastAPI
    │
    ├── Firebase Authentication verification
    ├── PostgreSQL
    ├── AI Orchestrator
    ├── RAG
    ├── Google Places / Routes
    ├── Sarvam
    └── Offline Pack Generator
          │
          ▼
      Flutter App
      Local AI / Local DB
```

Authentication:

```text
Firebase Authentication
```

Backend:

```text
FastAPI
```

Database:

```text
PostgreSQL
```

Web:

```text
React
```

Mobile:

```text
Flutter
```

AI:

```text
Groq + selected LLM
RAG
Gemma offline
Sarvam voice
```

Maps/places:

```text
Google Maps / Places / Routes APIs
```

---

# 3. API Design Principles

## 3.1 JSON everywhere

All normal application APIs use:

```http
Content-Type: application/json
```

Exception:

- audio upload/streaming endpoints if implemented using multipart or provider-specific formats.

## 3.2 REST conventions

Use:

```text
GET     → retrieve
POST    → create / execute action
PATCH   → partial update
DELETE  → delete
```

## 3.3 Versioning

All APIs begin with:

```text
/api/v1
```

Example:

```text
/api/v1/emergency-assistance
```

## 3.4 IDs

Use string IDs externally.

Example:

```json
{
  "incident_id": "inc_01J..."
}
```

Do not expose database implementation-specific integer IDs if avoidable.

## 3.5 Timestamps

Use ISO-8601 UTC timestamps:

```text
2026-08-20T12:30:45Z
```

Clients must not invent local timestamp formats.

## 3.6 Coordinates

Always:

```json
{
  "latitude": 22.7196,
  "longitude": 75.8577
}
```

Rules:

```text
latitude  ∈ [-90, 90]
longitude ∈ [-180, 180]
```

Never reverse the order.

---

# 4. Authentication Contract

Firebase handles user authentication.

Client obtains Firebase ID token.

Every protected FastAPI request sends:

```http
Authorization: Bearer <FIREBASE_ID_TOKEN>
```

FastAPI:

```text
Authorization header
        ↓
Firebase token verification
        ↓
decoded uid
        ↓
request.user
```

The client must never send:

```json
{
  "user_id": "..."
}
```

as a substitute for authentication.

The backend derives the authenticated user ID from the verified Firebase token.

---

# 5. Standard Headers

Required for protected JSON APIs:

```http
Authorization: Bearer <token>
Content-Type: application/json
Accept: application/json
```

Optional:

```http
X-Request-ID: <uuid>
```

Recommended for debugging.

---

# 6. Standard Response Envelope

Successful responses should follow:

```json
{
  "success": true,
  "data": {},
  "meta": null,
  "request_id": "req_123"
}
```

For lists:

```json
{
  "success": true,
  "data": [],
  "meta": {
    "page": 1,
    "page_size": 20,
    "total": 42
  },
  "request_id": "req_123"
}
```

The client should always read:

```text
response.data
```

rather than assuming the API returns the object directly.

---

# 7. Standard Error Envelope

Every API error should use:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request.",
    "details": []
  },
  "request_id": "req_123"
}
```

Example:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_COORDINATES",
    "message": "Latitude must be between -90 and 90.",
    "details": [
      {
        "field": "location.latitude",
        "reason": "out_of_range"
      }
    ]
  },
  "request_id": "req_123"
}
```

---

# 8. Standard HTTP Status Codes

| Status | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 202 | Accepted async action |
| 204 | Successful request with no body |
| 400 | Bad request |
| 401 | Missing/invalid authentication |
| 403 | Authenticated but not allowed |
| 404 | Resource not found |
| 409 | Conflict |
| 422 | Validation failure |
| 429 | Rate limit |
| 500 | Internal server error |
| 502 | Upstream provider failure |
| 503 | Temporary service unavailable |

Do not return `200` for application-level failures.

---

# 9. Shared Enums

These values must remain identical across React, Flutter, FastAPI and database models.

## IncidentType

```text
ACCIDENT
TYRE_PUNCTURE
VEHICLE_BREAKDOWN
VEHICLE_FIRE
MEDICAL_EMERGENCY
STRANDED
FUEL_EMERGENCY
OTHER
```

## ServiceCategory

```text
HOSPITAL
POLICE
AMBULANCE
FIRE_STATION
TOWING
PUNCTURE_REPAIR
MECHANIC
VEHICLE_SERVICE
FUEL_STATION
OTHER
```

## Severity

```text
LOW
MEDIUM
HIGH
CRITICAL
UNKNOWN
```

## NetworkMode

```text
ONLINE
LIMITED
OFFLINE
```

## AIResponseMode

```text
ONLINE
OFFLINE
FALLBACK
```

## Language

Initial:

```text
en
hi
```

Future values can be added without changing the API structure.

## SourceAuthority

```text
OFFICIAL
INSTITUTIONAL
VERIFIED_SECONDARY
UNKNOWN
```

## ActionType

```text
CALL
NAVIGATE
OPEN_MAP
GET_GUIDANCE
CONTACT_PROVIDER
```

---

# 10. Shared Location Schema

```json
{
  "latitude": 22.7196,
  "longitude": 75.8577,
  "accuracy_meters": 8.5,
  "timestamp": "2026-08-20T12:30:45Z"
}
```

Pydantic concept:

```python
class Location(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_meters: float | None = Field(default=None, ge=0)
    timestamp: datetime
```

Clients should send GPS accuracy when available.

---

# 11. Shared Service Schema

Every service returned to either client must have the same shape.

```json
{
  "service_id": "svc_123",
  "provider_id": "google_place_abc",
  "name": "ABC Hospital",
  "category": "HOSPITAL",
  "location": {
    "latitude": 22.7196,
    "longitude": 75.8577,
    "accuracy_meters": null,
    "timestamp": "2026-08-20T12:30:45Z"
  },
  "address": "Example address",
  "phone": "+91XXXXXXXXXX",
  "distance_meters": 1250,
  "estimated_duration_seconds": 420,
  "rating": 4.4,
  "is_open": null,
  "availability_status": "UNKNOWN",
  "source": "GOOGLE_PLACES",
  "retrieved_at": "2026-08-20T12:30:45Z",
  "is_cached": false
}
```

Important:

```text
is_open = null
```

means we do not know.

Do NOT convert unknown availability into:

```text
false
```

---

# 12. Provider Availability Rule

RAAHAT must distinguish:

```text
OPEN
CLOSED
UNKNOWN
```

For cached/offline data:

```text
availability_status = UNKNOWN
```

unless a valid verified status is available.

Never claim:

> “This mechanic is available right now”

based only on an old Places result.

---

# 13. Core API Groups

The API surface should be organized into:

```text
1. Health
2. User/Profile
3. Emergency Assistance
4. Places/Services
5. Routes
6. RAG
7. Voice
8. Offline Packs
9. Incidents
10. Agentic Actions
11. Sync
```

Not every endpoint must be implemented on day one.

---

# 14. Health API

## GET

```text
GET /api/v1/health
```

No authentication required.

Response:

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "version": "1.0.0",
    "services": {
      "database": "ok",
      "google": "ok",
      "rag": "ok",
      "llm": "ok"
    }
  },
  "request_id": "req_123"
}
```

Used for:

- deployment checks
- frontend startup diagnostics
- debugging

---

# 15. User Profile

## GET

```text
GET /api/v1/users/me
```

Response:

```json
{
  "success": true,
  "data": {
    "user_id": "firebase_uid",
    "name": "Satwik",
    "email": "user@example.com",
    "preferred_language": "hi",
    "created_at": "2026-08-20T10:00:00Z"
  }
}
```

## PATCH

```text
PATCH /api/v1/users/me
```

Request:

```json
{
  "name": "Satwik",
  "preferred_language": "hi"
}
```

Do not allow client to modify:

```text
user_id
created_at
```

---

# 16. Emergency Assistance — PRIMARY API

This is the most important API contract in RAAHAT.

## POST

```text
POST /api/v1/emergency-assistance
```

Purpose:

> Convert a user's situation into structured incident understanding, guidance, relevant services and recommended actions.

---

# 17. Emergency Assistance Request

```json
{
  "message": "My tyre got punctured on the highway.",
  "language": "en",
  "location": {
    "latitude": 22.7196,
    "longitude": 75.8577,
    "accuracy_meters": 10,
    "timestamp": "2026-08-20T12:30:45Z"
  },
  "network_mode": "ONLINE",
  "include_services": true,
  "service_categories": [
    "PUNCTURE_REPAIR",
    "MECHANIC",
    "TOWING"
  ],
  "max_services": 5,
  "session_id": "sess_123"
}
```

---

# 18. Emergency Assistance Request Validation

Required:

```text
message
location
network_mode
```

Constraints:

```text
message:
1–2000 characters

max_services:
1–20

language:
supported enum

network_mode:
supported enum
```

`service_categories` is optional.

If absent, the backend determines relevant categories.

---

# 19. Emergency Assistance Response

```json
{
  "success": true,
  "data": {
    "incident": {
      "incident_type": "TYRE_PUNCTURE",
      "severity": "MEDIUM",
      "confidence": 0.94,
      "summary": "Vehicle has a tyre puncture."
    },
    "guidance": {
      "title": "Stay safe after a tyre puncture",
      "steps": [
        "Move to a safe location if possible.",
        "Turn on hazard lights.",
        "Avoid continuing to drive if the tyre is damaged."
      ],
      "safety_note": "Do not attempt repairs in an unsafe traffic position.",
      "sources": []
    },
    "services": [],
    "recommended_actions": [],
    "ai": {
      "mode": "ONLINE",
      "model": "selected-model",
      "rag_used": true
    }
  },
  "request_id": "req_123"
}
```

---

# 20. Incident Object

```json
{
  "incident_type": "TYRE_PUNCTURE",
  "severity": "MEDIUM",
  "confidence": 0.94,
  "summary": "Vehicle has a tyre puncture."
}
```

Backend owns the classification.

Frontend must never assume:

```text
if message contains "puncture"
```

It should render whatever structured classification the backend returns.

---

# 21. Guidance Object

```json
{
  "title": "Immediate safety guidance",
  "steps": [
    "Step 1",
    "Step 2"
  ],
  "safety_note": "Important warning",
  "sources": [
    {
      "source_id": "src_123",
      "title": "Official Road Safety Guide",
      "authority_level": "OFFICIAL",
      "url": "https://example.com",
      "last_verified": "2026-08-20T00:00:00Z"
    }
  ]
}
```

The frontend renders this generically.

---

# 22. Recommended Action Object

```json
{
  "action_id": "act_123",
  "type": "CALL",
  "label": "Call nearest mechanic",
  "service_id": "svc_123",
  "requires_confirmation": true
}
```

For sensitive actions:

```text
requires_confirmation = true
```

The frontend must show a confirmation UI.

---

# 23. Emergency Response Does NOT Claim Live Availability

If a service is returned:

```json
{
  "availability_status": "UNKNOWN"
}
```

The UI should say:

```text
Availability unknown
```

not:

```text
Available now
```

unless backed by a real verified mechanism.

---

# 24. Places / Nearby Services API

## GET

```text
GET /api/v1/services/nearby
```

Query:

```text
latitude
longitude
category
radius_meters
limit
```

Example:

```text
/api/v1/services/nearby?latitude=22.7196&longitude=75.8577&category=HOSPITAL&radius_meters=5000&limit=10
```

---

# 25. Nearby Services Response

```json
{
  "success": true,
  "data": {
    "services": [],
    "center": {
      "latitude": 22.7196,
      "longitude": 75.8577
    },
    "radius_meters": 5000
  },
  "request_id": "req_123"
}
```

---

# 26. Service Search API

## POST

```text
POST /api/v1/services/search
```

Useful when filters become complex.

Request:

```json
{
  "location": {
    "latitude": 22.7196,
    "longitude": 75.8577,
    "accuracy_meters": 10,
    "timestamp": "2026-08-20T12:30:45Z"
  },
  "categories": [
    "HOSPITAL",
    "AMBULANCE"
  ],
  "radius_meters": 10000,
  "limit": 10,
  "sort": "RELEVANCE"
}
```

---

# 27. Service Detail

## GET

```text
GET /api/v1/services/{service_id}
```

Response:

```json
{
  "success": true,
  "data": {
    "service": {}
  },
  "request_id": "req_123"
}
```

---

# 28. Route API

## POST

```text
POST /api/v1/routes/plan
```

Request:

```json
{
  "origin": {
    "latitude": 22.7196,
    "longitude": 75.8577,
    "accuracy_meters": 8,
    "timestamp": "2026-08-20T12:30:45Z"
  },
  "destination": {
    "latitude": 23.2599,
    "longitude": 77.4126,
    "accuracy_meters": null,
    "timestamp": "2026-08-20T12:30:45Z"
  },
  "travel_mode": "DRIVE"
}
```

---

# 29. Route Response

```json
{
  "success": true,
  "data": {
    "route_id": "route_123",
    "origin": {},
    "destination": {},
    "distance_meters": 190000,
    "duration_seconds": 14400,
    "polyline": "...",
    "segments": []
  },
  "request_id": "req_123"
}
```

---

# 30. Offline Pack Creation API

## POST

```text
POST /api/v1/offline-packs
```

Purpose:

> Prepare a route-aware offline package.

Request:

```json
{
  "route_id": "route_123",
  "corridor_width_meters": 5000,
  "service_categories": [
    "HOSPITAL",
    "POLICE",
    "AMBULANCE",
    "TOWING",
    "PUNCTURE_REPAIR",
    "MECHANIC"
  ],
  "include_emergency_contacts": true,
  "include_rag": true,
  "language": "en"
}
```

---

# 31. Offline Pack Response

For a small package:

```json
{
  "success": true,
  "data": {
    "pack_id": "pack_123",
    "version": 1,
    "status": "READY",
    "size_bytes": 38200000,
    "download_url": "...",
    "checksum": "...",
    "created_at": "2026-08-20T12:30:45Z",
    "expires_at": "2026-08-27T12:30:45Z"
  },
  "request_id": "req_123"
}
```

If generation is asynchronous:

```text
202 Accepted
```

with:

```json
{
  "pack_id": "pack_123",
  "status": "PROCESSING"
}
```

---

# 32. Offline Pack Status

## GET

```text
GET /api/v1/offline-packs/{pack_id}
```

Response:

```json
{
  "success": true,
  "data": {
    "pack_id": "pack_123",
    "status": "READY",
    "version": 1,
    "size_bytes": 38200000,
    "checksum": "...",
    "created_at": "...",
    "expires_at": "..."
  },
  "request_id": "req_123"
}
```

---

# 33. Offline Pack Download

The actual binary/package download can use:

```text
GET /api/v1/offline-packs/{pack_id}/download
```

This may return:

```text
application/octet-stream
```

or a signed download URL.

The Flutter app must verify the checksum before activating the package.

---

# 34. RAG Query API

## POST

```text
POST /api/v1/rag/query
```

Request:

```json
{
  "query": "What should I do if someone is bleeding heavily?",
  "language": "en",
  "region": "India",
  "emergency_type": "severe_bleeding",
  "severity": "CRITICAL",
  "top_k": 5
}
```

---

# 35. RAG Response

```json
{
  "success": true,
  "data": {
    "answer": "...",
    "sources": [],
    "retrieval": {
      "method": "HYBRID",
      "reranked": true,
      "contexts_used": 5
    }
  },
  "request_id": "req_123"
}
```

Do not expose raw vector embeddings.

---

# 36. RAG Source Object

```json
{
  "source_id": "src_001",
  "title": "Official Emergency Guide",
  "authority_level": "OFFICIAL",
  "url": "https://example.com",
  "last_verified": "2026-08-20T00:00:00Z"
}
```

---

# 37. RAG Confidence

If returned:

```json
{
  "confidence": 0.91
}
```

the client should treat this as an informational signal, not a medical truth score.

The backend remains responsible for safety policy.

---

# 38. Voice API

The existing Sarvam architecture should eventually connect to the main emergency API.

Conceptual flow:

```text
Voice
 ↓
Sarvam STT
 ↓
text
 ↓
/emergency-assistance
 ↓
RAG + Places + Decision Engine
 ↓
response text
 ↓
Sarvam TTS
```

---

# 39. Voice Text Processing API

## POST

```text
POST /api/v1/voice/assist
```

Request:

```json
{
  "text": "Highway par tyre puncture ho gaya.",
  "language": "hi",
  "location": {},
  "network_mode": "ONLINE",
  "session_id": "sess_123"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "transcript": "Highway par tyre puncture ho gaya.",
    "response_text": "Please move to a safe location...",
    "emergency_assistance": {}
  },
  "request_id": "req_123"
}
```

The voice layer should not create a separate business-logic response format. It should reuse the emergency-assistance contract.

---

# 40. Audio Upload API

Only implement if required by the chosen Sarvam integration.

Possible:

```text
POST /api/v1/voice/transcribe
```

Input:

```text
multipart/form-data
audio=<file>
language=hi
```

Response:

```json
{
  "success": true,
  "data": {
    "transcript": "...",
    "language": "hi"
  },
  "request_id": "req_123"
}
```

Do not build this endpoint if Sarvam directly handles the required voice transport.

---

# 41. Agentic Action API

Agentic provider contact must have a strict permission boundary.

## POST

```text
POST /api/v1/actions/provider-contact
```

Request:

```json
{
  "service_id": "svc_123",
  "action": "CALL",
  "purpose": "Ask whether a mechanic can assist at the user's current location.",
  "location": {},
  "incident_id": "inc_123"
}
```

Backend response should initially be a **confirmation request**, not an automatic call.

```json
{
  "success": true,
  "data": {
    "action_id": "act_123",
    "status": "CONFIRMATION_REQUIRED",
    "message": "This action will contact the selected mechanic."
  },
  "request_id": "req_123"
}
```

---

# 42. Agentic Action Confirmation

## POST

```text
POST /api/v1/actions/{action_id}/confirm
```

Request:

```json
{
  "confirmed": true
}
```

Response:

```json
{
  "success": true,
  "data": {
    "action_id": "act_123",
    "status": "STARTED"
  },
  "request_id": "req_123"
}
```

The exact provider/voice infrastructure is implementation-dependent.

---

# 43. Action Status

## GET

```text
GET /api/v1/actions/{action_id}
```

Possible statuses:

```text
PENDING
CONFIRMATION_REQUIRED
STARTED
IN_PROGRESS
COMPLETED
FAILED
CANCELLED
```

---

# 44. Incident API

## POST

```text
POST /api/v1/incidents
```

Normally the main emergency endpoint can create an incident internally.

Manual creation is useful if the UI requires it.

Request:

```json
{
  "incident_type": "TYRE_PUNCTURE",
  "severity": "MEDIUM",
  "location": {},
  "description": "Tyre punctured on highway."
}
```

---

# 45. Incident Detail

## GET

```text
GET /api/v1/incidents/{incident_id}
```

Response:

```json
{
  "success": true,
  "data": {
    "incident_id": "inc_123",
    "incident_type": "TYRE_PUNCTURE",
    "severity": "MEDIUM",
    "status": "ACTIVE",
    "location": {},
    "created_at": "...",
    "updated_at": "..."
  },
  "request_id": "req_123"
}
```

---

# 46. Incident Status

Possible:

```text
ACTIVE
ASSISTANCE_REQUESTED
RESOLVED
CANCELLED
```

---

# 47. Sync API

Offline clients need a controlled way to synchronize when connectivity returns.

## POST

```text
POST /api/v1/sync
```

Request:

```json
{
  "device_id": "device_123",
  "app_version": "1.0.0",
  "offline_pack_versions": [
    {
      "pack_id": "pack_123",
      "version": 1
    }
  ]
}
```

Response:

```json
{
  "success": true,
  "data": {
    "updates_available": [
      {
        "pack_id": "pack_123",
        "latest_version": 2
      }
    ]
  },
  "request_id": "req_123"
}
```

---

# 48. Client Responsibilities

## React

Responsible for:

- Firebase login
- storing authentication state
- obtaining Firebase ID token
- sending `Authorization`
- rendering API responses
- validating basic form input
- handling loading/error states
- never implementing backend business rules independently

## Flutter

Responsible for:

- Firebase login
- token persistence
- GPS
- network state
- offline package storage
- local AI
- local service search
- rendering API responses
- retry/sync

## FastAPI

Responsible for:

- authoritative validation
- authentication verification
- business logic
- incident classification
- service selection
- RAG
- Google API calls
- AI orchestration
- security
- database access

---

# 49. Frontend API Client Rule

React should have a single API client.

Concept:

```text
src/
└── api/
    ├── client.ts
    ├── auth.ts
    ├── emergency.ts
    ├── services.ts
    ├── routes.ts
    ├── rag.ts
    └── offline.ts
```

Do NOT scatter:

```text
fetch(...)
axios(...)
```

through UI components.

---

# 50. Flutter API Client Rule

Flutter should similarly have:

```text
lib/
└── services/
    ├── api_client.dart
    ├── auth_service.dart
    ├── emergency_service.dart
    ├── services_service.dart
    ├── route_service.dart
    ├── offline_service.dart
    └── voice_service.dart
```

UI widgets should not construct raw HTTP requests.

---

# 51. API Client Responsibilities

Every client API wrapper should handle:

```text
base URL
headers
auth token
serialization
deserialization
timeouts
HTTP errors
retry policy
request ID
```

---

# 52. Timeout Rules

Suggested starting defaults:

```text
normal API: 10–15 seconds
Google search: 10–15 seconds
RAG: 20–30 seconds
LLM: 30 seconds
offline local inference: application-controlled
offline package download: longer / resumable if implemented
```

Tune based on measurements.

Do not let a voice request hang indefinitely.

---

# 53. Retry Rules

Retry only safe/idempotent operations automatically.

Good candidates:

```text
GET services
GET route
GET pack status
```

Be careful with:

```text
POST provider contact
POST payment/action
POST external side effect
```

Never blindly retry an action that may cause duplicate calls.

---

# 54. Idempotency

For side-effecting POST requests, support:

```http
Idempotency-Key: <uuid>
```

especially:

```text
provider-contact
incident creation
other external actions
```

Backend stores/reuses the result for repeated requests.

---

# 55. Request IDs

Every request should have a server-generated request ID.

Example:

```text
req_01J...
```

Return it in:

```json
{
  "request_id": "req_01J..."
}
```

This makes hackathon debugging much easier.

When Santosh says:

> “The service API is failing.”

we can trace:

```text
request_id
```

through FastAPI logs.

---

# 56. Serialization Rules

Use:

```text
snake_case
```

for JSON.

Correct:

```json
{
  "incident_type": "TYRE_PUNCTURE",
  "distance_meters": 1200
}
```

Do not mix:

```text
incidentType
distanceMeters
```

between clients.

---

# 57. Null Rules

Use `null` when information is genuinely unknown.

Example:

```json
{
  "phone": null,
  "is_open": null,
  "availability_status": "UNKNOWN"
}
```

Do not use:

```text
""
"unknown"
-1
0
```

to represent missing data unless explicitly defined.

---

# 58. Date Rules

Use UTC ISO-8601:

```text
2026-08-20T12:30:45Z
```

React and Flutter convert to local display time.

Backend/database storage should remain consistent.

---

# 59. Enum Rules

Never send free-text values where an enum exists.

Bad:

```json
{
  "severity": "very serious"
}
```

Good:

```json
{
  "severity": "CRITICAL"
}
```

---

# 60. Validation Ownership

There are three layers.

## Layer 1 — UI

Basic validation:

```text
empty message
invalid coordinates
missing required field
```

## Layer 2 — API client

Serialization/type validation.

## Layer 3 — FastAPI

Authoritative validation.

Backend must never trust the client.

---

# 61. Pydantic Models

FastAPI should define explicit request/response models.

Example:

```python
class EmergencyAssistanceRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: LanguageCode = "en"
    location: Location
    network_mode: NetworkMode
    include_services: bool = True
    service_categories: list[ServiceCategory] = []
    max_services: int = Field(default=5, ge=1, le=20)
    session_id: str | None = None
```

Response models should also be explicit.

Do not return arbitrary dictionaries everywhere.

---

# 62. OpenAPI as the Contract

FastAPI automatically generates OpenAPI.

The team should treat:

```text
/openapi.json
/docs
```

as the technical API reference.

The `.md` file defines the intended contract; OpenAPI validates the actual implementation.

---

# 63. Contract-First Workflow

Before implementing an endpoint:

```text
1. Define request schema
2. Define response schema
3. Define error schema
4. Add Pydantic models
5. Add OpenAPI documentation
6. Share example payload
7. React builds against contract
8. Flutter builds against contract
9. Backend implements
10. Integration test
```

This prevents the classic:

> “I thought the response was `services`, but he made it `results`.”

problem.

---

# 64. Shared Contract Repository

Recommended project structure:

```text
contracts/
├── README.md
├── enums.md
├── errors.md
├── emergency.md
├── services.md
├── routes.md
├── rag.md
├── voice.md
├── offline.md
└── actions.md
```

If practical, generate TypeScript/Dart types from OpenAPI rather than manually duplicating them.

---

# 65. Type Generation

Recommended direction:

```text
FastAPI Pydantic
      ↓
OpenAPI
      ↓
Generated client/types
      ├── React TypeScript
      └── Flutter Dart
```

This is preferable to manually maintaining:

```text
Python model
+
TypeScript interface
+
Dart model
```

independently.

---

# 66. Example TypeScript Model

Conceptual:

```ts
export interface Location {
  latitude: number;
  longitude: number;
  accuracy_meters?: number | null;
  timestamp: string;
}

export interface EmergencyAssistanceRequest {
  message: string;
  language: LanguageCode;
  location: Location;
  network_mode: NetworkMode;
  include_services: boolean;
  service_categories?: ServiceCategory[];
  max_services?: number;
  session_id?: string | null;
}
```

Generated types are preferable in the actual project.

---

# 67. Example Dart Model

Conceptual:

```dart
class Location {
  final double latitude;
  final double longitude;
  final double? accuracyMeters;
  final DateTime timestamp;
}
```

Serialization should map exactly to:

```text
latitude
longitude
accuracy_meters
timestamp
```

Internally Dart can use camelCase, but JSON remains snake_case.

---

# 68. API Contract Test

For every important endpoint, maintain:

```text
valid request
invalid request
valid response
error response
```

Example:

```text
POST /emergency-assistance
```

Test:

1. valid puncture
2. missing message
3. invalid latitude
4. unsupported language
5. too many services
6. missing authentication

---

# 69. Integration Test Matrix

| Endpoint | React | Flutter | Backend | Priority |
|---|---|---|---|---|
| health | — | — | ✓ | P0 |
| users/me | ✓ | ✓ | ✓ | P1 |
| emergency-assistance | ✓ | ✓ | ✓ | P0 |
| services/nearby | ✓ | ✓ | ✓ | P0 |
| routes/plan | ✓ | ✓ | ✓ | P1 |
| rag/query | dev | dev | ✓ | P1 |
| voice/assist | ✓ | ✓ | ✓ | P1 |
| offline-packs | ✓ | ✓ | ✓ | P1 |
| incidents | ✓ | ✓ | ✓ | P2 |
| provider-contact | ✓ | ✓ | ✓ | P2 |
| sync | — | ✓ | ✓ | P1 |

---

# 70. P0 APIs

These should be implemented first:

```text
GET  /api/v1/health

GET  /api/v1/users/me

POST /api/v1/emergency-assistance

GET  /api/v1/services/nearby

POST /api/v1/services/search
```

The goal:

```text
React
   ↓
FastAPI
   ↓
Google Places
   ↓
response

Flutter
   ↓
FastAPI
   ↓
Google Places
   ↓
response
```

---

# 71. P1 APIs

After P0:

```text
POST /api/v1/routes/plan

POST /api/v1/rag/query

POST /api/v1/voice/assist

POST /api/v1/offline-packs

GET  /api/v1/offline-packs/{id}

GET  /api/v1/offline-packs/{id}/download

POST /api/v1/sync
```

---

# 72. P2 APIs

Only after the core system works:

```text
POST /api/v1/incidents

GET /api/v1/incidents/{id}

POST /api/v1/actions/provider-contact

POST /api/v1/actions/{id}/confirm

GET /api/v1/actions/{id}
```

Do not let P2 features block the core demo.

---

# 73. API Dependency Graph

```text
Firebase
   │
   ▼
Authentication
   │
   ▼
FastAPI
   │
   ├──────────────┐
   ▼              ▼
Emergency       Services
   │              │
   ├──────┬───────┘
   │      │
   ▼      ▼
  RAG   Google
   │    Places
   │      │
   └──┬───┘
      ▼
Decision Engine
      │
      ▼
Response
```

Routes:

```text
Route Planning
      ↓
Offline Pack
      ↓
Flutter Local Storage
      ↓
Offline AI
```

Voice:

```text
Sarvam
 ↓
Voice Assist
 ↓
Emergency Assistance
```

---

# 74. Example End-to-End Puncture Request

Client sends:

```json
{
  "message": "My tyre got punctured on the highway.",
  "language": "en",
  "location": {
    "latitude": 22.7196,
    "longitude": 75.8577,
    "accuracy_meters": 8,
    "timestamp": "2026-08-20T12:30:45Z"
  },
  "network_mode": "ONLINE",
  "include_services": true,
  "service_categories": [
    "PUNCTURE_REPAIR",
    "MECHANIC",
    "TOWING"
  ],
  "max_services": 5
}
```

Backend:

```text
verify Firebase
      ↓
validate Pydantic
      ↓
classify incident
      ↓
determine service categories
      ↓
Google Places
      ↓
RAG guidance
      ↓
rank services
      ↓
build response
```

Response:

```text
incident
+
guidance
+
services
+
actions
+
AI metadata
```

---

# 75. Example Accident + Hospital Request

Request:

```json
{
  "message": "There has been an accident and my friend is bleeding badly.",
  "language": "en",
  "location": {
    "latitude": 22.7196,
    "longitude": 75.8577,
    "accuracy_meters": 6,
    "timestamp": "2026-08-20T12:30:45Z"
  },
  "network_mode": "ONLINE",
  "include_services": true,
  "service_categories": [
    "HOSPITAL",
    "AMBULANCE",
    "POLICE"
  ],
  "max_services": 5
}
```

Backend should produce:

```text
incident = ACCIDENT
severity = CRITICAL
guidance = verified bleeding/accident guidance
services = nearby hospitals/ambulance/police
actions = emergency contact/navigation
```

---

# 76. Offline API Boundary

When Flutter is offline:

```text
Do NOT call:
POST /emergency-assistance
```

Instead:

```text
LocalAIService.assist(...)
```

The offline service should return a response shaped similarly to the online response.

This means the UI does not need two completely different renderers.

---

# 77. Offline Response Contract

```json
{
  "success": true,
  "data": {
    "incident": {},
    "guidance": {},
    "services": [],
    "recommended_actions": [],
    "ai": {
      "mode": "OFFLINE",
      "model": "gemma",
      "rag_used": true
    },
    "limitations": [
      "Provider information is cached and may be outdated.",
      "Live availability cannot be verified offline."
    ]
  },
  "request_id": null
}
```

`request_id` may be null because no server request occurred.

---

# 78. Online/Offline UI Rule

The response must expose:

```text
ai.mode
```

Possible:

```text
ONLINE
OFFLINE
FALLBACK
```

The UI can show:

```text
Powered by RAAHAT
Offline mode
```

without changing its fundamental layout.

---

# 79. Voice Integration Rule

Voice should be a transport layer.

Do not build:

```text
voice business logic
```

separately from:

```text
text business logic
```

Instead:

```text
Voice
 ↓
Transcript
 ↓
same Emergency Assistance API
```

This guarantees:

```text
text and voice produce the same backend behavior.
```

---

# 80. Sarvam Integration Boundary

Sarvam should communicate with:

```text
/api/v1/voice/assist
```

or directly with the already established FastAPI voice endpoint.

The business layer should receive normalized text:

```json
{
  "text": "...",
  "language": "hi"
}
```

The backend then calls:

```text
Emergency Orchestrator
```

Do not duplicate RAG/Places logic inside the voice layer.

---

# 81. Agentic Action Safety Contract

Any action with external side effects must follow:

```text
AI proposes action
      ↓
Backend creates action
      ↓
User confirmation
      ↓
Execution
      ↓
Status
```

Never:

```text
LLM
 ↓
automatically call random provider
```

The frontend must clearly display:

```text
Who will be contacted
Why
What information will be shared
Confirmation button
```

---

# 82. Data Privacy Rule

Do not send unnecessary information to:

- Google
- Groq
- Sarvam
- external providers

For example, provider contact action should send only the information necessary for the action.

---

# 83. Backend Logging

Log:

```text
request_id
endpoint
authenticated uid
status code
latency
upstream provider
error code
```

Avoid logging:

- Firebase tokens
- API keys
- raw sensitive user data
- unnecessary exact location history

---

# 84. Error Code Catalog

Use stable machine-readable codes.

Examples:

```text
AUTH_REQUIRED
AUTH_INVALID
VALIDATION_ERROR
INVALID_COORDINATES
UNSUPPORTED_LANGUAGE
INCIDENT_NOT_FOUND
SERVICE_NOT_FOUND
NO_SERVICES_FOUND
GOOGLE_PLACES_ERROR
GOOGLE_ROUTES_ERROR
RAG_UNAVAILABLE
RAG_NO_RELEVANT_CONTEXT
LLM_UNAVAILABLE
VOICE_UNAVAILABLE
OFFLINE_PACK_NOT_FOUND
OFFLINE_PACK_INVALID
OFFLINE_PACK_EXPIRED
ACTION_CONFIRMATION_REQUIRED
ACTION_FAILED
RATE_LIMITED
INTERNAL_ERROR
```

Frontend behavior should depend on `code`, not on English `message`.

---

# 85. Error Handling Example

Backend:

```json
{
  "success": false,
  "error": {
    "code": "NO_SERVICES_FOUND",
    "message": "No relevant services were found nearby.",
    "details": {
      "category": "PUNCTURE_REPAIR",
      "radius_meters": 5000
    }
  },
  "request_id": "req_123"
}
```

React:

```text
if code == NO_SERVICES_FOUND:
    show "No nearby service found"
```

Not:

```text
if message.includes("No relevant")
```

---

# 86. Pagination

For normal lists:

```text
page
page_size
total
```

But nearby services should usually use:

```text
limit
```

rather than traditional pagination because the user is requesting geographically relevant top results.

---

# 87. Sorting

Service API may support:

```text
DISTANCE
RELEVANCE
RATING
```

Backend should determine the actual ranking.

The frontend should not re-rank the services independently.

---

# 88. Google API Boundary

Frontend should ideally NOT contain secret Google server keys for server-side APIs.

Recommended:

```text
React / Flutter
      ↓
FastAPI
      ↓
Google Places / Routes
```

If a client-side Google Maps SDK requires a client-restricted key, keep it separately restricted and never reuse server credentials.

---

# 89. RAG API Boundary

Frontend should normally call:

```text
/emergency-assistance
```

rather than manually combining:

```text
/rag/query
+
/services/nearby
```

The direct RAG endpoint is primarily useful for:

- development
- testing
- evaluation
- internal debugging

The orchestrator should compose the final user experience.

---

# 90. Database ↔ API Rule

Database models are internal.

Never expose database rows directly.

Bad:

```python
return db_service
```

Good:

```text
DB model
 ↓
service mapper
 ↓
ServiceResponse
```

This prevents database schema changes from breaking frontend clients.

---

# 91. API Contract Freeze

Before the team starts parallel frontend/backend development:

```text
Freeze P0 contracts.
```

After freezing:

- changes require team agreement
- breaking changes require version/schema update
- update OpenAPI
- update generated clients
- update test fixtures

---

# 92. Breaking vs Non-Breaking Changes

## Usually non-breaking

Adding an optional response field:

```json
{
  "new_optional_field": null
}
```

## Potentially breaking

Changing:

```text
incident_type
```

from:

```text
TYRE_PUNCTURE
```

to:

```text
PUNCTURE
```

Changing:

```text
services: []
```

to:

```text
results: []
```

Changing required request fields.

---

# 93. API Integration Checklist

Before declaring an endpoint complete:

- [ ] Request model exists
- [ ] Response model exists
- [ ] Pydantic validation exists
- [ ] OpenAPI generated
- [ ] Example request documented
- [ ] Example response documented
- [ ] Error responses documented
- [ ] Auth requirement documented
- [ ] React client implemented
- [ ] Flutter client implemented
- [ ] Backend test exists
- [ ] Integration test exists
- [ ] Invalid payload tested
- [ ] Request ID logged
- [ ] Timeout configured
- [ ] Error code defined

---

# 94. Daily Team Integration Rule

Every time an API changes:

```text
1. Tell team
2. Update Pydantic schema
3. Update OpenAPI
4. Update this contract
5. Update example JSON
6. Update React types
7. Update Flutter model
8. Run contract tests
```

Do not silently change payloads.

---

# 95. Recommended Git Workflow

Create:

```text
contracts/
```

and protect it.

Suggested branches:

```text
feature/api-emergency-contract
feature/react-emergency-client
feature/flutter-emergency-client
feature/rag
feature/offline
```

Before merging a backend contract change:

```text
React + Flutter compatibility check
```

---

# 96. P0 Integration Milestone

The first integration milestone should be:

```text
Firebase Auth
       ↓
React
       ↓
POST /emergency-assistance
       ↓
FastAPI
       ↓
Mock incident + mock services
       ↓
React renders response
```

AND:

```text
Firebase Auth
       ↓
Flutter
       ↓
POST /emergency-assistance
       ↓
FastAPI
       ↓
same response schema
       ↓
Flutter renders response
```

Once both clients can consume the same response, replace mocks with real AI/Places.

---

# 97. P1 Integration Milestone

```text
React + Flutter
        ↓
Emergency API
        ↓
Incident classifier
        ↓
RAG
        ↓
Google Places
        ↓
Service ranking
        ↓
Unified response
```

---

# 98. P2 Integration Milestone

```text
Flutter
 ↓
offline detected
 ↓
LocalAIService
 ↓
Local RAG
 ↓
Gemma
 ↓
same response schema
 ↓
same UI components
```

---

# 99. P3 Integration Milestone

```text
Voice
 ↓
Sarvam
 ↓
transcript
 ↓
Emergency API
 ↓
RAAHAT
 ↓
response
 ↓
Sarvam TTS
```

---

# 100. P4 Integration Milestone

```text
AI Agent
 ↓
proposed provider action
 ↓
confirmation
 ↓
provider contact
 ↓
action status
```

---

# 101. The One Contract That Matters Most

The team should freeze this first:

```text
POST /api/v1/emergency-assistance
```

Because it becomes the common contract between:

```text
React
Flutter
Voice
Online AI
Offline AI
RAG
Places
Decision Engine
```

Everything else can evolve around it.

---

# 102. Final Architecture

```text
                         ┌──────────────┐
                         │   FIREBASE   │
                         │     AUTH     │
                         └──────┬───────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
          REACT              FLUTTER            SARVAM
             │                  │                  │
             │                  │              transcript
             │                  │                  │
             └──────────┬───────┴──────────────────┘
                        ▼
                 FASTAPI /api/v1
                        │
               ┌────────┼─────────┐
               │        │         │
               ▼        ▼         ▼
          Validation   Auth     Router
                                │
               ┌────────────────┼─────────────────┐
               │                │                 │
               ▼                ▼                 ▼
          Emergency          Routes            Services
          Assistance                             │
               │                                 │
        ┌──────┼──────┐                          ▼
        ▼      ▼      ▼                    Google Places
       RAG    LLM   Decision
               │      Engine
               └──┬───┘
                  ▼
             Unified Response
                  │
          ┌───────┴────────┐
          ▼                ▼
       React             Flutter
                            │
                      if offline
                            ▼
                     Local AI Service
                       │         │
                    Local RAG  Gemma
                       │         │
                       └────┬────┘
                            ▼
                       Same response
                         contract
```

---

# 103. Final Rulebook

### Rule 1
**FastAPI/Pydantic is the authoritative schema.**

### Rule 2
**OpenAPI is the machine-readable contract.**

### Rule 3
**React and Flutter never invent field names.**

### Rule 4
**Use snake_case in JSON.**

### Rule 5
**Use enums instead of free text.**

### Rule 6
**Use null for genuinely unknown values.**

### Rule 7
**Use ISO-8601 UTC timestamps.**

### Rule 8
**Never reverse latitude/longitude.**

### Rule 9
**Never expose database rows directly.**

### Rule 10
**Never let the frontend implement backend ranking/business rules.**

### Rule 11
**Never treat unknown service availability as false or true.**

### Rule 12
**Never automatically retry external side-effect actions.**

### Rule 13
**Use request IDs everywhere.**

### Rule 14
**Freeze P0 contracts before parallel development.**

### Rule 15
**Every contract change must update backend + React + Flutter + tests.**

### Rule 16
**Voice is a transport layer, not a second business-logic system.**

### Rule 17
**Offline AI returns the same conceptual response shape as online AI.**

### Rule 18
**RAG and Google APIs remain backend subsystems; clients consume their results through the main orchestration API.**

---

# 104. Final Objective

The purpose of this API architecture is simple:

> **A developer should be able to open this document, copy the request/response schema, implement their client, and know exactly what FastAPI expects and exactly what FastAPI will return.**

If that remains true throughout the hackathon, the team avoids one of the most common causes of integration failure:

```text
Backend says:
"services"

Frontend expects:
"results"

Flutter expects:
"nearby_services"

Backend sends:
"recommended_services"
```

RAAHAT should have **one canonical contract**.

```text
             ONE CONTRACT
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
     React      Flutter    Voice
       │          │          │
       └──────────┼──────────┘
                  ▼
               FastAPI
                  │
          ┌───────┼────────┐
          ▼       ▼        ▼
         RAG    Places    AI
                  │
                  ▼
          Unified Response
```

**Contract first. Code second. Integration third.**
