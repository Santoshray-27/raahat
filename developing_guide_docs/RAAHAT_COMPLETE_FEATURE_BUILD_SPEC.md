# RAAHAT — Complete Feature & Functionality Build Specification

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Team:** Solution Savvy  
**Document type:** Implementation feature inventory  
**Purpose:** Define every major feature, screen, API, backend responsibility, AI capability, database entity, offline capability, and integration that may need to be built.

---

# 0. How To Use This Document

This document is the **build checklist** for RAAHAT.

The previous PRD explains *why* the system exists and its overall architecture.

This document answers:

> **Exactly what do we need to build?**

Every feature is categorized into:

- **P0 — Core / must work**
- **P1 — Important / should work**
- **P2 — Advanced / wow factor / implement if time permits**

The feature list is intentionally detailed. During the 24-hour hackathon, the team should implement the P0 vertical slice first and then move downward.

---

# 1. System-Wide Feature Map

RAAHAT consists of the following major subsystems:

```text
RAAHAT
│
├── Frontend Web — React
│
├── Mobile App — Flutter
│
├── Backend — FastAPI
│
├── AI Layer
│   ├── Situation Understanding
│   ├── Decision Engine
│   ├── RAG
│   ├── Reranking
│   ├── Multilingual AI
│   ├── Offline Gemma
│   └── Agentic Tools
│
├── Location & Service Discovery
│   ├── Google Places
│   ├── Google Routes
│   └── Google Maps navigation
│
├── Database
│   └── PostgreSQL
│
├── Authentication
│   └── Firebase Auth
│
├── Offline Layer
│   ├── Local DB
│   ├── Cached route data
│   ├── Offline RAG
│   └── Gemma
│
└── External Integrations
    ├── Sarvam
    ├── Groq
    └── Google Maps Platform
```

---

# 2. FRONTEND WEB — REACT

The React application is the web-facing interface for RAAHAT.

It should focus on:

- route planning
- emergency interaction
- service discovery
- map visualization
- AI assistance
- service details
- navigation
- contact actions
- saved information
- status and incident information

---

# 3. React — Application Foundation

## 3.1 Project setup

Build:

- React application
- TypeScript if the team is comfortable with it
- routing
- reusable component system
- API client
- authentication context
- global state where required
- environment configuration

### Required environment variables

Frontend should NOT contain secret API keys.

Allowed client configuration:

- public Firebase configuration where required
- public map configuration if legitimately required

Secrets must remain in FastAPI.

---

# 4. React — Authentication

## 4.1 Login

Build:

- login page
- email/password or selected Firebase-supported authentication method
- authentication loading state
- authentication error state
- successful login redirect

## 4.2 Registration

Build:

- signup page
- input validation
- Firebase account creation
- error handling

## 4.3 Logout

Build:

- logout action
- token/session cleanup
- redirect to login

## 4.4 Auth state

Frontend should know:

- authenticated
- unauthenticated
- loading

## 4.5 Protected routes

Examples:

- dashboard
- emergency interface
- saved routes
- profile
- incident history if implemented

---

# 5. React — Main Dashboard

The dashboard should provide:

- current location
- map
- emergency input
- voice interaction entry point
- route planning
- nearby service categories
- recent/saved routes
- emergency contacts
- offline status where relevant

Primary actions:

```text
Report Emergency
Plan Journey
Find Help
Use Voice
Prepare Offline Pack
```

---

# 6. React — Location Interface

## 6.1 Current location

Display:

- current latitude/longitude internally
- human-readable location
- GPS/loading state
- location permission state
- location error

## 6.2 Location permission

Handle:

- permission granted
- permission denied
- permission unavailable
- retry

## 6.3 Manual location

Provide fallback:

- search location
- enter location
- select location on map

This is useful if browser GPS fails.

---

# 7. React — Map

## 7.1 Map display

Display:

- user location
- route
- service markers
- selected provider
- relevant emergency services

## 7.2 Marker categories

Potential categories:

- hospital
- police
- ambulance/provider
- mechanic
- puncture/tire shop
- towing
- fuel station
- vehicle service

## 7.3 Marker interaction

Clicking/tapping marker should show:

- provider name
- category
- distance
- address
- phone if available
- verification/freshness
- action buttons

---

# 8. React — Emergency Input

Users must be able to describe the situation.

## 8.1 Text input

Examples:

- “My car broke down.”
- “Tyre puncture ho gaya.”
- “There has been an accident and someone is injured.”
- “I am stranded on the highway.”

