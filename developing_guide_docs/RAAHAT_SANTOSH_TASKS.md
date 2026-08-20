# RAAHAT — Santosh Task & Execution Plan

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Team:** Solution Savvy  
**Team Member:** Santosh Ray  
**Primary Domains:** React Web + FastAPI Core Backend + Maps/Places/Routes Integration + System Integration + Deployment Research

---

# 1. Purpose

This is Santosh's personal execution guide for RAAHAT.

It is intended to be provided to Santosh's AI coding/research assistant together with the common project documents:

- RAAHAT PRD
- Complete feature/functionality document
- System architecture document
- RAG architecture document
- Offline AI architecture document
- API Contracts & Integration Guide

Those documents explain the whole product.

This document explains:

- what Santosh owns
- what he should build first
- what he should research
- what he must deliver to Satwik and Saanvi
- what dependencies exist
- how his phases synchronize with theirs
- how to avoid blocking the rest of the team

---

# 2. Team Context

## Team

**Solution Savvy**

## Members

### Satwik Misra

Primary areas:

- AI development
- RAG
- AI orchestration
- FastAPI AI integration
- LLM integrations
- Sarvam
- Gemma/offline AI
- Agentic AI
- PostgreSQL
- Firebase
- AI evaluation

### Santosh Ray

Primary areas:

- React
- FastAPI core backend
- API implementation
- Google Maps / Places / Routes integration
- alternative API research
- frontend/backend integration
- system integration
- deployment

### Saanvi Gupta

Primary areas:

- research
- Flutter
- mobile application
- RAG knowledge/data research
- offline package preparation
- offline AI integration support
- mobile testing

---

# 3. Santosh's Core Mission

Santosh owns the **application/platform layer** of RAAHAT.

His responsibility is to make sure:

```text
React Web
    ↓
FastAPI
    ↓
External APIs / PostgreSQL / Firebase verification
    ↓
AI/RAG services
    ↓
Unified API responses
```

works reliably.

His second major responsibility is:

> **Make sure RAAHAT does not collapse if a planned external API is unavailable.**

Therefore, Google Maps / Places / Routes research must include viable alternatives.

---

# 4. What Santosh Does NOT Own

Do not independently take ownership of:

- core RAG architecture
- final RAG retrieval strategy
- LLM orchestration
- Gemma model architecture
- AI evaluation
- PostgreSQL architecture
- Firebase backend architecture
- Sarvam AI design
- final offline AI architecture

These are primarily Satwik's responsibilities.

Santosh integrates them through agreed contracts.

---

# 5. Phase Overview

```text
PHASE 0
Architecture + environment + contract understanding
        ↓
PHASE 1
React foundation + FastAPI foundation + Maps/API research
        ↓
PHASE 2
Core backend + external API integration + React integration
        ↓
PHASE 3
AI/RAG integration + full web integration
        ↓
PHASE 4
System hardening + fallback APIs + testing
        ↓
PHASE 5
Deployment + final integration + demo preparation
```

The phases intentionally overlap with Satwik and Saanvi.

---

# 6. Dependency Philosophy

Santosh must work in a way that prevents this:

```text
Satwik waiting for backend
Saanvi waiting for API
Santosh waiting for RAG
```

Instead:

```text
PHASE 1
API contracts + mock services + backend skeleton
             ↓
PHASE 2
real service integration

Satwik can build AI independently
Saanvi can build Flutter against the contracts
             ↓
PHASE 3
everyone integrates
```

---

# PHASE 0 — UNDERSTANDING + SETUP

## Goal

Become fully aligned with the project's architecture and API contracts before implementation.

---

# 7. Read All Common Documents

Santosh's AI assistant should receive:

1. PRD
2. complete feature/functionality document
3. architecture document
4. RAG architecture document
5. offline AI architecture document
6. API Contracts & Integration Guide

The AI assistant must understand:

```text
React
 ↓
FastAPI
 ↓
PostgreSQL
 ↓
Firebase Authentication
 ↓
Google APIs
 ↓
RAG / AI
 ↓
Flutter client
```

---

# 8. Freeze API Contract Understanding

The API contract document is authoritative.

Santosh must understand at minimum:

```text
GET  /api/v1/health

GET  /api/v1/users/me

POST /api/v1/emergency-assistance

GET  /api/v1/services/nearby

POST /api/v1/services/search

POST /api/v1/routes/plan

POST /api/v1/rag/query

POST /api/v1/voice/assist

POST /api/v1/offline-packs

POST /api/v1/sync
```

P0 APIs must be prioritized over advanced features.

---

# 9. Backend Environment

Set up:

- Python
- FastAPI
- Uvicorn
- Pydantic
- PostgreSQL client/ORM
- Firebase Admin SDK
- environment variable handling
- HTTP client
- testing framework

Suggested:

```text
FastAPI
Pydantic
SQLAlchemy
PostgreSQL
Firebase Admin
httpx
pytest
```

Exact libraries may be changed if the team agrees.

---

# 10. Backend Structure

Suggested:

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── health.py
│   │       ├── users.py
│   │       ├── emergency.py
│   │       ├── services.py
│   │       ├── routes.py
│   │       ├── rag.py
│   │       ├── voice.py
│   │       ├── offline.py
│   │       └── actions.py
│   │
│   ├── schemas/
│   ├── models/
│   ├── services/
│   └── repositories/
│
├── tests/
├── requirements.txt
└── README.md
```

Do not overengineer the structure during the hackathon.

---

# PHASE 1 — REACT + FASTAPI FOUNDATION + API RESEARCH

## Goal

By the end of Phase 1:

```text
React app running
FastAPI running
API contracts implemented
Firebase verification skeleton ready
PostgreSQL connection ready
Maps/Places research complete
Google alternatives identified
Mock responses available
```

---

# 11. React Application Foundation

Build the web application shell.

Suggested pages:

```text
Landing / Home
Login
Emergency Assistance
Nearby Services
Route Planner
Emergency Details
Offline Information
Profile / Settings
```

The web version does not need to reproduce every mobile feature immediately.

---

# 12. React UI Priorities

P0:

```text
Home
Emergency Assistance
Nearby Services
Emergency result
```

P1:

```text
Route Planner
Service details
Profile
```

P2:

```text
Advanced/optional features
```

---

# 13. React Architecture

Suggested:

```text
src/
├── api/
├── components/
├── pages/
├── hooks/
├── models/
├── utils/
├── auth/
└── App.tsx
```

Use a centralized API client.

Do NOT scatter raw:

```text
fetch()
axios()
```

through components.

---

# 14. React API Client

The API client must handle:

```text
base URL
Firebase token
Authorization
JSON serialization
errors
timeouts
request IDs
```

Example:

```text
apiClient
   ↓
emergencyApi
servicesApi
routesApi
```

---

# 15. FastAPI Health Endpoint

Implement first:

```text
GET /api/v1/health
```

It should verify basic system status.

Use it to test:

```text
React → FastAPI
```

and later:

```text
deployment → FastAPI
```

---

# 16. Firebase Authentication Integration

Santosh supports the backend integration.

Flow:

```text
React
 ↓
Firebase Authentication
 ↓
ID Token
 ↓
Authorization: Bearer <token>
 ↓
FastAPI
 ↓
Firebase Admin verification
 ↓
