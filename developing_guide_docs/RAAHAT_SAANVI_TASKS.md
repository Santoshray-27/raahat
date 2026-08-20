# RAAHAT — Saanvi Task & Execution Plan

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Team:** Solution Savvy  
**Team Member:** Saanvi Gupta  
**Primary Domains:** Research + Flutter/Mobile + Offline Preparation + Knowledge/Data Support

---

# 1. Purpose of This Document

This document is Saanvi's **personal execution guide** for the RAAHAT project.

It is intended to be provided to Saanvi's AI assistant/AI coding agent together with the common project documents:

- RAAHAT PRD
- RAAHAT complete feature/functionality document
- RAAHAT architecture document
- RAAHAT RAG architecture document
- RAAHAT Offline AI architecture document
- RAAHAT API Contracts & Integration Guide

Those documents explain the overall product.

**This document explains Saanvi's responsibilities specifically.**

The objective is not merely to divide features between teammates. The objective is to create a **dependency-aware execution plan** where:

```text
Saanvi's Phase 1 outputs
        ↓
Satwik's Phase 2 AI/RAG work

Saanvi's Phase 1 outputs
        ↓
Saanvi's own Phase 2 implementation

Santosh's Phase 1 outputs
        ↓
Saanvi's Phase 2 integration

Saanvi's Phase 2 outputs
        ↓
Final team integration
```

No teammate should be unnecessarily blocked waiting for Saanvi, and Saanvi should not wait unnecessarily for another teammate.

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
- API integration
- Google Maps / Places / Routes
- frontend/backend integration
- system integration
- deployment
- research of alternatives if Google APIs are unavailable

### Saanvi Gupta
Primary areas:

- Research
- Flutter
- mobile application
- domain/knowledge research
- RAG data research and preparation
- offline package preparation
- offline mobile AI integration support
- testing and scenario validation

---

# 3. Saanvi's Core Mission

Saanvi owns two major pillars:

```text
                 SAANVI
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
     RESEARCH              FLUTTER
        │                     │
        ▼                     ▼
Knowledge/Data          Mobile Application
        │                     │
        └──────────┬──────────┘
                   ▼
             Offline Layer
```

Her work should make two things possible:

### Pillar A — Knowledge

Provide Satwik with high-quality, structured, verified material required to build the RAG system.

### Pillar B — Mobile

Build the Flutter application that becomes the mobile interface for:

- emergency assistance
- location-aware assistance
- nearby services
- route preparation
- offline mode
- local AI
- cached services
- emergency guidance
- future voice interaction

---

# 4. The Most Important Rule

> **Do not wait for the entire backend or RAG system to be completed before starting Flutter.**

Use:

```text
API contracts
+
mock responses
+
local mock data
```

to build the application early.

Similarly:

> **Do not give Satwik raw/unstructured research links and expect him to turn them into a knowledge base during the final hours.**

Research must be converted into structured, usable material.

---

# 5. Phase Overview

The execution plan is:

```text
PHASE 0
Project understanding + setup
        ↓
PHASE 1
Research + knowledge preparation + Flutter foundation
        ↓
PHASE 2
Knowledge handoff + core Flutter features + API integration
        ↓
PHASE 3
Offline package + local AI integration + full mobile integration
        ↓
PHASE 4
Testing + failure handling + UX refinement
        ↓
PHASE 5
Final integration + demo + presentation support
```

---

# 6. Dependency Philosophy

Saanvi's work is intentionally split into two tracks.

```text
RESEARCH TRACK
      │
      ├── domain research
      ├── emergency knowledge
      ├── RAG source collection
      ├── data quality
      └── offline data requirements

FLUTTER TRACK
      │
      ├── app shell
      ├── screens
      ├── location
      ├── API client
      ├── offline UI
      └── local storage
```

These tracks proceed in parallel.

---

# PHASE 0 — PROJECT UNDERSTANDING & SETUP

## Goal

Become completely aligned with what RAAHAT is supposed to build before writing significant code.

---