## 8.2 Voice entry

Connect to the voice workflow when implemented.

## 8.3 Input states

Handle:

- empty input
- sending
- processing
- success
- error
- retry

---

# 9. React — Emergency Analysis Result

After submission, display:

### Incident

- incident type
- severity
- detected situation
- relevant warning

### Required assistance

Example:

```text
Recommended assistance:
1. Ambulance
2. Emergency Hospital
3. Police
```

or:

```text
Recommended assistance:
1. Puncture Repair
2. Mobile Mechanic
3. Towing
```

---

# 10. React — Emergency Guidance

Display RAG-generated guidance.

Possible structure:

```text
WHAT TO DO NOW

1. Move to a safe location if possible.
2. Keep hazard lights on.
3. Do not stand in the traffic lane.

WHY

Based on your reported situation...
```

For medical/emergency guidance:

- clearly distinguish guidance from professional medical care
- show source information where available
- avoid unsupported claims

---

# 11. React — Recommended Services

Each recommended service card should show:

- provider name
- category
- distance
- approximate travel time if available
- address
- phone/contact
- verification status
- last verified/synchronized timestamp where available
- reason for recommendation

Actions:

- Call
- Navigate
- View Details
- Ask RAAHAT to Contact (advanced)

---

# 12. React — Service Ranking Explanation

Provide a simple explanation such as:

> Recommended because it is a suitable puncture-repair service and is 1.4 km away.

Do NOT expose complicated mathematical scoring to normal users.

---

# 13. React — Service Details

Detailed service page/modal:

- name
- type
- address
- location
- phone
- distance
- route
- verification
- source
- last synchronization
- available actions

---

# 14. React — Navigation

Provide:

- route preview
- distance
- estimated duration
- destination
- “Open in Google Maps”

Where possible, hand navigation to Google Maps rather than implementing a full navigation engine.

---

# 15. React — Call Actions

Normal call:

```text
CALL PROVIDER
```

The browser/mobile environment should use the appropriate `tel:` flow where supported.

For advanced agentic calling:

```text
ASK RAAHAT TO CALL
```

This MUST show confirmation first.

---

# 16. React — Agentic Provider Calling UI

Advanced P2 feature.

Flow:

```text
Provider selected
      ↓
RAAHAT asks:
“Would you like me to call this provider?”
      ↓
YES
      ↓
Calling...
      ↓
Call result
```

Display:

- call status
- provider
- reason
- outcome
- estimated arrival if provider gave one
- service confirmation if provider gave one

---

# 17. React — Route Planning

User should be able to:

- enter start location
- enter destination
- use current location as start
- preview route
- save route
- prepare offline emergency data

Example:

```text
START
Indore

DESTINATION
Bhopal

[PLAN ROUTE]

[PREPARE OFFLINE EMERGENCY PACK]
```

---

# 18. React — Offline Pack Preparation

Before travel:

Display:

```text
Preparing emergency data...

✓ Route
✓ Hospitals
✓ Police
✓ Mechanics
✓ Puncture services
✓ Towing
✓ Emergency contacts
✓ Emergency guidance
✓ Offline AI package status
```

Show:

- estimated download size
- data freshness
- successful completion
- failure/retry

---

# 19. React — Offline Pack Status

Show:

- downloaded/not downloaded
- last updated
- route covered
- number of cached providers
- offline AI installed/not installed

---

# 20. React — Emergency Contacts

Display important emergency contacts according to region.

Potential:

- police
- ambulance
- fire
- other region-specific emergency services

Numbers must come from trusted structured data.

---

# 21. React — Profile

Potential:

- name
- email
- language
- emergency preferences
- saved routes
- offline package status

Do not collect unnecessary personal data.

---

# 22. React — Settings

Potential settings:

- language
- location permission
- notification preferences
- offline AI
- privacy
- data deletion
- logout

---

# 23. React — Network State

Display:

- Online
- Poor connection
- Offline

When offline:

- disable actions that require live network
- enable cached services/guidance
- clearly mark stale information

---

# 24. React — Error Handling

Must handle:

- Google API failure
- FastAPI failure
- RAG failure
- authentication failure
- location failure
- network timeout
- provider unavailable
- incomplete service information

Never show a fake result when an API fails.

---

# 25. FLUTTER MOBILE APP

Flutter is the primary mobile/offline emergency experience.

Its most important advantage is:

> **Mobile-native location + local storage + offline AI + emergency actions.**

---