authenticated user
```

Important:

> Firebase authentication ownership remains shared with Satwik, but Santosh owns making the FastAPI/React integration work.

Do not invent a second authentication mechanism.

---

# 17. PostgreSQL Integration Boundary

PostgreSQL ownership belongs primarily to Satwik.

Santosh should therefore:

- understand the required API data
- create repository interfaces if needed
- consume agreed database models
- avoid silently changing the schema
- coordinate schema changes with Satwik

Do not create an independent competing data model.

---

# PHASE 1B — GOOGLE API RESEARCH

This is an important responsibility.

---

# 18. Google Maps / Places / Routes Research

Research exactly which Google APIs are needed.

Likely categories:

```text
Places
Routes
Maps visualization
Geocoding if required
```

Determine:

```text
API availability
pricing
quotas
authentication
request limits
required fields
response structure
India coverage
```

The goal is not simply:

> “Google Maps works.”

The goal is:

> “We know exactly what RAAHAT needs from Google, how to call it, and what happens if we cannot use it.”

---

# 19. Google API Requirements

Research how to obtain:

### Nearby services

```text
Hospital
Police
Ambulance
Towing
Puncture Repair
Mechanic
Vehicle Service
Fuel Station
```

### Routing

Need:

```text
origin
destination
distance
duration
route geometry/polyline
```

### Map display

Need:

```text
map
markers
route
user location
```

---

# 20. Alternative API Research

This is explicitly part of Santosh's responsibility.

If Google APIs are unavailable because of:

```text
API key problem
quota
pricing
rate limit
service restriction
network issue
hackathon environment
```

RAAHAT must have alternatives researched.

Investigate suitable alternatives such as:

```text
OpenStreetMap
Overpass API
OSRM
GraphHopper
openrouteservice
Geoapify
Mapbox
HERE
TomTom
```

Do not assume every alternative is equally suitable.

Evaluate each for:

```text
India coverage
free tier
commercial/demo restrictions
places/search capability
routing
distance
geocoding
rate limits
API key requirement
ease of integration
response quality
```

---

# 21. Alternative API Decision Matrix

Create a table:

| Provider | Places | Routing | India | Free option | Key required | Rate limits | Best use |
|---|---|---|---|---|---|---|---|
| Google | ✓ | ✓ | ✓ | Limited/conditional | ✓ | Yes | Primary |
| OSM/Overpass | ✓* | — | ✓ | ✓ | Usually no | Yes | POI fallback |
| OSRM | — | ✓ | ✓ | ✓/self-host | Depends | Yes | Routing |
| openrouteservice | —/limited | ✓ | ✓ | ✓ | ✓ | Yes | Routing fallback |
| Geoapify | ✓ | ✓ | ✓ | ✓ | ✓ | Yes | Combined fallback |
| Mapbox | ✓ | ✓ | ✓ | Conditional | ✓ | Yes | Alternative |
| HERE | ✓ | ✓ | ✓ | Conditional | ✓ | Yes | Alternative |

`*` OSM/Overpass is based on community-mapped POI data and should not be treated as identical to Google Places.

The final choice must be based on actual availability and hackathon constraints.

---

# 22. Recommended Fallback Strategy

The architecture should not hard-code:

```text
RAAHAT → Google only
```

Instead:

```text
Provider Interface
      │
      ├── GoogleProvider
      ├── OSMProvider
      ├── RoutingFallbackProvider
      └── OtherProvider
```

Then:

```text
Service Search
      ↓
Primary provider
      ↓ failure
Fallback provider
      ↓
Normalize response
      ↓
RAAHAT Service schema
```

This is much more robust.

---

# 23. Provider-Normalization Rule

Google and alternative providers will return different schemas.

Do NOT send their raw responses directly to React/Flutter.

Instead:

```text
Google response
        ↓
                   ┌──→ Unified Service
OSM response ──────┤
        ↓           │
Other response ────┘
```

Canonical output:

```json
{
  "service_id": "svc_123",
  "name": "ABC Hospital",
  "category": "HOSPITAL",
  "location": {
    "latitude": 22.7196,
    "longitude": 75.8577
  },
  "address": "...",
  "phone": null,
  "distance_meters": 1200,
  "source": "GOOGLE_PLACES",
  "is_cached": false
}
```

---

# PHASE 1C — MOCK-FIRST DEVELOPMENT

This prevents dependency blocking.

---

# 24. Mock Emergency Endpoint

Implement:

```text
POST /api/v1/emergency-assistance
```

initially with controlled mock intelligence if Satwik's AI service is not ready.

Example:

```json
{
  "success": true,
  "data": {
    "incident": {
      "incident_type": "TYRE_PUNCTURE",
      "severity": "MEDIUM",
      "confidence": 0.95,
      "summary": "Vehicle has a tyre puncture."
    },
    "guidance": {
      "title": "Stay safe",
      "steps": [
        "Move to a safe location.",
        "Turn on hazard lights."
      ]
    },
    "services": []
  },
  "request_id": "req_demo"
}
```

This allows:

```text
React development
Flutter development
```

to proceed.

---

# 25. Mock Services Endpoint

Implement:

```text
GET /api/v1/services/nearby
```

using mock data initially.

Use the exact production response schema.

Do not change:

```text
services
```

to another name later.

---

# 26. Mock Route Endpoint

Implement:

```text
POST /api/v1/routes/plan
```

using mock route data if Google integration is not ready.

This lets:

```text
Saanvi → Flutter route UI
Santosh → React route UI
```

develop simultaneously.

---

# PHASE 2 — CORE BACKEND + REAL EXTERNAL APIs

## Goal

Move from:

```text
mock
```

to:

```text
real services
```

without changing the public API contracts.

---

# 27. Google Places Integration

Implement the service provider layer.

Required behavior:

```text
location
+
categories
+
radius
        ↓