## 0.1 Read the Common Documents

Saanvi's AI assistant should be given:

1. PRD
2. feature/functionality document
3. architecture document
4. RAG architecture document
5. offline AI architecture document
6. API contracts document

The AI assistant must understand:

```text
Problem Statement
↓
RAAHAT solution
↓
Web architecture
↓
Flutter architecture
↓
Backend
↓
RAG
↓
Offline AI
↓
API contracts
```

---

## 0.2 Understand What Saanvi Does NOT Own

Do not independently take ownership of:

- PostgreSQL
- Firebase backend architecture
- core RAG implementation
- LLM orchestration
- FastAPI AI orchestration
- Sarvam backend architecture
- Google Places backend integration
- final deployment architecture

These belong primarily to Satwik/Santosh.

Saanvi can support integration and research but should not create conflicting implementations.

---

## 0.3 Flutter Environment

Set up:

- Flutter SDK
- Android Studio / required Android tooling
- emulator if available
- actual Android device
- Git branch
- project structure

Confirm:

```text
flutter doctor
```

works sufficiently for development.

---

## 0.4 Define Flutter Project Structure

Suggested structure:

```text
lib/
├── core/
│   ├── constants/
│   ├── network/
│   ├── location/
│   ├── storage/
│   ├── theme/
│   └── utils/
│
├── models/
│
├── services/
│   ├── api_client.dart
│   ├── auth_service.dart
│   ├── emergency_service.dart
│   ├── services_service.dart
│   ├── route_service.dart
│   ├── offline_service.dart
│   └── voice_service.dart
│
├── features/
│   ├── auth/
│   ├── home/
│   ├── emergency/
│   ├── services/
│   ├── route/
│   ├── offline/
│   └── profile/
│
└── main.dart
```

This is a suggested structure, not a mandatory one.

---

# PHASE 1 — RESEARCH + KNOWLEDGE PREPARATION + FLUTTER FOUNDATION

## Goal

By the end of Phase 1:

```text
Saanvi has produced
        ↓
structured research material
        ↓
RAG-ready knowledge/data
        ↓
Flutter application skeleton
        ↓
mock-driven screens
```

Most importantly:

> **Satwik should be able to begin real RAG ingestion from Saanvi's outputs without having to redo the research.**

---

# 7. PHASE 1A — DOMAIN RESEARCH

Research the actual roadside emergency problem deeply.

The research should answer:

- What situations are users likely to face?
- What information is required immediately?
- What information is useful but non-critical?
- What emergency categories should RAAHAT recognize?
- What roadside service categories are needed?
- What information should be available offline?
- Which information needs official sources?
- Which information can come from secondary sources?
- Which information becomes dangerous if inaccurate or outdated?

---

# 8. Emergency Scenario Research

Build a structured scenario list.

Initial categories:

```text
ACCIDENT
MEDICAL_EMERGENCY
SEVERE_BLEEDING
VEHICLE_FIRE
TYRE_PUNCTURE
VEHICLE_BREAKDOWN
STRANDED
FUEL_EMERGENCY
OTHER
```

For each scenario research:

```text
Scenario
↓
Immediate safety concern
↓
Recommended actions
↓
Things user should avoid
↓
Emergency services needed
↓
Relevant service categories
↓
Offline knowledge required
↓
Source
↓
Source authority
```

---

# 9. Research Deliverable Format

Do NOT simply send:

```text
20 random links
```

Instead create structured research.

Example:

```markdown
## Severe Bleeding

### Situation
A person is experiencing severe bleeding after an accident.

### Immediate priorities
- ...
- ...

### Avoid
- ...

### Required services
- Ambulance
- Hospital

### Offline importance
CRITICAL

### Sources
1. Official source
2. Institutional source

### Verification date
YYYY-MM-DD
```

---

# 10. RAG Knowledge Research

This is one of Saanvi's **highest-priority responsibilities**.

Satwik needs the source material for the RAG system.

Research and collect information covering:

### Roadside safety