# 26. Flutter — App Foundation

Build:

- Flutter project
- navigation
- theme
- reusable components
- API client
- authentication integration
- local storage
- network state detection
- permission management

---

# 27. Flutter — Authentication

Implement:

- Firebase login
- signup
- logout
- session persistence
- token handling
- protected application state

---

# 28. Flutter — Mobile Home Screen

Primary actions:

```text
🚨 Emergency Assistance
🗺️ Plan Journey
📍 Nearby Help
🎙️ Talk to RAAHAT
📦 Offline Pack
```

The interface should prioritize emergency actions.

---

# 29. Flutter — GPS

Implement:

- location permission
- current location
- background/location updates only if necessary
- GPS accuracy
- location unavailable state
- last known location

Avoid continuous tracking unless explicitly required.

---

# 30. Flutter — Emergency Mode

Emergency mode should simplify the interface.

Show:

- current location
- incident
- severity
- recommended help
- CALL
- NAVIGATE
- SOS
- guidance

Avoid unnecessary menus.

---

# 31. Flutter — Voice

Potential flow:

```text
Tap microphone
      ↓
Speak
      ↓
Sarvam / voice workflow
      ↓
FastAPI
      ↓
Response
      ↓
Voice/text result
```

Offline voice implementation is separate and may be P2.

---

# 32. Flutter — Local Database

Use an appropriate local database/storage mechanism.

Potential contents:

- route data
- service records
- coordinates
- emergency contacts
- emergency guidance metadata
- offline RAG index
- cached responses
- sync metadata

---

# 33. Flutter — Offline Mode

Detect:

- online
- offline
- connection restored

When offline:

```text
NO INTERNET
      ↓
GPS
      ↓
Local database
      ↓
Local spatial query
      ↓
Offline decision
      ↓
Gemma
      ↓
Offline RAG
```

---

# 34. Flutter — Route-Aware Offline Pack

User enters:

```text
Indore → Bhopal
```

System downloads emergency data for a corridor around the route.

Data may include:

- providers
- hospitals
- police
- mechanics
- puncture services
- towing
- emergency contacts
- relevant emergency guidance
- route/map data

---

# 35. Flutter — Local Spatial Search

When offline:

1. Read GPS coordinates.
2. Query local provider data.
3. Calculate distance.
4. Filter within configurable radius.
5. Pass only relevant candidates to decision logic/AI.

Important:

> Gemma should NOT perform raw geographic calculations.

---

# 36. Flutter — Offline Gemma

Provide an offline AI package.

Package includes:

- selected Gemma model
- model runtime
- model configuration
- offline RAG index
- relevant tokenizer/runtime files as required

User downloads the model before travel.

---

# 37. Flutter — Offline RAG

Offline RAG should use:

- local knowledge base
- local vector/index data
- metadata
- trusted emergency guidance

It must not depend on the internet.

---

# 38. Flutter — Offline Service Cards

Each cached provider should display:

- name
- type
- distance from current location
- cached phone number
- cached address
- last synchronized
- stale-data warning where relevant

---

# 39. Flutter — Offline Actions

If cellular connectivity still exists:

- Call provider
- Call emergency number

If navigation data is cached:

- open offline route/map capability

If no network:

- show available cached information
- show current coordinates
- provide instructions for seeking help

---

# 40. Flutter — SOS

Potential SOS workflow:

```text
SOS
 ↓
Confirm or configurable emergency trigger
 ↓
Current location
 ↓
Emergency contact / emergency number
```

Do not implement dangerous automatic calling without explicit requirements/permissions.

---

# 41. Flutter — Sync

When connectivity returns:

```text
Offline changes/data
      ↓
Sync manager
      ↓
FastAPI
      ↓
PostgreSQL
```

Potential sync:

- incidents
- route state
- offline usage logs
- updated cache metadata

Avoid uploading sensitive data unnecessarily.

---

# 42. BACKEND — FASTAPI

FastAPI is the central orchestration layer.

Suggested module structure:

```text
backend/
├── app/
│   ├── main.py
│   ├── api/
│   ├── auth/
│   ├── users/
│   ├── incidents/
│   ├── services/
│   ├── locations/
│   ├── routes/
│   ├── ai/
│   ├── rag/
│   ├── tools/
│   ├── offline/
│   ├── database/
│   └── security/
```

---

# 43. Backend — Authentication

Implement:

- Firebase ID-token verification
- authenticated request dependency
- user identity extraction
- authorization
- invalid token handling
- expired token handling