Google Places
        ↓
normalize
        ↓
ServiceResponse
```

---

# 28. Service Ranking

Backend should handle ranking.

Potential factors:

```text
distance
relevance
category match
availability when known
data quality
source reliability
```

Do not let React/Flutter independently rank results.

---

# 29. Google Routes Integration

Implement:

```text
POST /api/v1/routes/plan
```

Backend:

```text
validate coordinates
 ↓
Google Routes
 ↓
normalize
 ↓
RouteResponse
```

---

# 30. Fallback Provider Integration

At least one viable fallback should be technically proven before final integration.

The exact fallback depends on:

```text
API availability
quota
internet
hackathon constraints
```

Do not wait until the final demo to discover that the fallback doesn't work.

---

# 31. External API Failure Handling

If Google fails:

```text
Google
 ↓ error
fallback provider
 ↓
normalize
 ↓
return result
```

If all providers fail:

```text
return cached/local result if available
```

If no data exists:

```text
NO_SERVICES_FOUND
```

Do not fabricate providers.

---

# 32. Backend API Error Contracts

Use stable error codes:

```text
AUTH_REQUIRED
AUTH_INVALID
VALIDATION_ERROR
GOOGLE_PLACES_ERROR
GOOGLE_ROUTES_ERROR
NO_SERVICES_FOUND
UPSTREAM_PROVIDER_ERROR
RATE_LIMITED
INTERNAL_ERROR
```

React and Flutter should rely on codes, not English messages.

---

# PHASE 3 — AI/RAG INTEGRATION

## Goal

Connect Satwik's AI layer to the platform without rewriting backend contracts.

---

# 33. AI Boundary

Santosh should expect Satwik's AI system to expose a normalized interface.

Concept:

```text
FastAPI
  ↓
Emergency Orchestrator
  ↓
AI/RAG
  ↓
structured result
```

The public API remains:

```text
POST /api/v1/emergency-assistance
```

---

# 34. Do Not Duplicate RAG Logic

Santosh should NOT build a second RAG implementation inside the core backend.

Instead:

```text
Emergency API
     ↓
AI service
     ↓
Satwik's RAG
```

---

# 35. RAG Response Integration

Consume fields such as:

```text
answer
sources
retrieval method
contexts used
confidence if provided
```

Do not expose raw vector data.

---

# 36. Voice Integration

Santosh supports integration between the application/backend and Satwik's Sarvam voice system.

Concept:

```text
Voice
 ↓
Sarvam
 ↓
text
 ↓
Emergency Assistance
 ↓
response
 ↓
Sarvam TTS
```

Voice must reuse the same business logic.

Do not create a separate emergency-answering system just for voice.

---

# 37. Agentic Actions

If the agentic provider-contact feature is implemented:

```text
AI proposes
 ↓
backend creates action
 ↓
user confirmation
 ↓
external action
 ↓
status
```

Santosh should implement the API/state-management side.

Do not allow:

```text
LLM → uncontrolled external call
```

---

# PHASE 4 — SYSTEM HARDENING

## Goal

Make the system reliable enough for the final demo.

---

# 38. Failure Matrix

Test:

```text
Google unavailable
Google rate limited
fallback unavailable
RAG unavailable
LLM unavailable
database unavailable
Firebase invalid
network lost
slow API
empty service result
invalid coordinates
```

Every failure must have a predictable response.

---

# 39. Provider Failover Test

Explicitly test:

```text
Google disabled
 ↓
fallback provider
 ↓
RAAHAT still returns services
```

This should become a strong technical point during judging.

---

# 40. Cached Data Support

Backend must support generating offline-pack data for Flutter.

Flow:

```text
route
 ↓
corridor
 ↓
service categories
 ↓
fetch services
 ↓
normalize
 ↓