- accident safety
- highway safety
- vehicle breakdown
- puncture
- towing
- stranded motorists
- roadside visibility
- night-time breakdown safety

### Emergency response

- emergency response procedures
- ambulance guidance
- police/emergency contacts
- accident response
- basic emergency guidance

### Vehicle emergencies

- tyre puncture
- overheating
- battery failure
- fuel emergency
- engine breakdown
- vehicle fire

### Location/service information

Research what types of service data RAAHAT should maintain.

---

# 11. Source Authority Hierarchy

Prioritize:

```text
Tier 1
Official government / emergency organizations

Tier 2
Hospitals / recognized institutions / authoritative organizations

Tier 3
Trusted secondary sources

Tier 4
General web content
```

Avoid using random blogs as the primary source for safety-critical instructions.

---

# 12. Research Source Metadata

For every important source record:

```text
source_id
title
organization
authority_level
url
topic
language
retrieved_at
last_verified
notes
```

Example:

```json
{
  "source_id": "src_001",
  "title": "Official Road Safety Guidance",
  "organization": "Example Authority",
  "authority_level": "OFFICIAL",
  "url": "https://example.org",
  "topic": "roadside_safety",
  "language": "en",
  "retrieved_at": "2026-08-20T10:00:00Z"
}
```

---

# 13. Multilingual Research

RAAHAT should support at least:

```text
English
Hindi
Hinglish
```

Research equivalent terminology.

Examples:

```text
puncture
tyre puncture
टायर पंचर
टायर में पंचर
```

And:

```text
accident
हादसा
दुर्घटना
accident ho gaya
```

This material helps Satwik evaluate multilingual retrieval.

---

# 14. RAG Query Dataset

Create a test set for Satwik.

Target:

```text
50–100 queries
```

Include:

### English

```text
What should I do after a tyre puncture?
```

### Hindi

```text
गाड़ी का टायर पंचर हो गया है क्या करूं?
```

### Hinglish

```text
Highway pe tyre puncture ho gaya, ab kya karu?
```

### Emergency

```text
My friend is bleeding heavily after an accident.
```

### Ambiguous

```text
Gaadi ruk gayi hai.
```

### Multi-intent

```text
Accident hua hai aur hospital chahiye.
```

---

# 15. Expected Answer Points

For each test query define:

```text
query
expected_intent
expected_category
required_evidence
expected_answer_points
severity
safety_constraints
language
```

Example:

```json
{
  "query": "Highway pe tyre puncture ho gaya",
  "expected_intent": "roadside_assistance",
  "expected_category": "TYRE_PUNCTURE",
  "required_evidence": [
    "safe_positioning",
    "hazard_lights"
  ],
  "severity": "MEDIUM"
}
```

This becomes Satwik's RAG evaluation dataset.

---

# 16. Offline Knowledge Research

Identify information that must survive internet loss.

Prioritize:

```text
CRITICAL
Emergency guidance
Emergency contacts
Accident safety
Severe bleeding guidance
Vehicle fire safety

HIGH
Puncture guidance
Breakdown safety
Towing guidance
Roadside safety

MEDIUM
General vehicle troubleshooting
```

Do not attempt to put the entire online knowledge base into the offline package.

---

# 17. Offline Service Data Requirements

Research what information is required for:

```text
Hospital
Police
Ambulance
Fire Station
Towing
Puncture Repair
Mechanic
Vehicle Service
Fuel Station
```

For each:

```text
name
category
latitude
longitude
address
phone
retrieved_at
availability status
source
```

This becomes the expected structure for the offline package.

---

# 18. Research on Data Freshness

Determine which data can become stale quickly.

Example:

```text
Provider phone number → may change
Provider location → may change
Provider hours → may change
Emergency guidance → relatively stable
Emergency number → highly important, must be verified
```

Provide recommendations for:

```text
freshness policy
update frequency
offline warning
```

---

# 19. Research on Offline Flutter AI

Research:

- Gemma mobile deployment
- AI Edge
- MediaPipe LLM inference
- model size
- quantization
- Android compatibility
- actual device RAM
- model loading
- latency

Do not make the final model decision purely from documentation.

The actual Android phone must be tested.

---

# 20. Research on Local Embeddings

Investigate:

- EmbeddingGemma
- multilingual embedding alternatives
- model size
- Android compatibility
- latency
- Hindi/Hinglish retrieval quality

Output:

```text
Candidate
Pros
Cons
Model size
Runtime
Language performance
Recommendation
```

---

# PHASE 1B — FLUTTER FOUNDATION

While research is happening, Flutter development proceeds in parallel.

---

# 21. Flutter App Shell

Build:

- splash screen
- authentication screen
- home screen
- bottom navigation if needed
- theme
- reusable components

Do not wait for backend.

Use mock data.

---

# 22. Core Flutter Screens

Initial screens:

```text
Splash
Login
Home
Emergency Assistance
Nearby Services
Route Planner
Offline Pack
Profile / Settings
```

Additional screens can be added after core functionality works.

---

# 23. Home Screen

Should expose:

```text
Emergency Assistance
Nearby Services
Plan Route
Offline Safety Pack
```

The UI should make the emergency function immediately accessible.

---

# 24. Emergency Screen

Initial mock flow:

```text
User describes situation
        ↓
Submit
        ↓
Mock response
        ↓
Incident
Guidance
Nearby services
Actions
```

Do not wait for the real API.

---

# 25. Nearby Services Screen

Support:

```text
Current location
↓
service categories
↓
service cards
```

Each card can show:

```text
name
category
distance
phone
address
cached/live status
```

---

# 26. Route Planner Screen

User selects:

```text
Origin
Destination
```

Then eventually:

```text
route
distance
duration
prepare offline pack
```

For Phase 1 use mocked route data if Google integration is not ready.

---

# 27. Offline Pack Screen

Initial UI:

```text
Route
↓
Pack contents
↓
Estimated size
↓
Download
↓
Progress
↓
Ready
```

It can initially use mock package metadata.

---

# 28. API Client Foundation

Create the API client according to the API contract document.

Required:

```text
base URL
Authorization header
JSON serialization
error handling
timeouts
request IDs
```

Do not hard-code endpoint strings throughout widgets.

---

# 29. Firebase Integration

Saanvi supports Firebase login integration on Flutter.

However:

> Firebase backend ownership belongs to Satwik.

Saanvi's responsibility is primarily:

```text
Flutter
↓
Firebase Auth
↓
obtain ID token
↓
send Authorization header
```

Do not redesign the backend authentication model independently.

---

# 30. Location Integration

Implement:

```text
GPS permission
current location
accuracy
timestamp
```

Return the canonical schema:

```json
{
  "latitude": 22.7196,
  "longitude": 75.8577,
  "accuracy_meters": 8,
  "timestamp": "2026-08-20T12:30:45Z"
}
```

Test:

- permission granted
- permission denied
- GPS unavailable
- low accuracy
- location updates

---

# PHASE 1C — MOCK-DRIVEN DEVELOPMENT

The most important anti-blocking technique:

> **Build the Flutter UI against the API contract using mock responses.**

Example:

```json
{
  "success": true,
  "data": {
    "incident": {
      "incident_type": "TYRE_PUNCTURE",
      "severity": "MEDIUM",
      "confidence": 0.94
    },
    "guidance": {
      "title": "Stay safe",
      "steps": [
        "Move to a safe location."
      ]
    },
    "services": []
  }
}
```

When the real FastAPI endpoint is ready:

```text
mock source
   ↓
replace with HTTP
```

The UI should not need major changes.

---

# PHASE 2 — KNOWLEDGE HANDOFF + CORE FLUTTER INTEGRATION

## Goal

By the end of Phase 2:

```text
Research → RAG-ready data
Flutter → real FastAPI APIs
GPS → backend
Emergency API → mobile UI
Services API → mobile UI
```

---

# 31. RAG Knowledge Handoff