Example:

```text
Authorization: Bearer <firebase_token>
```

---

# 44. Backend — User APIs

Potential endpoints:

```text
GET    /users/me
PATCH  /users/me
DELETE /users/me
```

User data should be scoped to the authenticated Firebase UID.

---

# 45. Backend — Incident APIs

Potential endpoints:

```text
POST /incidents
GET  /incidents/{id}
GET  /incidents
PATCH /incidents/{id}
```

Incident fields:

- ID
- user ID
- incident type
- severity
- location
- timestamp
- status
- required services
- relevant guidance

---

# 46. Backend — Core Emergency Endpoint

Central endpoint concept:

```text
POST /emergency-assistance
```

Responsibilities:

1. Validate input.
2. Identify authenticated user.
3. Understand user query.
4. Extract incident.
5. Determine severity.
6. Determine required services.
7. Retrieve knowledge if needed.
8. Query Google Places if needed.
9. Rank services.
10. Produce grounded response.
11. Return structured result.

---

# 47. Backend — Query Understanding

Input:

```json
{
  "message": "My car broke down on the highway",
  "location": {
    "latitude": 22.7,
    "longitude": 75.8
  },
  "language": "en"
}
```

Output:

```json
{
  "incident_type": "vehicle_breakdown",
  "severity": "medium",
  "needs": [
    "mechanic",
    "towing"
  ]
}
```

The LLM should output structured data, not arbitrary prose.

---

# 48. Backend — Incident Classification

Initial categories:

- accident
- injury
- vehicle_breakdown
- tyre_puncture
- fuel_emergency
- stranded
- medical_emergency
- other

Allow future category extension.

---

# 49. Backend — Severity Engine

Potential levels:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The system should combine:

- AI extraction
- deterministic rules

Example:

```text
injury = true
 ↓
at least HIGH/CRITICAL
```

Safety-critical escalation should be deterministic wherever possible.

---

# 50. Backend — Service Requirement Engine

Map incident → required services.

Example:

```text
tyre_puncture
→ puncture_repair
→ mobile_mechanic
→ towing
```

```text
accident + injury
→ ambulance
→ hospital
→ police
→ towing
```

```text
vehicle_breakdown
→ mechanic
→ towing
```

---

# 51. Backend — Google Places Service

Build a dedicated Google Places client.

Responsibilities:

- nearby search
- place details
- category mapping
- request batching where appropriate
- API errors
- rate limiting
- caching where appropriate
- normalization

---

# 52. Backend — Google Place Type Mapping

Maintain internal mapping:

```text
internal_service_type
        ↓
Google place type(s)
```

Examples:

```text
hospital → hospital / general_hospital
police → police
mechanic → car_repair
puncture → tire_shop
fuel → gas_station
```

Exact mappings should be tested against the Google API.

---

# 53. Backend — Provider Normalization

Convert Google/provider records into one internal schema.

Example:

```json
{
  "provider_id": "...",
  "name": "...",
  "type": "mechanic",
  "latitude": 22.7,
  "longitude": 75.8,
  "address": "...",
  "phone": "...",
  "source": "google_places",
  "verification_status": "source_verified"
}
```

---

# 54. Backend — Service Ranking

Create a ranking module.

Possible factors:

```text
incident suitability
distance
provider category match
verification/freshness
accessibility
other context
```

Example conceptual score:

```text
score =
  suitability_weight
+ distance_weight
+ freshness_weight
+ accessibility_weight
```

Exact weights remain to be tuned.

---

# 55. Backend — Distance

Distance can be calculated using:

- coordinates for straight-line distance
- Google Routes for route distance/time where required

Do not confuse straight-line distance with driving distance.

---

# 56. Backend — Service Explanation

Return a reason:

```text
"Recommended because it is a nearby puncture-repair provider."
```

This makes recommendations explainable.

---

# 57. Backend — Navigation

Provide:

- destination coordinates
- place ID
- route information where needed
- Google Maps navigation handoff data

---

# 58. Backend — Normal Calling

Return provider contact information.

Frontend/mobile can initiate a phone call where supported.

---

# 59. Backend — Agentic Calling

Advanced endpoint/tool:

```text
POST /tools/call-provider
```

Before execution:

- authenticate user
- verify provider
- verify user confirmation
- construct call request
- execute through approved telephony provider
- capture result
- return outcome

---

# 60. Backend — Tool Permission System

Tools should have:

```text
tool_name
requires_confirmation
allowed_user
parameters
execution_status
```

Example:

```json
{
  "tool": "call_provider",
  "requires_confirmation": true
}
```

---

# 61. Backend — Emergency Actions

Potential tools:

- `call_provider`
- `call_emergency`
- `navigate_to_provider`
- `share_location`
- `send_sos`
- `get_nearby_services`

Tool execution must be controlled by backend logic.

---

# 62. Backend — Route APIs

Potential endpoints:

```text
POST /routes
GET  /routes
GET  /routes/{id}
DELETE /routes/{id}
POST /routes/{id}/prepare-offline
```

---

# 63. Backend — Offline Pack Generation

Given:

```text
start
destination
route geometry
```

Generate:

- emergency corridor
- service queries
- cached provider dataset
- emergency contacts
- relevant RAG documents
- sync metadata

---

# 64. Backend — Offline Pack Download

Provide:

```text
GET /offline-packs/{route_id}
```

or an equivalent package-download mechanism.

Package may include:

```text
providers.json
emergency_contacts.json
guidance.json
rag_index/
metadata.json
route_data/
```

Exact package format is implementation-dependent.

---

# 65. Backend — Offline Pack Versioning

Store:

- pack ID
- route ID
- created time
- version
- data source timestamps
- expiry/recommended refresh
- size
- checksum if required

---

# 66. Backend — Network-Aware Behavior

Backend should not pretend online data is available when APIs fail.

Return explicit statuses:

```text
online
degraded
offline-cache
error
```

---

# 67. Backend — Error Handling

Standardize:

- validation errors
- authentication errors
- authorization errors
- Google API errors
- LLM errors
- RAG errors
- database errors
- timeout errors
- provider call errors

---

# 68. Backend — Rate Limiting

Potentially rate-limit:

- emergency endpoint
- Google Places calls
- LLM calls
- provider-call tool
- authentication-sensitive endpoints

Especially important for expensive external APIs.

---

# 69. Backend — Caching

Potential cache targets:

- Google Places results
- Place Details
- emergency contacts
- RAG retrieval results where safe
- route information
- offline packs

Do not cache user-specific sensitive information unnecessarily.

---

# 70. AI FEATURES — OVERVIEW

AI is not one monolithic model.

RAAHAT AI should be divided into:

```text
AI
│
├── Query Understanding
├── Incident Classification
├── Severity Extraction
├── Decision/Orchestration
├── RAG
├── Reranking
├── Grounded Generation
├── Multilingual
├── Voice
├── Offline Gemma
└── Agentic Tools
```

---

# 71. AI — Query Understanding

Input:

> “Meri car highway pe band ho gayi hai.”

Extract:

- incident
- urgency
- required help
- location context if stated
- language

Return structured output.

---

# 72. AI — Structured Output

Use schemas rather than free-form LLM responses.

Example:

```json
{
  "incident_type": "vehicle_breakdown",
  "severity": "medium",
  "injury": false,
  "requires_emergency_services": false,
  "required_services": [
    "mechanic",
    "towing"
  ]
}
```

---

# 73. AI — Decision Engine

The decision engine combines:

- LLM understanding
- deterministic rules
- location
- service availability data
- ranking

The LLM does NOT have unrestricted authority.

---

# 74. AI — Emergency Escalation

Example:

```text
Initial:
vehicle breakdown
 ↓
mechanic/towing
```

User later says:

> “Actually someone hit us and my friend is bleeding.”

System should reclassify:

```text
accident + injury
 ↓
critical
 ↓
ambulance
hospital
police
```

This dynamic escalation is a major demo capability.

---

# 75. AI — RAG Knowledge Domains

Initial RAG collections/namespaces:

```text
emergency_guidance
roadside_assistance
regional_emergency
first_aid
```

Potential future:

```text
service_policies
regional_protocols
```

---

# 76. AI — RAG Ingestion Pipeline

Build:

```text
Trusted Sources
 ↓
Fetch / upload
 ↓
Clean
 ↓
Normalize
 ↓
Metadata extraction
 ↓
Contextualization
 ↓
Chunking
 ↓
Embedding
 ↓
Vector index
 ↓
BM25 index
```

---

# 77. AI — Document Metadata

Each document/chunk should have:

- document ID
- chunk ID
- source
- source URL
- authority
- region
- state/country
- language
- domain
- emergency type
- severity
- date retrieved
- last verified
- version

---

# 78. AI — Chunking

Chunking should preserve:

- section boundaries
- semantic meaning
- document context

Avoid arbitrary cuts through critical instructions.

---

# 79. AI — Contextual Chunking

Before indexing, enrich chunks with document context.

Example:

```text
Document:
Emergency First Aid Guide

Section:
Severe Bleeding

Context:
Guidance for controlling severe external bleeding.

Chunk:
Apply firm pressure...
```

This prevents context loss.

---

# 80. AI — Vector Retrieval

Generate embeddings for contextualized chunks.

Search using semantic similarity.

---

# 81. AI — BM25 Retrieval

Use lexical retrieval for:

- exact emergency terms
- names
- numbers
- acronyms
- specific procedures

---

# 82. AI — Hybrid Fusion

Combine:

```text
BM25 results
+
Vector results
↓
Fusion
↓
Top candidate set
```

---

# 83. AI — Reranking

Pipeline:

```text
Top 30-50 candidates
 ↓
Reranker
 ↓
Top 5-10
```

Reranking should happen before final LLM generation.

---

# 84. AI — Metadata Filtering

Filter by:

- country
- state/region
- language
- emergency type
- domain
- severity
- source authority

This reduces irrelevant retrieval.

---

# 85. AI — Grounded Generation

Final LLM prompt should include:

- user question
- structured incident
- retrieved evidence
- service results
- relevant constraints

Rules:

- answer from evidence
- do not invent
- acknowledge uncertainty
- do not fabricate service facts
- do not fabricate emergency procedures

---

# 86. AI — Source Attribution

Where practical, final answers should expose:

- source
- last verified
- relevant document/title

This supports trust.

---

# 87. AI — Confidence

Track retrieval/generation confidence where possible.

If confidence is below an acceptable threshold:

```text
Do not confidently answer.
```

Fallback to:

- safer guidance
- official emergency contact
- explicit uncertainty

---

# 88. AI — Agentic Routing

Controlled router:

```text
User query
 ↓
Determine required capabilities
 ↓
RAG?
Places?
Database?
Tool?
Multiple?
 ↓
Execute permitted operations
 ↓
Combine results
```

---

# 89. AI — Tool Calling

Potential tools:

```text
get_current_location
search_nearby_services
get_service_details
get_emergency_contact
retrieve_guidance
navigate
call_provider
call_emergency
share_location
send_sos
```

Tools must have schemas and permissions.

---

# 90. AI — Tool Safety

Tool execution rules:

- authentication required
- parameters validated
- sensitive actions require confirmation
- provider calls require explicit user permission
- emergency calls require clearly defined UX
- tool execution logged where appropriate

---

# 91. AI — Multilingual

AI should support:

- English
- Hindi
- additional Indian languages as practical

Use:

- Sarvam
- language detection
- translation only where needed
- multilingual RAG metadata

Avoid unnecessary translation if the model/retriever can work directly in the source language.

---

# 92. AI — Voice

Online flow:

```text
User voice
 ↓
Sarvam STT
 ↓
FastAPI
 ↓
AI orchestration
 ↓
Response
 ↓
Sarvam TTS
 ↓
User
```

The existing Sarvam voice-agent integration should be reused rather than rebuilt.

---

# 93. AI — Offline Gemma

Offline AI flow:

```text
User
 ↓
Offline input
 ↓
Gemma
 ↓
Structured understanding
 ↓
Local decision engine
 ↓
Offline RAG
 ↓
Response
```

The model should operate on-device.

---

# 94. AI — Offline RAG

Offline knowledge package contains:

- emergency guidance
- relevant first-aid knowledge
- roadside procedures
- regional emergency information

Retrieval should happen locally.

---

# 95. AI — Offline Provider Selection

Important:

```text
GPS
 ↓
Local spatial database
 ↓
Nearby cached candidates
 ↓
Decision engine
 ↓
Gemma explains/selects
```

Do NOT send the entire route dataset into Gemma.

---

# 96. DATABASE — POSTGRESQL

PostgreSQL is the primary application database.

---

# 97. Database — Users

Suggested fields:

```text
id
firebase_uid
name
email
language
created_at
updated_at
```

Firebase UID should be unique.

---

# 98. Database — Routes

Suggested fields:

```text
id
user_id
start_location
destination
route_geometry
created_at
updated_at
offline_pack_version
```

Do not store excessive route history.

---

# 99. Database — Incidents

Suggested fields:

```text
id
user_id
incident_type
severity
latitude
longitude
description
status
created_at
updated_at
```

---