package
```

The package should include:

```text
service metadata
coordinates
emergency knowledge references
timestamps
version
checksum
```

The exact package content is defined by the offline architecture.

---

# 41. Data Freshness

Every external service result should have:

```text
retrieved_at
source
availability_status
```

Do not claim live availability if the source cannot guarantee it.

---

# PHASE 5 — DEPLOYMENT

## Goal

Get the backend and React web application reachable for final testing.

---

# 42. Deployment Research

Santosh owns researching the easiest viable deployment strategy.

Potential categories:

```text
Backend hosting
Frontend hosting
PostgreSQL hosting
environment variables
HTTPS
CORS
domain/URL
health checks
```

Possible platforms may include:

```text
Render
Railway
Vercel
Fly.io
Cloud providers
Supabase for PostgreSQL if appropriate
```

The final choice should be based on:

```text
free/low-cost availability
ease
reliability
hackathon time
FastAPI support
PostgreSQL support
deployment speed
```

---

# 43. Deployment Order

Recommended:

```text
PostgreSQL
 ↓
FastAPI
 ↓
health check
 ↓
React
 ↓
Firebase
 ↓
Google API keys
 ↓
AI integrations
 ↓
end-to-end test
```

---

# 44. Environment Variables

Never hard-code secrets.

Examples:

```text
DATABASE_URL
FIREBASE_PROJECT_ID
FIREBASE_PRIVATE_KEY
GOOGLE_MAPS_API_KEY
GOOGLE_PLACES_API_KEY
GOOGLE_ROUTES_API_KEY
GROQ_API_KEY
SARVAM_API_KEY
```

Exact variables depend on final implementation.

---

# 45. CORS

Configure only required origins.

Development:

```text
localhost
```

Production:

```text
deployed React domain
```

Do not use unrestricted production CORS if avoidable.

---

# 46. Deployment Health Check

After deployment:

```text
GET /api/v1/health
```

must work.

Test:

```text
browser
curl
React
Flutter
```

---

# 47. Final Integration Order

The team should integrate in this sequence:

```text
1. Firebase Auth
2. FastAPI health
3. React ↔ FastAPI
4. Flutter ↔ FastAPI
5. Nearby services
6. Route
7. RAG
8. Emergency orchestration
9. Voice
10. Offline pack
11. Agentic actions
12. Deployment
13. Final testing
```

Do not attempt everything simultaneously.

---

# 48. React ↔ Backend Integration

Final flow:

```text
React
 ↓
Firebase ID token
 ↓
FastAPI
 ↓
validation
 ↓
AI / Places / DB
 ↓
unified response
 ↓
React
```

---

# 49. Flutter ↔ Backend Integration

Final flow:

```text
Flutter
 ↓
Firebase ID token
 ↓
FastAPI
 ↓
unified response
 ↓
Flutter
```

Offline requests do not call the backend.

---

# 50. API Contract Rules

Santosh must follow:

### Rule 1

FastAPI Pydantic schemas are authoritative.

### Rule 2

Use:

```text
snake_case
```

in JSON.

### Rule 3

Use canonical enums.

### Rule 4

Use ISO-8601 UTC timestamps.

### Rule 5

Never reverse latitude/longitude.

### Rule 6

Use `null` for unknown values.

### Rule 7

Do not expose database rows directly.

### Rule 8

Do not send raw Google/OSM responses to clients.

### Rule 9

Normalize all providers into RAAHAT's schema.

### Rule 10

Do not silently change contracts.

---

# 51. Provider Abstraction

The backend should ideally have:

```text
providers/
├── google_places.py
├── google_routes.py
├── osm.py
├── routing_fallback.py
└── base.py
```

Example conceptual interface:

```python
class PlacesProvider:
    async def search_nearby(...):
        ...