Deliver to Satwik:

```text
01_sources/
02_documents/
03_structured_knowledge/
04_query_dataset/
05_expected_answers/
06_multilingual_terms/
```

Recommended structure:

```text
rag-research/
├── sources.csv
├── emergency_guidance.md
├── roadside_safety.md
├── vehicle_emergencies.md
├── service_categories.md
├── multilingual_terms.csv
└── evaluation_queries.json
```

The exact format can be changed if Satwik's ingestion pipeline requires another format.

---

# 32. RAG Handoff Checklist

Before saying research is complete:

- [ ] sources collected
- [ ] authority level recorded
- [ ] URLs recorded
- [ ] important information extracted
- [ ] duplicated information removed
- [ ] contradictory information flagged
- [ ] multilingual terms prepared
- [ ] evaluation queries created
- [ ] expected answer points created
- [ ] critical information identified
- [ ] offline-critical information identified

---

# 33. Resolve Conflicting Information

If two sources disagree:

```text
Do NOT silently choose one.
```

Mark:

```text
CONFLICT
```

Then provide:

```text
Source A
Source B
reason for preferred source
```

Satwik should know about important conflicts before ingestion.

---

# 34. Real API Integration

Once Santosh exposes stable endpoints:

```text
Flutter
 ↓
API client
 ↓
FastAPI
```

Integrate in this order:

```text
1. Auth
2. Health
3. Emergency assistance
4. Nearby services
5. Route
6. Offline pack
7. Voice
```

---

# 35. API Contract Discipline

If an endpoint does not match the API contract:

```text
STOP
```

Do not silently modify the Flutter model to accommodate an accidental backend mismatch.

First confirm:

```text
Is the contract wrong?
or
Is the implementation wrong?
```

Then update the canonical contract.

---

# 36. Flutter Emergency Integration

Replace mock:

```text
MockEmergencyService
```

with:

```text
EmergencyApiService
```

Request:

```json
{
  "message": "...",
  "language": "hi",
  "location": {},
  "network_mode": "ONLINE",
  "include_services": true
}
```

Render:

```text
incident
guidance
services
recommended actions
AI mode
limitations
```

---

# 37. Nearby Services Integration

Connect:

```text
GPS
 ↓
/services/nearby
 ↓
service cards
```

Ensure:

```text
distance_meters
```

is displayed consistently.

Do not calculate a competing distance in the UI unless explicitly required.

---

# 38. Route Integration

Connect:

```text
origin
destination
 ↓
/routes/plan
 ↓
route
 ↓
prepare offline pack
```

---

# PHASE 3 — OFFLINE PACKAGE + LOCAL AI

## Goal

Make the mobile app useful without internet.

---

# 39. Offline State Detection

Flutter should detect:

```text
ONLINE
LIMITED
OFFLINE
```

The app must expose the current state to the UI.

---

# 40. Offline Storage

Implement local storage for:

```text
offline pack metadata
route
services
emergency knowledge
RAG chunks/index
settings
```

Technology selection should follow the offline architecture decision and benchmarking.

---

# 41. Offline Pack Download

Flow:

```text
User plans route
 ↓
backend creates pack
 ↓
Flutter downloads
 ↓
checksum verification
 ↓
installation
 ↓
Ready
```

If installation fails:

```text
retain previous valid pack
```

---

# 42. Offline Pack UI

Display:

```text
Route
Pack size
Created time
Last updated
Expiry
Included services
Included emergency knowledge
Status
```

---

# 43. Offline AI Integration

Saanvi owns the Flutter-side integration.

Target architecture:

```text
Flutter
 ↓
Offline Orchestrator
 ↓
Local Retrieval
 ↓
Gemma
 ↓
Response
```

Satwik owns the AI/RAG design and model behavior.

Saanvi owns making that system work correctly inside the mobile application.

---

# 44. Local AI States

UI must handle:

```text
MODEL_NOT_INSTALLED
MODEL_LOADING
MODEL_READY
MODEL_ERROR
OFFLINE_RAG_READY
OFFLINE_RAG_UNAVAILABLE
```