# 100. Database — Providers

Suggested fields:

```text
id
external_provider_id
source
name
category
latitude
longitude
address
phone
region
verification_status
last_verified
last_synced
created_at
updated_at
```

---

# 101. Database — Service Categories

Example:

```text
hospital
ambulance
police
mechanic
puncture
towing
fuel
vehicle_service
```

---

# 102. Database — Emergency Contacts

Fields:

```text
id
country
state
region
service_type
phone_number
source
last_verified
```

---

# 103. Database — Verification

Potential fields:

```text
provider_id
source
verification_status
verified_at
verified_by
confidence
notes
```

---

# 104. Database — Offline Packs

Fields:

```text
id
route_id
version
created_at
expires_at / refresh_at
size
checksum
status
```

---

# 105. Database — Action Logs

For important tool actions:

```text
id
user_id
action_type
provider_id
confirmation_status
execution_status
created_at
result
```

Do not store sensitive call content unless required.

---

# 106. Database — RAG Metadata

Potential relational metadata:

```text
document_id
source
authority
region
language
domain
emergency_type
version
retrieved_at
verified_at
```

Actual vector storage can be implemented using PostgreSQL-compatible vector storage if chosen.

---

# 107. Firebase Authentication

Firebase handles:

- signup
- login
- session
- identity
- token issuance

FastAPI handles:

- token verification
- authorization
- database access control

---

# 108. Authorization

Every protected request must determine:

```text
Who is the user?
 ↓
What resource is being requested?
 ↓
Does it belong to this user?
 ↓
Allow / deny
```

Never trust a client-provided `user_id` without verifying it against the Firebase identity.

---

# 109. Secrets

Never expose:

- Groq API key
- Sarvam API key
- Google server-side API keys
- telephony credentials
- PostgreSQL password
- service account secrets

Secrets live in backend environment/configuration.

---

# 110. Offline Security

Offline package may contain:

- location/service data
- emergency information
- AI model
- RAG knowledge

Protect where practical.

Do not store unnecessary personal information in the package.

---

# 111. API Integration Map

## React → FastAPI

For:

- auth-backed application requests
- incidents
- services
- routes
- AI
- RAG
- offline packs

## Flutter → FastAPI

For the same core application services.

## Sarvam → FastAPI

For voice-agent interaction.

## FastAPI → Groq

For LLM reasoning/structured extraction where selected.

## FastAPI → Google

For Places/Routes.

## FastAPI → PostgreSQL

For structured application data.

## Flutter → Local DB/Gemma

For offline functionality.

---

# 112. Suggested API Inventory

## Authentication

```text
GET /health
GET /users/me
PATCH /users/me
```

## Emergency

```text
POST /emergency-assistance
POST /incidents
GET /incidents
GET /incidents/{id}
PATCH /incidents/{id}
```

## Services

```text
GET /services/nearby
GET /services/{id}
GET /services/{id}/details
```

## Routes

```text
POST /routes
GET /routes
GET /routes/{id}
DELETE /routes/{id}
POST /routes/{id}/prepare-offline
```

## RAG/AI

```text
POST /ai/analyze
POST /ai/ask
POST /rag/query
```

## Actions

```text
POST /tools/call-provider
POST /tools/navigate
POST /tools/share-location
POST /tools/send-sos
```

Exact endpoints may be consolidated during implementation.

---

# 113. Recommended First Build Order

## Sprint 1 — Skeleton

- Git repository
- FastAPI
- React
- Flutter
- PostgreSQL
- Firebase Auth
- environment configuration

## Sprint 2 — Core location

- GPS
- Google Places
- service schema
- map
- service cards

## Sprint 3 — Core intelligence

- incident extraction
- severity
- service requirements
- ranking

## Sprint 4 — First complete demo

```text
Text
 ↓
FastAPI
 ↓
AI
 ↓
Google Places
 ↓
Ranking
 ↓
Service
 ↓
Navigate/Call
```

## Sprint 5 — RAG

- knowledge ingestion
- hybrid retrieval
- reranking
- grounded answer

## Sprint 6 — Voice

- connect Sarvam to final endpoint

## Sprint 7 — Offline

- route pack
- local database
- offline services
- Gemma
- offline RAG

## Sprint 8 — Advanced agent

- provider calling
- confirmation
- tool execution
- call result

## Sprint 9 — Polish

- UX
- loading/error states
- demo data
- presentation
- security
- testing

---

# 114. P0 Feature Checklist

## Frontend Web