```

Then:

```text
GooglePlacesProvider
OSMProvider
```

can implement the same interface.

This prevents provider lock-in.

---

# 52. Database Abstraction

Similarly:

```text
repositories/
├── users.py
├── services.py
├── incidents.py
└── offline_packs.py
```

The API layer should not contain raw SQL everywhere.

---

# 53. Request IDs

Every request should produce:

```text
request_id
```

Log:

```text
endpoint
latency
status
provider
error
```

Never log:

```text
Firebase tokens
API keys
unnecessary sensitive data
```

---

# 54. Testing

At minimum:

### Backend unit tests

- Pydantic validation
- authentication
- service normalization
- provider fallback
- error mapping

### API tests

- emergency endpoint
- nearby services
- route
- health
- auth failures

### Integration tests

```text
React → FastAPI
Flutter → FastAPI
FastAPI → Google
FastAPI → fallback
FastAPI → AI
```

---

# 55. Phase 1 Exit Criteria

Santosh can move forward when:

- [ ] React project runs
- [ ] FastAPI project runs
- [ ] API structure exists
- [ ] P0 Pydantic schemas exist
- [ ] health endpoint works
- [ ] Firebase verification skeleton works
- [ ] PostgreSQL connection path is understood
- [ ] mock emergency endpoint works
- [ ] mock services endpoint works
- [ ] mock route endpoint works
- [ ] Google APIs researched
- [ ] alternatives researched
- [ ] fallback recommendation documented

---

# 56. Phase 2 Exit Criteria

- [ ] Google Places works
- [ ] route API works
- [ ] provider normalization works
- [ ] at least one fallback path is tested
- [ ] React consumes real APIs
- [ ] Flutter can consume real APIs
- [ ] service ranking works
- [ ] errors are standardized
- [ ] API contract remains stable

---

# 57. Phase 3 Exit Criteria

- [ ] Satwik's RAG integrated
- [ ] emergency orchestration works
- [ ] voice integration works
- [ ] offline-pack backend works
- [ ] service data is packageable
- [ ] agentic action API works if included

---

# 58. Phase 4 Exit Criteria

- [ ] provider failures tested
- [ ] AI failures tested
- [ ] DB failures tested
- [ ] auth failures tested
- [ ] network failures tested
- [ ] fallback provider tested
- [ ] API latency measured
- [ ] logs contain request IDs
- [ ] no secrets committed

---

# 59. Phase 5 Exit Criteria

- [ ] FastAPI deployed
- [ ] React deployed
- [ ] PostgreSQL connected
- [ ] Firebase production configuration works
- [ ] CORS works
- [ ] HTTPS works
- [ ] environment variables configured
- [ ] health endpoint works
- [ ] end-to-end demo works

---

# 60. Handoff to Saanvi

Santosh must provide:

```text
API base URL
API documentation
Firebase auth requirements
endpoint status
request examples
response examples
known limitations
Google/fallback provider status
```

Especially communicate:

```text
Which endpoints are READY
Which are MOCK
Which are UNAVAILABLE
```

Do not tell Saanvi:

> "Backend is almost done."

Give concrete status.

---

# 61. Handoff to Satwik

Santosh must provide:

```text
AI integration interface
RAG endpoint requirements
service data schema
route data schema
offline pack requirements
external provider status
```

Satwik should be able to plug his AI system into FastAPI without rewriting the API layer.

---

# 62. Communication Protocol

When Santosh changes an API:

```text
1. update Pydantic schema
2. update OpenAPI
3. update contract document
4. notify Satwik
5. notify Saanvi
6. update examples
7. run tests
```

Never silently change:

```text
field names
enums
response structure
required fields
```

---

# 63. If Google APIs Stop Working

Santosh's response should be:

```text
DO NOT PANIC
```

Follow:

```text
Check API key
 ↓
Check quota
 ↓
Check network
 ↓
Check provider response
 ↓
Switch provider
 ↓
normalize response
 ↓