---

# 45. Offline Emergency Flow

Example:

```text
Internet OFF
     ↓
GPS
     ↓
User:
"Highway pe tyre puncture ho gaya"
     ↓
Local AI
     ↓
Local RAG
     ↓
Gemma
     ↓
Response
```

The UI should visibly show:

```text
Offline Mode
```

---

# 46. Offline Service Search

Use:

```text
GPS coordinates
+
cached services
```

to find:

```text
nearest relevant service
```

Use deterministic geospatial calculations.

Do not ask Gemma to calculate distances.

---

# 47. Cached Service Warning

Every cached service should expose:

```text
is_cached
retrieved_at
availability_status
```

The UI should communicate:

```text
Cached information
Availability cannot be verified offline
```

---

# 48. Offline Fallback

If Gemma fails:

```text
Gemma
 ↓ failure
Local RAG
 ↓ failure
Deterministic emergency guidance
 ↓ failure
Cached emergency contacts
```

Saanvi must make sure the UI handles each state gracefully.

---

# PHASE 4 — TESTING + HARDENING

## Goal

Find failures before the judges do.

---

# 49. Flutter Test Categories

Test:

### Authentication

- login
- logout
- expired session
- missing token

### Location

- permission
- denied
- GPS unavailable
- low accuracy

### Network

- online
- offline
- network loss during request
- network restoration

### API

- valid response
- malformed response
- timeout
- 401
- 404
- 500

### Offline

- pack missing
- pack corrupted
- old pack
- model missing
- model failure

---

# 50. Emergency Scenario Testing

Test at least:

```text
1. Tyre puncture
2. Accident
3. Severe bleeding
4. Vehicle fire
5. Breakdown
6. Stranded user
7. Need hospital
8. Need ambulance
9. Need police
10. Hindi query
11. Hinglish query
12. Offline query
```

---

# 51. UI Failure States

Every major screen should have:

```text
loading
success
empty
error
offline
retry
```

Never assume the backend always succeeds.

---

# 52. Offline Failure Tests

Simulate:

```text
No internet
+
No GPS
```

Expected:

```text
Clear limitation
+
cached emergency information
```

Simulate:

```text
No internet
+
Gemma unavailable
```

Expected:

```text
deterministic/cached fallback
```

Simulate:

```text
Corrupted offline pack
```

Expected:

```text
pack rejected
previous valid pack retained
```

---

# 53. Real Device Testing

Do not rely only on emulator.

Test the final demo phone.

Record:

```text
device
Android version
RAM
storage
model load time
local retrieval latency
Gemma response latency
battery impact
```

---

# PHASE 5 — FINAL INTEGRATION + DEMO

## Goal

Make the Flutter application judge-ready.

---

# 54. Final Mobile Demo Flow

Recommended demonstration:

```text
Open RAAHAT
      ↓
Login
      ↓
Home
      ↓
Plan journey
      ↓
Prepare Offline Safety Pack
      ↓
Show package contents
      ↓
Disable internet
      ↓
Show OFFLINE indicator
      ↓
GPS remains available
      ↓
User reports:
"Highway pe tyre puncture ho gaya"
      ↓
Local retrieval
      ↓
Gemma response
      ↓
Cached nearby puncture/mechanic services
      ↓
Show cached-data warning
```

---

# 55. Judge Questions Saanvi Should Be Ready For

## “Why Flutter?”

Answer:

> “We need a mobile-first emergency experience with GPS, local storage and on-device AI. Flutter lets us build the mobile interface while keeping the application architecture manageable.”

---

## “What happens when internet disappears?”

Answer:

> “The app switches to its offline layer. GPS continues to provide location, the route-aware offline package provides cached services and emergency knowledge, local retrieval finds relevant information, and Gemma generates a grounded response.”

---

## “Can you find a new mechanic offline?”

Answer:

> “No live discovery is possible without connectivity. We use the services cached along the planned route and clearly identify them as cached. Once connectivity returns, the data can be refreshed.”