- [ ] Login
- [ ] Signup
- [ ] Dashboard
- [ ] Current location
- [ ] Map
- [ ] Emergency input
- [ ] Incident result
- [ ] Severity display
- [ ] Recommended services
- [ ] Service details
- [ ] Call
- [ ] Navigate
- [ ] Emergency guidance
- [ ] Route planning

## Flutter

- [ ] Authentication
- [ ] GPS
- [ ] Emergency mode
- [ ] Local storage
- [ ] Online/offline detection
- [ ] Cached services
- [ ] Call
- [ ] Navigate
- [ ] Emergency guidance

## Backend

- [ ] FastAPI
- [ ] Firebase token verification
- [ ] PostgreSQL
- [ ] Emergency endpoint
- [ ] Incident classification
- [ ] Service requirement engine
- [ ] Google Places
- [ ] Ranking
- [ ] Error handling

## AI

- [ ] Structured incident extraction
- [ ] Severity
- [ ] Service requirement
- [ ] Basic RAG
- [ ] Grounded response

## Database/Auth

- [ ] User
- [ ] Incident
- [ ] Provider
- [ ] Emergency contact
- [ ] Firebase authentication
- [ ] Authorization

---

# 115. P1 Feature Checklist

- [ ] Sarvam voice
- [ ] Hindi
- [ ] Multilingual interaction
- [ ] Route saving
- [ ] Offline pack preparation
- [ ] Cached emergency services
- [ ] Cached emergency guidance
- [ ] Verification metadata
- [ ] Service ranking explanation
- [ ] Improved RAG
- [ ] BM25
- [ ] Vector search
- [ ] Reranking
- [ ] Contextual retrieval
- [ ] Offline route corridor

---

# 116. P2 Feature Checklist

- [ ] Offline Gemma
- [ ] Offline RAG
- [ ] Offline AI reasoning
- [ ] Agentic provider calling
- [ ] Provider confirmation
- [ ] Advanced SOS
- [ ] Advanced regional support
- [ ] Advanced verification
- [ ] Multi-provider aggregation
- [ ] More advanced tool orchestration

---

# 117. Non-Functional Requirements

## Performance

- Fast initial UI.
- API requests should have sensible timeouts.
- Avoid unnecessary Google API calls.
- Avoid sending huge contexts to LLMs.
- Offline queries should respond locally as much as possible.

## Reliability

- External API failure must not crash the application.
- Cached information should be available when appropriate.
- Every external result should have a source.

## Security

- HTTPS.
- Firebase token verification.
- Server-side API secrets.
- User-scoped database access.
- Minimum necessary personal data.

## Explainability

The system should be able to explain:

- why a service was recommended
- where service information came from
- when data was last synchronized
- whether information is live or cached

---

# 118. Final Feature Hierarchy

```text
CORE
│
├── Authentication
├── Location
├── Incident understanding
├── Decision engine
├── Google Places
├── Ranking
├── Guidance
├── Contact
└── Navigation

INTELLIGENCE
│
├── RAG
├── Hybrid retrieval
├── Reranking
├── Multilingual
└── Voice

RESILIENCE
│
├── Route caching
├── Local DB
├── Offline services
├── Offline RAG
└── Gemma

AGENTIC
│
├── Tool routing
├── User confirmation
├── Provider calling
├── Provider conversation
└── Action result

TRUST
│
├── Source metadata
├── Verification
├── Freshness
├── Privacy
└── Explainability
```

---

# 119. Final Definition of the Product

RAAHAT should be able to turn:

> **“Something happened to me on the road.”**

into:

```text
WHAT HAPPENED?
      ↓
HOW SERIOUS IS IT?
      ↓
WHAT HELP DO I NEED?
      ↓
WHO CAN HELP?
      ↓
WHICH OPTION IS BEST?
      ↓
WHAT SHOULD I DO RIGHT NOW?
      ↓
DO YOU WANT ME TO TAKE ACTION?
```

That is the core product.

The technology exists to support this workflow:

- **React** → web experience
- **Flutter** → mobile/offline experience
- **FastAPI** → orchestration
- **PostgreSQL** → structured data
- **Firebase** → authentication
- **Google Places/Maps** → location infrastructure
- **Groq/Sarvam** → AI and voice
- **Hybrid RAG** → trusted knowledge
- **Gemma** → offline AI
- **Agentic tools** → real-world actions

The system should always prioritize:

> **Correctness → safety → relevance → actionability → convenience.**