continue demo
```

The application architecture should not require rewriting the frontend.

---

# 64. If No External Provider Works

Use:

```text
cached/mock verified demo dataset
```

only for demonstration where appropriate.

Clearly distinguish:

```text
LIVE DATA
```

from:

```text
CACHED DATA
```

Never fabricate a live provider result.

---

# 65. Judge-Facing Technical Story

Santosh should be prepared to explain:

### “Why Google Maps?”

> “We use Google as a primary location intelligence provider rather than rebuilding a mapping ecosystem from scratch. RAAHAT adds emergency-specific intelligence, prioritization, AI assistance and offline capability on top.”

### “What if Google isn't available?”

> “The backend uses a provider abstraction. We normalize Google and alternative map/POI/routing providers into the same RAAHAT service schema, so the core application isn't locked to one provider.”

### “Why not build maps yourself?”

> “The innovation is the emergency intelligence layer, not recreating global mapping infrastructure.”

---

# 66. What Santosh Can Work On Independently

If Satwik is busy:

```text
React
FastAPI
API contracts
Google research
fallback research
provider abstraction
mock APIs
deployment research
testing
```

If Saanvi is busy:

```text
React
FastAPI
API contracts
Google integration
fallback APIs
backend
deployment
```

If both are busy:

```text
backend foundation
provider abstraction
API testing
deployment preparation
```

Santosh should almost never be idle.

---

# 67. What Santosh Must Not Change Without Agreement

Do not independently change:

```text
RAG architecture
Gemma architecture
offline AI design
database schema
authentication architecture
API contracts
emergency safety logic
AI decision rules
```

If a change seems necessary:

```text
propose
↓
discuss
↓
update contract
↓
implement
```

---

# 68. AI Assistant Instructions

Santosh's AI assistant should behave as:

```text
Senior React Engineer
+
FastAPI Backend Engineer
+
API Integration Engineer
+
Maps/Location API Researcher
+
System Integration Engineer
+
Deployment Assistant
```

It must:

- follow the common architecture
- respect API contracts
- use mock-first development
- research Google alternatives
- avoid provider lock-in
- never invent API responses
- keep frontend/backend schemas synchronized
- prioritize working features over abstraction
- avoid unnecessary overengineering

---

# 69. AI Assistant Decision Rule

When Santosh asks:

> “What should I do now?”

The assistant should determine:

```text
current phase
↓
highest-priority incomplete deliverable
↓
dependencies
↓
what can be built independently
↓
next actionable task
```

Do not automatically assign Satwik's or Saanvi's work.

---

# 70. Priority Rules

```text
P0 = blocks the team
P1 = core product
P2 = integration
P3 = reliability/polish
P4 = optional USP
```

Santosh should prioritize:

```text
API contracts
>
FastAPI foundation
>
React foundation
>
Maps/Places
>
fallback APIs
>
real integration
>
AI integration
>
deployment
>
polish
```

---

# 71. Anti-Overengineering Rule

This is a 24-hour hackathon.

Do not spend excessive time on:

- microservices
- Kubernetes
- elaborate abstractions
- complex CI/CD
- unnecessary database normalization
- custom map engines
- unnecessary frontend architecture

The target is:

```text
stable
fast
demonstrable
integrated
```

---

# 72. Final Santosh Responsibility Map

```text
SANTOSH
│
├── REACT WEB
│   ├── App shell
│   ├── Emergency UI
│   ├── Services UI
│   ├── Route UI
│   └── API integration
│
├── FASTAPI
│   ├── API endpoints
│   ├── validation
│   ├── authentication verification
│   ├── orchestration integration
│   └── error handling
│
├── LOCATION INTELLIGENCE
│   ├── Google Places
│   ├── Google Routes
│   ├── Maps
│   └── provider normalization
│
├── FALLBACK RESEARCH
│   ├── OpenStreetMap
│   ├── Overpass
│   ├── OSRM
│   ├── openrouteservice
│   ├── Geoapify
│   ├── Mapbox
│   ├── HERE
│   └── final fallback strategy
│
├── SYSTEM INTEGRATION
│   ├── RAG integration
│   ├── voice integration
│   ├── offline-pack backend
│   └── agentic action APIs
│
└── DEPLOYMENT
    ├── FastAPI
    ├── React
    ├── PostgreSQL connection
    ├── Firebase configuration
    ├── environment variables
    └── final E2E testing
```

---

# 73. Final Definition of Done

Santosh's work is complete when:

> **RAAHAT has a working React web application and FastAPI backend that follow the frozen API contracts, authenticate users through Firebase, communicate with PostgreSQL through the agreed data layer, retrieve and normalize location/service information, use Google Maps/Places/Routes when available, have a tested fallback strategy when Google is unavailable, integrate Satwik's AI/RAG layer, support the offline-pack backend, handle failures cleanly, and are deployable for the final demonstration.**

---

# 74. One-Line Mission

> **Build the reliable platform layer of RAAHAT: React + FastAPI + location intelligence + provider fallbacks + integration + deployment, while keeping every client and AI subsystem connected through one stable API contract.**