---

## “Is Gemma the source of truth?”

Answer:

> “No. Gemma is the local generation layer. The system retrieves trusted cached information first and uses Gemma to interpret and communicate that information.”

---

## “What if Gemma fails?”

Answer:

> “The system has graceful fallback levels. It can use local retrieved information or deterministic emergency guidance rather than becoming completely unusable.”

---

# 56. Phase Completion Rules

A phase is NOT complete because:

```text
"I wrote the code."
```

A phase is complete when:

```text
deliverable exists
+
tested
+
usable by next phase
+
communicated to teammate
```

---

# 57. Phase 1 Exit Criteria

Saanvi can move to Phase 2 when:

- [ ] domain research complete
- [ ] critical emergency scenarios identified
- [ ] RAG sources collected
- [ ] sources structured
- [ ] multilingual terminology prepared
- [ ] 50–100 evaluation queries created
- [ ] expected answer points created
- [ ] offline-critical information identified
- [ ] Flutter project bootstrapped
- [ ] core screens exist
- [ ] API client skeleton exists
- [ ] location module works
- [ ] mock API responses render correctly

---

# 58. Phase 2 Exit Criteria

- [ ] research handed to Satwik
- [ ] real emergency API integrated
- [ ] real services API integrated
- [ ] route API integrated
- [ ] authentication integrated
- [ ] API errors handled
- [ ] offline-pack UI integrated
- [ ] mobile app works against backend

---

# 59. Phase 3 Exit Criteria

- [ ] offline state detection
- [ ] offline package download
- [ ] package verification
- [ ] local service search
- [ ] local RAG integrated
- [ ] Gemma integrated
- [ ] offline emergency response works
- [ ] fallback works
- [ ] cached-data warnings work

---

# 60. Phase 4 Exit Criteria

- [ ] real device tested
- [ ] network-loss tested
- [ ] GPS failure tested
- [ ] API failures tested
- [ ] model failure tested
- [ ] corrupted pack tested
- [ ] Hindi tested
- [ ] Hinglish tested
- [ ] UI polished

---

# 61. Communication Protocol With Team

Saanvi should regularly communicate:

```text
RESEARCH READY
```

when research can be consumed.

And:

```text
FLUTTER READY
```

when a feature can be integrated.

And:

```text
BLOCKED
```

when something genuinely blocks progress.

Every blocked message should state:

```text
What is blocked?
Why?
Who owns the dependency?
What can I work on meanwhile?
```

---

# 62. Dependency Map

## Saanvi → Satwik

Saanvi provides:

```text
RAG sources
structured knowledge
multilingual terms
evaluation dataset
offline-critical knowledge
data quality findings
```

Satwik uses these for:

```text
RAG ingestion
retrieval evaluation
grounding
offline RAG
AI testing
```

---

## Satwik → Saanvi

Satwik provides:

```text
RAG API contract
AI response schema
offline AI interface
Gemma runtime requirements
local RAG requirements
```

Saanvi uses these for Flutter integration.

---

## Santosh → Saanvi

Santosh provides:

```text
FastAPI endpoints
API availability
Google service results
route results
offline pack endpoint
auth/backend integration
```

Saanvi consumes them through the API contract.

---

## Saanvi → Santosh

Saanvi provides:

```text
Flutter requirements
mobile API needs
offline pack data requirements
service data fields
location requirements
```

Santosh uses these while implementing backend APIs.

---

# 63. What Saanvi Can Do Without Anyone

If Satwik is busy:

```text
research
RAG dataset
Flutter UI
location
mock APIs
offline UX
testing
```

If Santosh is busy:

```text
research
Flutter
mock API
local storage
offline UI
testing
```

Therefore Saanvi should almost never be idle.

---

# 64. What Saanvi Must Not Do Without Agreement

Do not independently change:

```text
API field names
API response schemas
RAG architecture
backend authentication design
PostgreSQL schema
Google API architecture
AI model architecture
```

If a change seems necessary:

```text
propose → discuss → update contract → implement
```

---

# 65. AI Assistant Instructions

The AI assistant assigned to Saanvi must behave as:

```text
Flutter Engineer
+
Research Assistant
+
Mobile Integration Engineer
+
Offline AI Integration Assistant
```

It must understand that:

- Saanvi is not the sole owner of the backend.
- Satwik owns the main AI/RAG architecture.
- Santosh owns the core React/FastAPI/system integration.
- API contracts are shared and authoritative.
- Research must become actionable deliverables.
- Mock APIs should be used to prevent dependency blocking.
- Do not wait for backend before building Flutter.
- Do not silently modify contracts.
- Do not invent unsupported data.
- Safety-critical information must come from authoritative sources.

---

# 66. AI Assistant Working Style

When Saanvi asks:

> “What should I do now?”

The AI should first determine:

```text
current phase
↓
phase exit criteria
↓
dependencies
↓
highest-priority incomplete task
```

Then provide the next actionable task.

It should avoid giving her tasks belonging primarily to:

- Satwik's AI/RAG implementation
- Santosh's React/FastAPI ownership
- PostgreSQL
- Firebase backend architecture

unless collaboration is explicitly required.

---

# 67. Priority Rules

When choosing between tasks:

```text
P0 = blocks another teammate
P1 = core product functionality
P2 = integration
P3 = polish
P4 = optional USP
```

Saanvi should prioritize:

```text
P0 research handoffs
>
P0 Flutter foundation
>
P1 core mobile features
>
P1 offline foundation
>
P2 local AI integration
>
P3 UX polish
>
P4 optional features
```

---

# 68. Anti-Overengineering Rule

The hackathon is 24 hours.

Do not spend hours building:

- complex state architecture
- unnecessary animations
- elaborate local database abstractions
- unused screens
- unnecessary design systems
- features that are not in the judging demo

The goal is:

```text
working
reliable
demonstrable
```

not production-scale architecture.

---

# 69. Final Saanvi Responsibility Map

```text
SAANVI
│
├── RESEARCH
│   ├── Problem/domain research
│   ├── Emergency scenarios
│   ├── RAG source collection
│   ├── Source verification
│   ├── Multilingual terminology
│   ├── RAG evaluation dataset
│   ├── Offline-critical knowledge
│   └── Data freshness research
│
├── FLUTTER
│   ├── App shell
│   ├── Authentication UI/integration
│   ├── Home
│   ├── Emergency
│   ├── Nearby services
│   ├── Route planning
│   ├── Offline pack
│   └── Profile/settings
│
├── MOBILE INFRASTRUCTURE
│   ├── GPS
│   ├── Network state
│   ├── API client
│   ├── Local storage
│   └── Offline package management
│
├── OFFLINE AI INTEGRATION
│   ├── Local RAG integration
│   ├── Gemma integration
│   ├── Local service search
│   └── Offline fallback UI
│
└── VALIDATION
    ├── Scenario testing
    ├── Offline testing
    ├── Device testing
    ├── Failure testing
    └── Final demo
```

---

# 70. Final Definition of Done

Saanvi's work is complete when the following statement is true:

> **RAAHAT's Flutter application can authenticate a user, obtain location, communicate with the FastAPI backend using the agreed contracts, display emergency guidance and nearby services, prepare and consume a route-aware offline package, detect loss of connectivity, perform local retrieval/Gemma-assisted emergency assistance when available, gracefully fall back when local AI fails, and demonstrate the complete offline roadside-assistance flow on the actual Android device.**

At the same time:

> **Satwik has received structured, authoritative, multilingual, evaluation-ready knowledge that can be ingested directly into the RAG pipeline without repeating the research.**

That is the actual success criterion for Saanvi's role.

---

# 71. One-Line Mission

> **Research the knowledge RAAHAT needs, turn that research into clean inputs for the AI/RAG system, and build the Flutter/mobile experience that makes both the online and offline intelligence usable in the real world.**

