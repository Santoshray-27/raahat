# RAAHAT — Extremely Detailed System Architecture & End-to-End Flow

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Team:** Solution Savvy  
**Architecture status:** Implementation baseline  
**Document purpose:** Show exactly how RAAHAT works from the two user entry points — React Web and Flutter Mobile — through authentication, location, FastAPI, AI orchestration, RAG, Google Maps/Places, PostgreSQL, offline infrastructure, Sarvam voice, and optional agentic actions.

---

# 1. Architecture Philosophy

RAAHAT is not a map replacement.

Its architecture is based on:

> **Understand the situation → determine what the user needs → retrieve the right information → find the right nearby service → rank it → explain the recommendation → optionally take action.**

The system deliberately separates different classes of problems:

| Problem | Primary component |
|---|---|
| Who is the user? | Firebase Auth |
| Where is the user? | GPS / browser geolocation |
| What happened? | LLM + deterministic rules |
| What knowledge applies? | Hybrid RAG |
| What services are nearby? | Google Places |
| What service is best? | Decision + ranking engine |
| What route should be taken? | Google Routes / Maps |
| What structured data belongs to user? | PostgreSQL |
| What if internet disappears? | Flutter local database + offline pack |
| How does AI speak? | Sarvam |
| How does AI act? | Controlled tool/action layer |
| How does AI work without internet? | Gemma + offline RAG |

---

# 2. Complete System — Top-Level Diagram

```text
                                      ┌───────────────────────────────┐
                                      │            USER               │
                                      │                               │
                                      │  Text / Voice / Location /    │
                                      │  Emergency / Route Request    │
                                      └───────────────┬───────────────┘
                                                      │
                              ┌───────────────────────┴───────────────────────┐
                              │                                               │
                              ▼                                               ▼
                    ┌───────────────────┐                           ┌───────────────────┐
                    │    REACT WEB      │                           │   FLUTTER MOBILE  │
                    │                   │                           │                   │
                    │ Browser UI        │                           │ Native Mobile UI  │
                    │ Online-first      │                           │ Online + Offline  │
                    └─────────┬─────────┘                           └─────────┬─────────┘
                              │                                               │
                              │ HTTPS / REST                                  │ HTTPS / REST
                              │                                               │
                              └──────────────────────┬────────────────────────┘
                                                     │
                                                     ▼
                                      ┌──────────────────────────┐
                                      │       FIREBASE AUTH       │
                                      │                          │
                                      │ Signup / Login / Session │
                                      │ ID Token                 │
                                      └────────────┬─────────────┘
                                                   │
                                                   │ Firebase ID Token
                                                   ▼
                                      ┌──────────────────────────┐
                                      │         FASTAPI           │
                                      │       API GATEWAY         │
                                      └────────────┬─────────────┘
                                                   │
                                                   ▼
                                      ┌──────────────────────────┐
                                      │  AUTH MIDDLEWARE /        │
                                      │  TOKEN VERIFICATION       │
                                      └────────────┬─────────────┘
                                                   │
                                                   ▼
                                      ┌──────────────────────────┐
                                      │   REQUEST VALIDATION      │
                                      │   + USER CONTEXT          │
                                      └────────────┬─────────────┘
                                                   │
                                                   ▼
                                      ┌──────────────────────────┐
                                      │     AI ORCHESTRATOR       │
                                      │                          │
                                      │ Intent / Routing / Tools │
                                      └────────────┬─────────────┘
                                                   │
                 ┌─────────────────┬──────────────┼──────────────┬──────────────────┐
                 │                 │              │              │                  │
                 ▼                 ▼              ▼              ▼                  ▼
          ┌────────────┐    ┌────────────┐ ┌─────────────┐ ┌────────────┐    ┌────────────┐
          │   GROQ /   │    │    RAG     │ │   GOOGLE    │ │ POSTGRESQL │    │   ACTION   │
          │    LLM     │    │  ENGINE    │ │ PLACES/API  │ │            │    │   TOOLS    │
          └─────┬──────┘    └─────┬──────┘ └──────┬──────┘ └─────┬──────┘    └─────┬──────┘
                │                  │               │               │                 │
                │                  │               │               │          ┌──────┼──────┐
                │                  │               │               │          │      │      │
                ▼                  ▼               ▼               ▼          ▼      ▼      ▼
           Structured         Knowledge       Nearby Places    Users /     Call   Navigate  SOS
           reasoning          retrieval       / Details       Incidents
                                │
                         ┌──────┴───────┐
                         │              │
                         ▼              ▼
                       BM25          Vector
                         │              │
                         └──────┬───────┘
                                ▼
                           Fusion/Retrieval
                                │
                                ▼
                             Reranker
                                │
                                ▼
                        Grounded Context
                                │
                                └───────────────┐
                                                │
                                                ▼
                                      ┌──────────────────────┐
                                      │  DECISION ENGINE     │
                                      │                      │
                                      │ Incident + Severity  │
                                      │ Required Services    │
                                      │ Ranking              │
                                      └────────────┬─────────┘
                                                   │
                                                   ▼
                                      ┌──────────────────────────┐
                                      │       ACTION PLAN        │
                                      │                          │
                                      │ Guidance / Services /    │
                                      │ Navigation / Call / SOS  │
                                      └────────────┬─────────────┘
                                                   │
                              ┌────────────────────┼────────────────────┐
                              │                    │                    │
                              ▼                    ▼                    ▼
                       React Response      Flutter Response       Sarvam Voice
                                                                       │
                                                                       ▼
                                                                   User Voice
```

---

# 3. Two Entry Points

RAAHAT has two fundamentally different application entry paths.

## Entry Point A — React Web

```text
User opens browser
       ↓
React application loads
       ↓
Firebase authentication
       ↓
Browser location permission
       ↓
Online FastAPI interaction
       ↓
Google Places / RAG / PostgreSQL / AI
       ↓
React UI
```

## Entry Point B — Flutter Mobile

```text
User opens mobile application
       ↓
Flutter application loads
       ↓
Firebase authentication
       ↓
Native GPS permission
       ↓
Network detection
       ↓
       ┌───────────────┐
       │               │
    ONLINE           OFFLINE
       │               │
       ▼               ▼
   FastAPI          Local DB
       │               │
       │             Gemma
       │               │
       │          Offline RAG
       │               │
       └───────┬───────┘
               ▼
           User result
```

---

# 4. ENTRY A — USER OPENS REACT WEB APP

## 4.1 Browser Startup

```text
User
 ↓
https://raahat...
 ↓
React application
 ↓
Load configuration
 ↓
Initialize:
- router
- authentication state
- API client
- global state
- UI
 ↓
Check Firebase session
```

---

# 5. React Authentication Flow

```text
                React
                  │
                  ▼
          Is user authenticated?
             /           \
           NO             YES
           │               │
           ▼               ▼
       Login/Signup     Load profile
           │               │
           ▼               ▼
      Firebase Auth     Firebase ID Token
           │               │
           └───────┬───────┘
                   ▼
               FastAPI
                   │
                   ▼
          Verify Firebase Token
                   │
                   ▼
            Extract Firebase UID
                   │
                   ▼
             PostgreSQL User
                   │
                   ▼
             User Session
```

---

# 6. React Login

```text
User enters credentials
        ↓
Firebase Auth
        ↓
Authentication successful?
      /       \
    NO         YES
    │           │
    ▼           ▼
Error        ID Token
                │
                ▼
             FastAPI
                │
                ▼
          /users/me
                │
                ▼
             Dashboard
```

---

# 7. React Dashboard Startup

After authentication:

```text
Dashboard
   │
   ├── Request browser location
   │
   ├── Load user profile
   │
   ├── Load saved routes
   │
   ├── Load emergency contacts
   │
   ├── Initialize map
   │
   └── Check network
```

---

# 8. React Location Flow

```text
React
 ↓
navigator.geolocation
 ↓
Permission?
 ├── DENIED → show manual location option
 ├── ERROR → show retry/manual location
 └── GRANTED
       ↓
 latitude + longitude
       ↓
 UI state
       ↓
 FastAPI request when needed
```

The browser does not permanently track the user by default.

---

# 9. React — User Starts Emergency

Example:

> “My tyre got punctured on the highway.”

```text
User
 ↓
React Emergency Input
 ↓
POST /emergency-assistance
 ↓
FastAPI
```

Request:

```json
{
  "message": "My tyre got punctured on the highway",
  "location": {
    "latitude": 22.7,
    "longitude": 75.8
  },
  "language": "en",
  "mode": "online"
}
```

---

# 10. FastAPI Entry Pipeline

```text
HTTP Request
     ↓
CORS / HTTPS
     ↓
Authentication Middleware
     ↓
Firebase Token Verification
     ↓
User Identity
     ↓
Pydantic Request Validation
     ↓
Rate Limit / Abuse Checks
     ↓
Request Context
     ↓
AI Orchestrator
```

---

# 11. AI Orchestrator

The orchestrator is the brain that decides which systems need to be called.

```text
                  USER QUERY
                      │
                      ▼
              Query Understanding
                      │
                      ▼
             Structured Situation
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       Incident     Severity    Language
          │           │           │
          └───────────┼───────────┘
                      ▼
               Intent / Needs
                      │
                      ▼
              Tool/Source Router
                      │
       ┌──────────────┼─────────────────┐
       │              │                 │
       ▼              ▼                 ▼
      RAG           Places           Database
       │              │                 │
       └──────────────┼─────────────────┘
                      ▼
               Decision Engine
                      │
                      ▼
               Service Ranking
                      │
                      ▼
                Action Plan
```

---

# 12. Query Understanding

LLM receives:

```text
User message
+
location
+
language
+
optional previous conversation
```

It produces structured information.

Example:

```json
{
  "incident_type": "tyre_puncture",
  "severity": "medium",
  "injury": false,
  "required_services": [
    "puncture_repair",
    "mobile_mechanic",
    "towing"
  ],
  "requires_emergency_services": false
}
```

---

# 13. AI Safety Boundary

The LLM does not directly control the system.

```text
                  LLM
                   │
                   ▼
             Structured output
                   │
                   ▼
          Validation / Rules
                   │
                   ▼
          Decision Engine
                   │
                   ▼
           Allowed actions
```

This prevents:

- arbitrary tool calls
- unsupported claims
- accidental emergency actions
- hallucinated providers

---

# 14. Incident Classification

Example:

```text
"My friend is bleeding after an accident."
```

↓

```json
{
  "incident_type": "accident",
  "injury": true,
  "severity": "critical"
}
```

↓

Deterministic escalation rules:

```text
injury = true
        ↓
critical/high priority
        ↓
ambulance
hospital
police
```

---

# 15. Service Requirement Engine

```text
Incident
   ↓
Rules + AI
   ↓
Required service categories
```

Examples:

```text
TYRE PUNCTURE
    ↓
puncture repair
mobile mechanic
towing
```

```text
ACCIDENT + INJURY
    ↓
ambulance
hospital
police
towing
```

```text
FUEL EMERGENCY
    ↓
fuel station
roadside assistance
```

---

# 16. Google Places Flow

For live online service discovery:

```text
Required service types
        ↓
Current coordinates
        ↓
Google Places Nearby Search
        ↓
Candidate providers
        ↓
Normalize provider data
        ↓
Optional Place Details
        ↓
Service ranking
```

---

# 17. Google Places Internal Architecture

```text
FastAPI
  │
  ▼
Places Client
  │
  ├── Type mapping
  │
  ├── Location
  │
  ├── Radius
  │
  ├── Result limits
  │
  └── Field selection
  │
  ▼
Google Places
  │
  ▼
Raw results
  │
  ▼
Provider Normalizer
  │
  ▼
Internal Provider Model
```

---

# 18. Provider Normalization

Google data becomes:

```json
{
  "provider_id": "google:abc123",
  "name": "ABC Tyres",
  "type": "puncture_repair",
  "latitude": 22.701,
  "longitude": 75.801,
  "address": "...",
  "phone": "...",
  "source": "google_places"
}
```

This means the rest of RAAHAT does not need to understand Google-specific response formats.

---

# 19. Service Ranking Engine

```text
Candidate providers
       │
       ▼
Filter invalid results
       │
       ▼
Calculate:
- incident suitability
- category match
- distance
- route distance/time
- freshness
- verification
- accessibility
       │
       ▼
Score
       │
       ▼
Sort
       │
       ▼
Top N providers
```

---

# 20. Example — Tyre Puncture

Suppose Google returns:

```text
Mechanic A — 1.0 km
General Service B — 0.7 km
Puncture Shop C — 1.4 km
Towing D — 2.0 km
```

The system should NOT simply select B because it is closest.

Instead:

```text
Puncture relevance:
C >>> A > B > D

Distance:
B > A > C > D

Final ranking:
C
A
B
D
```

The exact score weights are still a tunable implementation detail.

---

# 21. RAG Decision

RAG is called only when the user needs knowledge.

Example:

> “What should I do if my friend is bleeding?”

```text
User question
     ↓
AI Orchestrator
     ↓
Knowledge required?
     ↓
YES
     ↓
RAG
```

For:

> “Find the nearest mechanic.”

RAG is NOT required.

---

# 22. RAG Architecture

```text
                USER QUERY
                    │
                    ▼
              Query Analysis
                    │
                    ▼
             Metadata Filters
                    │
          ┌─────────┴─────────┐
          │                   │
          ▼                   ▼
        BM25               Vector
          │                   │
          └─────────┬─────────┘
                    ▼
                Fusion
                    │
                    ▼
              Top 30-50
                    │
                    ▼
                Reranker
                    │
                    ▼
                 Top 5-10
                    │
                    ▼
            Authority/Source
               Validation
                    │
                    ▼
             Grounded Context
                    │
                    ▼
                  LLM
                    │
                    ▼
             Grounded Answer
```

---

# 23. RAG Data Flow

```text
Trusted sources
     ↓
Ingestion
     ↓
Cleaning
     ↓
Metadata
     ↓
Contextualization
     ↓
Chunking
     ↓
Embeddings
     ↓
Vector index
     +
BM25 index
```

---

# 24. RAG Metadata

Every chunk should carry metadata such as:

```text
document_id
chunk_id
source
authority
country
state
region
language
domain
emergency_type
severity
retrieved_at
verified_at
version
```

---

# 25. RAG Retrieval Example

User:

> “What should I do if someone is bleeding heavily?”

```text
Query
 ↓
language = English
domain = first_aid
emergency_type = bleeding
severity = critical
 ↓
Metadata filtering
 ↓
BM25 + vector
 ↓
fusion
 ↓
reranking
 ↓
top trusted chunks
 ↓
LLM
 ↓
grounded response
```

---

# 26. RAG Does Not Find Nearby Providers

Important boundary:

```text
"What should I do?"
        ↓
       RAG

"Which hospital is nearby?"
        ↓
     Google Places

"Which provider is best?"
        ↓
Decision Engine

"What is my saved route?"
        ↓
PostgreSQL / local DB
```

---

# 27. Response Synthesis

The final response can combine multiple sources.

Example:

```text
User:
"My friend is injured after an accident.
Find help and tell me what to do."

                 AI Orchestrator
                        │
         ┌──────────────┼──────────────┐
         ▼              ▼              ▼
        RAG          Places         PostgreSQL
         │              │              │
         │              │              │
         └──────────────┼──────────────┘
                        ▼
                Decision Engine
                        │
                        ▼
                 Final response
```

Final response:

```text
This appears to be a high-priority accident.

DO NOW:
[grounded emergency guidance]

NEAREST RECOMMENDED HELP:
1. Hospital A — 2.1 km
2. Ambulance B — 2.5 km
3. Police C — 3.0 km

[CALL] [NAVIGATE]
```

---

# 28. PostgreSQL Flow

```text
FastAPI
   │
   ▼
Database Service
   │
   ├── Users
   ├── Incidents
   ├── Routes
   ├── Providers
   ├── Emergency Contacts
   ├── Verification
   ├── Offline Packs
   └── Action Logs
```

---

# 29. User Data Flow

```text
Firebase UID
    ↓
FastAPI
    ↓
User lookup
    ↓
PostgreSQL
    ↓
User-specific resources
```

Never trust a client-provided user ID without checking it against the authenticated Firebase identity.

---

# 30. Route Planning Flow — React

```text
User
 ↓
Enter destination
 ↓
Current location or manual start
 ↓
FastAPI
 ↓
Google Routes
 ↓
Route geometry
 ↓
Route summary
 ↓
React map
```

---

# 31. Route-Aware Offline Preparation

This is a major feature.

```text
User
 ↓
"Indore → Bhopal"
 ↓
Route API
 ↓
Route geometry
 ↓
Create emergency corridor
 ↓
Find relevant service categories
 ↓
Query Google Places along corridor
 ↓
Collect:
- hospitals
- police
- mechanics
- puncture
- towing
- fuel
 ↓
Collect emergency contacts
 ↓
Collect relevant RAG knowledge
 ↓
Package data
 ↓
Download to Flutter device
```

---

# 32. Offline Pack Architecture

```text
                    ONLINE
                       │
              ┌────────┴────────┐
              │                 │
          Google APIs       PostgreSQL
              │                 │
              └────────┬────────┘
                       ▼
                Offline Pack
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Providers    Guidance      Metadata
          │            │            │
          └────────────┼────────────┘
                       ▼
                  Flutter Device
```

---

# 33. Flutter Startup Flow

```text
User opens app
      ↓
Flutter initializes
      ↓
Check Firebase session
      ↓
Check permissions
      ↓
Check network
      ↓
Load local database
      ↓
Load offline pack metadata
      ↓
Load current location
      ↓
Home screen
```

---

# 34. Flutter Online Mode

```text
Flutter
  │
  ▼
Network available?
  │
 YES
  │
  ▼
FastAPI
  │
  ├── AI
  ├── RAG
  ├── Google Places
  ├── PostgreSQL
  └── Tools
  │
  ▼
Response
  │
  ▼
Flutter UI
```

---

# 35. Flutter Offline Mode

```text
Flutter
  │
  ▼
Network unavailable
  │
  ▼
Offline Mode
  │
  ├── GPS
  │
  ├── Local DB
  │
  ├── Offline RAG
  │
  └── Gemma
  │
  ▼
Offline Decision Engine
  │
  ▼
Local Response
```

---

# 36. Offline Nearby Service Flow

Example:

> User is offline and needs a mechanic.

```text
User
 ↓
"Need a mechanic"
 ↓
Gemma / local understanding
 ↓
required_service = mechanic
 ↓
GPS
 ↓
current coordinates
 ↓
Local DB spatial query
 ↓
cached mechanics within radius
 ↓
distance calculation
 ↓
ranking
 ↓
Flutter service cards
```

Gemma does not search raw coordinates.

---

# 37. Offline Emergency Flow

Example:

> User is offline and reports an injury.

```text
User
 ↓
Voice/text
 ↓
Gemma
 ↓
Incident classification
 ↓
Severity
 ↓
Offline RAG
 ↓
Emergency guidance
 ↓
Local cached emergency services
 ↓
GPS
 ↓
Local service ranking
 ↓
Flutter emergency UI
```

---

# 38. Offline Data Freshness

Each cached provider should carry:

```text
last_synced_at
source
```

UI:

```text
Cached information
Last updated: 2 hours ago
```

If old:

```text
⚠ Information may be outdated
```

---

# 39. Network Recovery

When connection returns:

```text
Offline
 ↓
Network restored
 ↓
Sync Manager
 ↓
Compare versions
 ↓
Upload permitted local state
 ↓
Download updated:
- providers
- emergency data
- route packs
- RAG updates
 ↓
Update local DB
```

---

# 40. Sarvam Voice Flow

RAAHAT already has a working basic Sarvam → FastAPI flow.

Final architecture:

```text
                 USER
                  │
                  │ Voice
                  ▼
             SARVAM AGENT
                  │
             Speech → Text
                  │
                  ▼
               FastAPI
                  │
                  ▼
          AI Orchestrator
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
      RAG       Places      DB
       │          │          │
       └──────────┼──────────┘
                  ▼
             Final answer
                  │
                  ▼
               Sarvam
                  │
             Text → Speech
                  │
                  ▼
                 USER
```

---

# 41. Sarvam Voice — Example

User says:

> “Meri gaadi highway pe kharab ho gayi hai.”

```text
Sarvam STT
 ↓
Hindi text
 ↓
FastAPI
 ↓
Incident = vehicle_breakdown
 ↓
Need = mechanic/towing
 ↓
Google Places
 ↓
Ranking
 ↓
Response
 ↓
Sarvam TTS
 ↓
"Mainne aapke paas..."
```

---

# 42. Agentic Provider Calling

This is an advanced feature.

```text
User
 ↓
"Can you call this mechanic?"
 ↓
AI identifies provider
 ↓
System displays confirmation
 ↓
USER APPROVES
 ↓
FastAPI Tool Layer
 ↓
Telephony Provider
 ↓
Provider phone
 ↓
Voice Agent
 ↓
Explains:
- user situation
- approximate/current location
- requested service
 ↓
Provider responds
 ↓
STT / agent understanding
 ↓
Structured result
 ↓
FastAPI
 ↓
Database/action log
 ↓
User
```

---

# 43. Agentic Call Permission Boundary

```text
LLM
 ↓
requests call_provider
 ↓
Backend sees:
requires_confirmation = true
 ↓
STOP
 ↓
Ask user
 ↓
YES?
 ├── NO → cancel
 └── YES → execute
```

The LLM cannot bypass the confirmation requirement.

---

# 44. Agentic Call Result

Example:

```json
{
  "provider": "ABC Mechanics",
  "can_assist": true,
  "estimated_arrival": "20-30 minutes",
  "service": "puncture repair",
  "notes": "Provider requested current location"
}
```

If the agent cannot understand the provider:

```text
call_status = needs_human_followup
```

Never invent a successful confirmation.

---

# 45. Emergency Escalation Flow

Important dynamic behavior.

```text
Initial:
"My car stopped."
        ↓
vehicle_breakdown
        ↓
mechanic/towing

User:
"My friend is bleeding."
        ↓
New information
        ↓
Re-run classification
        ↓
accident/injury
        ↓
severity = critical
        ↓
ambulance + hospital + police
        ↓
Emergency guidance
```

The system should be able to update the incident state.

---

# 46. Full Emergency Flow — Online

```text
USER
 │
 │ opens React / Flutter
 ▼
AUTH
 │
 │ Firebase
 ▼
LOCATION
 │
 │ GPS
 ▼
INPUT
 │
 │ text / voice
 ▼
FASTAPI
 │
 ▼
AUTH VERIFY
 │
 ▼
VALIDATE REQUEST
 │
 ▼
AI ORCHESTRATOR
 │
 ▼
QUERY UNDERSTANDING
 │
 ├───────────────┐
 │               │
 ▼               ▼
INCIDENT       LANGUAGE
 │
 ▼
SEVERITY
 │
 ▼
SERVICE REQUIREMENTS
 │
 ├───────────────┬─────────────────┐
 │               │                 │
 ▼               ▼                 ▼
RAG           GOOGLE PLACES     POSTGRES
 │               │                 │
 │               ▼                 │
 │          CANDIDATES              │
 │               │                 │
 └───────────────┼─────────────────┘
                 ▼
          SERVICE NORMALIZATION
                 │
                 ▼
           RANKING ENGINE
                 │
                 ▼
            DECISION ENGINE
                 │
                 ▼
             ACTION PLAN
                 │
       ┌─────────┼─────────┐
       ▼         ▼         ▼
    Guidance   Services  Actions
                         │
                    ┌────┼────┐
                    ▼    ▼    ▼
                   Call Nav  SOS
                         │
                         ▼
                    USER RESULT
```

---

# 47. Full Emergency Flow — Offline

```text
USER
 │
 ▼
FLUTTER
 │
 ▼
NETWORK CHECK
 │
 └── OFFLINE
       │
       ▼
     GPS
       │
       ▼
LOCAL DATABASE
       │
       ├── cached providers
       ├── emergency contacts
       ├── route data
       └── metadata
       │
       ▼
     GEMMA
       │
       ▼
INCIDENT UNDERSTANDING
       │
       ▼
LOCAL DECISION ENGINE
       │
       ├──────────────┐
       ▼              ▼
LOCAL SPATIAL      OFFLINE RAG
SEARCH                │
       │              │
       └──────┬───────┘
              ▼
        LOCAL RESPONSE
              │
              ▼
          FLUTTER UI
```

---

# 48. Full Voice Flow

```text
USER
 │
 │ speaks
 ▼
SARVAM
 │
 │ STT
 ▼
TEXT
 │
 ▼
FASTAPI
 │
 ▼
AUTH / SESSION
 │
 ▼
AI ORCHESTRATOR
 │
 ├── LLM
 ├── RAG
 ├── Places
 ├── DB
 └── Tools
 │
 ▼
DECISION ENGINE
 │
 ▼
RESPONSE
 │
 ▼
SARVAM TTS
 │
 ▼
USER HEARS RESPONSE
```

---

# 49. Full Agentic Flow

```text
USER
 │
 ▼
VOICE/TEXT
 │
 ▼
AI ORCHESTRATOR
 │
 ▼
IDENTIFY POSSIBLE ACTION
 │
 ▼
"CALL PROVIDER"
 │
 ▼
PERMISSION CHECK
 │
 ├── NO → return to user
 │
 └── YES
       │
       ▼
 TOOL EXECUTION
       │
       ▼
 TELEPHONY
       │
       ▼
 PROVIDER
       │
       ▼
 PROVIDER RESPONSE
       │
       ▼
 AGENT UNDERSTANDING
       │
       ▼
 STRUCTURED RESULT
       │
       ▼
 USER
```

---

# 50. Data Flow — Online

```text
                ┌─────────────────┐
                │      USER       │
                └────────┬────────┘
                         │
              ┌──────────┴───────────┐
              │                      │
           React                  Flutter
              │                      │
              └──────────┬───────────┘
                         ▼
                    FastAPI
                         │
                 ┌───────┴───────┐
                 │               │
              Firebase        PostgreSQL
                 │               │
                 └───────┬───────┘
                         │
                   AI Orchestrator
                         │
       ┌─────────┬───────┼─────────┬─────────┐
       ▼         ▼       ▼         ▼         ▼
      LLM       RAG    Places    Routes    Tools
       │         │       │         │         │
       └─────────┴───────┼─────────┴─────────┘
                         ▼
                   Decision Engine
                         │
                         ▼
                    Final Result
```

---

# 51. Data Flow — Offline

```text
             FLUTTER DEVICE
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
       GPS       Local DB      Gemma
                    │           │
                    │      Offline RAG
                    │           │
                    └─────┬─────┘
                          ▼
                  Offline Decision
                       Engine
                          │
                          ▼
                     Local Result
                          │
                          ▼
                       USER
```

---

# 52. Database Relationship Diagram

```text
Firebase User
     │
     │ firebase_uid
     ▼
┌───────────────┐
│     USERS     │
└───────┬───────┘
        │
        ├──────────────┐
        │              │
        ▼              ▼
┌───────────────┐  ┌───────────────┐
│    ROUTES     │  │   INCIDENTS   │
└───────┬───────┘  └───────────────┘
        │
        ▼
┌───────────────┐
│ OFFLINE_PACKS │
└───────────────┘

┌──────────────────────┐
│ SERVICE_PROVIDERS    │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ PROVIDER_VERIFICATION│
└──────────────────────┘

┌──────────────────────┐
│ EMERGENCY_CONTACTS   │
└──────────────────────┘

┌──────────────────────┐
│ ACTION_LOGS          │
└──────────────────────┘
```

---

# 53. Authentication + Authorization Architecture

```text
             USER
              │
              ▼
       React / Flutter
              │
              ▼
        Firebase Auth
              │
              ▼
        Firebase ID Token
              │
              ▼
            FastAPI
              │
              ▼
      Verify Firebase Token
              │
              ▼
        Firebase UID
              │
              ▼
         PostgreSQL
              │
              ▼
     User-owned resources
```

---

# 54. Security Boundary

```text
PUBLIC CLIENT
React / Flutter
      │
      │ HTTPS
      ▼
FASTAPI
      │
      ├── Auth
      ├── Validation
      ├── Authorization
      ├── Rate limits
      └── Tool permissions
      │
      ├──────────────┬───────────────┐
      ▼              ▼               ▼
 PostgreSQL       Google           LLM APIs
                 APIs
      │
      └── secrets never sent to client
```

---

# 55. Tool Execution Architecture

```text
AI
 │
 ▼
Tool request
 │
 ▼
Tool Registry
 │
 ▼
Schema Validation
 │
 ▼
Permission Check
 │
 ▼
Confirmation required?
 │
 ├── YES → User confirmation
 │              │
 │              ▼
 │          Execute / Cancel
 │
 └── NO → Execute
```

---

# 56. Example — "Find Me a Mechanic"

```text
User
 │
 ▼
React / Flutter
 │
 ▼
FastAPI
 │
 ▼
LLM
 │
 ▼
incident = breakdown
 │
 ▼
required_service = mechanic
 │
 ▼
Google Places
 │
 ▼
candidate mechanics
 │
 ▼
ranking
 │
 ▼
top 3
 │
 ▼
response
 │
 ├── provider cards
 ├── call
 └── navigate
```

---

# 57. Example — "What Should I Do?"

```text
User
 │
 ▼
FastAPI
 │
 ▼
AI Router
 │
 ▼
Knowledge required
 │
 ▼
Hybrid RAG
 │
 ├── BM25
 ├── Vector
 ├── Fusion
 └── Reranker
 │
 ▼
Trusted context
 │
 ▼
LLM
 │
 ▼
Grounded guidance
 │
 ▼
User
```

---

# 58. Example — "Call the Mechanic for Me"

```text
User
 │
 ▼
AI identifies action
 │
 ▼
Provider selected
 │
 ▼
"Would you like me to call?"
 │
 ├── NO → stop
 │
 └── YES
       │
       ▼
FastAPI tool
       │
       ▼
Telephony provider
       │
       ▼
Mechanic
       │
       ▼
Conversation
       │
       ▼
Structured result
       │
       ▼
User
```

---

# 59. Example — Accident + Injury

```text
User:
"Accident hua hai aur dost ko chot lagi hai."
          │
          ▼
      Sarvam / UI
          │
          ▼
       FastAPI
          │
          ▼
    Query Understanding
          │
          ▼
 accident + injury
          │
          ▼
    Critical/High severity
          │
     ┌────┼─────┐
     ▼    ▼     ▼
  Ambulance Hospital Police
     │      │      │
     └──────┼──────┘
            ▼
      Google Places
            │
            ▼
       Ranking Engine
            │
            ▼
        RAG Guidance
            │
            ▼
      Final Emergency UI
            │
      ┌─────┼─────┐
      ▼     ▼     ▼
     CALL  NAV   SOS
```

---

# 60. Example — Offline Accident

```text
User
 │
 ▼
Flutter
 │
 ▼
No Network
 │
 ▼
GPS
 │
 ▼
Gemma
 │
 ▼
accident + injury
 │
 ▼
Local Decision Engine
 │
 ├───────────────┐
 ▼               ▼
Cached Hospital  Offline RAG
Cached Ambulance Guidance
Cached Police
 │               │
 └───────┬───────┘
         ▼
   Emergency UI
```

---

# 61. Example — Journey Preparation

```text
User
 │
 ▼
Flutter / React
 │
 ▼
Enter route
 │
 ▼
Google Routes
 │
 ▼
Route geometry
 │
 ▼
Backend
 │
 ├── Service discovery
 ├── Emergency contacts
 ├── RAG selection
 └── Offline package creation
 │
 ▼
Download
 │
 ▼
Flutter Local Storage
 │
 ├── Provider data
 ├── Route data
 ├── Emergency contacts
 ├── Guidance
 └── Gemma/RAG package
```

---

# 62. Service Information Freshness

```text
Google / PostgreSQL
        │
        ▼
Provider record
        │
        ├── source
        ├── last_synced
        └── verification
        │
        ▼
Service Ranking
        │
        ▼
User
```

For offline:

```text
cached record
      ↓
last_synced_at
      ↓
fresh enough?
   /       \
 YES        NO
 │           │
use        show stale warning
```

---

# 63. Failure Handling Architecture

```text
                 Request
                    │
                    ▼
               FastAPI
                    │
                    ▼
              AI Orchestrator
                    │
      ┌─────────────┼──────────────┐
      ▼             ▼              ▼
    RAG          Google          Database
      │             │              │
      └─────────────┼──────────────┘
                    │
              any failure?
                /       \
              NO         YES
              │           │
              ▼           ▼
          continue      fallback
                            │
                   ┌────────┼────────┐
                   ▼        ▼        ▼
                 cache    retry    safe response
```

Never fabricate a successful provider result because an external API failed.

---

# 64. Complete Architecture — Detailed Master Diagram

```text
══════════════════════════════════════════════════════════════════════════════
                               USER LAYER
══════════════════════════════════════════════════════════════════════════════

                         ┌───────────────────┐
                         │       USER        │
                         │                   │
                         │ Text              │
                         │ Voice             │
                         │ Location          │
                         │ Route             │
                         │ Emergency         │
                         └─────────┬─────────┘
                                   │
                 ┌─────────────────┴─────────────────┐
                 │                                   │
                 ▼                                   ▼
       ╔════════════════════╗              ╔════════════════════╗
       ║    REACT WEB       ║              ║   FLUTTER MOBILE   ║
       ║                    ║              ║                    ║
       ║ Dashboard          ║              ║ Home               ║
       ║ Map                ║              ║ Emergency Mode     ║
       ║ Route Planning     ║              ║ GPS                ║
       ║ Emergency Input    ║              ║ Offline            ║
       ║ Services           ║              ║ Local DB           ║
       ║ Voice              ║              ║ Gemma              ║
       ╚═════════╤══════════╝              ╚═════════╤══════════╝
                 │                                   │
                 └────────────────┬──────────────────┘
                                  │
                                  ▼
                         ╔══════════════════╗
                         ║  FIREBASE AUTH   ║
                         ║                  ║
                         ║ Login            ║
                         ║ Signup           ║
                         ║ Session          ║
                         ║ ID Token         ║
                         ╚════════╤═════════╝
                                  │
                                  ▼
══════════════════════════════════════════════════════════════════════════════
                              API LAYER
══════════════════════════════════════════════════════════════════════════════

                         ╔══════════════════╗
                         ║     FASTAPI      ║
                         ║                  ║
                         ║ API Gateway      ║
                         ║ Validation       ║
                         ║ Authentication   ║
                         ║ Authorization    ║
                         ║ Rate Limiting    ║
                         ╚════════╤═════════╝
                                  │
                                  ▼
                         ╔══════════════════╗
                         ║ AI ORCHESTRATOR  ║
                         ║                  ║
                         ║ Intent Router    ║
                         ║ Source Router    ║
                         ║ Tool Router      ║
                         ╚════════╤═════════╝
                                  │
                ┌─────────────────┼───────────────────┐
                │                 │                   │
                ▼                 ▼                   ▼
       ╔════════════════╗ ╔════════════════╗ ╔════════════════╗
       ║ QUERY / LLM    ║ ║      RAG       ║ ║   LOCATION    ║
       ║                ║ ║                ║ ║   SERVICES    ║
       ║ Groq           ║ ║ BM25           ║ ║ Google Places ║
       ║ Structured     ║ ║ Vector         ║ ║ Google Routes ║
       ║ extraction     ║ ║ Fusion         ║ ║ Google Maps   ║
       ╚═══════╤════════╝ ║ Reranker       ║ ╚═══════╤════════╝
               │          ╚═══════╤════════╝         │
               │                  │                  │
               └──────────────────┼──────────────────┘
                                  │
                                  ▼
                         ╔══════════════════╗
                         ║ DECISION ENGINE  ║
                         ║                  ║
                         ║ Incident         ║
                         ║ Severity         ║
                         ║ Service Need     ║
                         ║ Ranking          ║
                         ║ Safety Rules     ║
                         ╚════════╤═════════╝
                                  │
                                  ▼
                         ╔══════════════════╗
                         ║   ACTION PLAN    ║
                         ║                  ║
                         ║ Guidance         ║
                         ║ Providers        ║
                         ║ Navigation       ║
                         ║ Call             ║
                         ║ SOS              ║
                         ╚════════╤═════════╝
                                  │
                    ┌─────────────┼──────────────┐
                    │             │              │
                    ▼             ▼              ▼
                 React         Flutter        Sarvam
                 Response      Response       Voice
                                                │
                                                ▼
                                               USER


══════════════════════════════════════════════════════════════════════════════
                              DATA LAYER
══════════════════════════════════════════════════════════════════════════════

                         ╔══════════════════╗
                         ║   POSTGRESQL     ║
                         ║                  ║
                         ║ Users            ║
                         ║ Routes           ║
                         ║ Incidents        ║
                         ║ Providers        ║
                         ║ Verification     ║
                         ║ Emergency Data   ║
                         ║ Offline Packs    ║
                         ║ Action Logs      ║
                         ╚══════════════════╝


══════════════════════════════════════════════════════════════════════════════
                            OFFLINE LAYER
══════════════════════════════════════════════════════════════════════════════

                         ╔══════════════════╗
                         ║ FLUTTER DEVICE   ║
                         ╚════════╤═════════╝
                                  │
               ┌──────────────────┼──────────────────┐
               │                  │                  │
               ▼                  ▼                  ▼
        ╔════════════╗     ╔════════════╗     ╔════════════╗
        ║ Local DB   ║     ║   GEMMA    ║     ║ Offline    ║
        ║            ║     ║            ║     ║ RAG        ║
        ║ Providers  ║     ║ Local AI   ║     ║            ║
        ║ Routes     ║     ║ Reasoning  ║     ║ Guidance   ║
        ║ Contacts   ║     ║            ║     ║ Knowledge  ║
        ╚═════╤══════╝     ╚═════╤══════╝     ╚═════╤══════╝
              │                  │                  │
              └──────────────────┼──────────────────┘
                                 ▼
                         Offline Decision
                             Engine
                                 │
                                 ▼
                            User Response


══════════════════════════════════════════════════════════════════════════════
                              ACTION LAYER
══════════════════════════════════════════════════════════════════════════════

                         AI Orchestrator
                                │
                                ▼
                           Tool Request
                                │
                                ▼
                         Permission Check
                                │
                      ┌─────────┴─────────┐
                      │                   │
                    Denied              Allowed
                      │                   │
                      ▼                   ▼
                    Stop             Tool Execute
                                          │
                             ┌────────────┼────────────┐
                             ▼            ▼            ▼
                          Provider     Navigation     SOS
                            Call
                             │
                             ▼
                          Telephony
                             │
                             ▼
                          Provider
                             │
                             ▼
                        AI Conversation
                             │
                             ▼
                       Structured Result
                             │
                             ▼
                            User
```

---

# 65. End-to-End Golden Path

The single most important working path for the hackathon:

```text
1. User opens Flutter app.
        ↓
2. Firebase session is checked.
        ↓
3. GPS location is obtained.
        ↓
4. User says:
   "My car tyre has punctured."
        ↓
5. AI extracts:
   tyre_puncture / medium
        ↓
6. Decision Engine chooses:
   puncture + mechanic + towing
        ↓
7. Google Places searches nearby providers.
        ↓
8. Providers are normalized.
        ↓
9. Ranking engine evaluates them.
        ↓
10. Top providers returned.
        ↓
11. Flutter displays:
    "Recommended Puncture Repair — 1.4 km"
        ↓
12. User can:
    CALL
    NAVIGATE
        ↓
13. If user asks:
    "Can you call them for me?"
        ↓
14. RAAHAT asks permission.
        ↓
15. User confirms.
        ↓
16. Agentic calling executes.
        ↓
17. Provider confirms assistance.
        ↓
18. RAAHAT reports:
    "They can come in approximately 20 minutes."
```

This is the ideal advanced demo.

---

# 66. Golden Path — Accident

```text
User:
"Accident hua hai aur ek person injured hai."

        ↓

Incident extraction

        ↓

ACCIDENT + INJURY

        ↓

Severity escalation

        ↓

CRITICAL / HIGH

        ↓

Parallel operations

 ┌──────────────┬────────────────┬────────────────┐
 │              │                │                │
 ▼              ▼                ▼                ▼
RAG          Ambulance        Hospital          Police
Guidance     discovery        discovery        discovery

 └──────────────┬────────────────┴────────────────┘
                ▼
          Decision Engine
                ↓
          Ranked assistance
                ↓
       Emergency instructions
                ↓
       CALL / NAVIGATE / SOS
```

---

# 67. Golden Path — Offline

```text
Before journey:

User enters route
       ↓
Backend generates offline pack
       ↓
Flutter downloads
       ↓
User loses network

Later:

User asks for help
       ↓
Flutter detects offline
       ↓
GPS
       ↓
Gemma
       ↓
Local DB
       ↓
Offline RAG
       ↓
Local decision engine
       ↓
Cached provider/guidance
       ↓
User
```

---

# 68. Architecture Rules to Preserve During Coding

## Rule 1

Do not call Google Places from the frontend with secret credentials.

## Rule 2

Do not put API secrets in React or Flutter.

## Rule 3

Do not let the LLM directly execute sensitive tools.

## Rule 4

Do not use RAG to answer live geospatial questions.

## Rule 5

Do not make Gemma perform raw spatial calculations.

## Rule 6

Do not claim provider availability unless it has actually been confirmed.

## Rule 7

Do not store unnecessary location history.

## Rule 8

Do not make offline mode pretend that cached information is live.

## Rule 9

Do not build every feature before the core vertical slice works.

## Rule 10

Every advanced feature must be removable without breaking the P0 product.

---

# 69. Build Boundary

The architecture intentionally has four layers:

```text
PRESENTATION
React + Flutter + Sarvam
        ↓
APPLICATION
FastAPI + Orchestrator
        ↓
INTELLIGENCE
LLM + RAG + Decision Engine
        ↓
INFRASTRUCTURE
Google + PostgreSQL + Firebase + Local DB
```

This separation allows the team to change:

- LLM
- RAG engine
- map provider
- telephony provider
- frontend
- offline model

without rewriting the entire product.

---

# 70. Final Mental Model

When thinking about RAAHAT, remember this sequence:

```text
                    WHAT HAPPENED?
                           │
                           ▼
                     UNDERSTAND IT
                           │
                           ▼
                    HOW SERIOUS?
                           │
                           ▼
                    WHAT IS NEEDED?
                           │
             ┌─────────────┼──────────────┐
             ▼             ▼              ▼
          KNOWLEDGE      SERVICES       ACTION
             │             │              │
             ▼             ▼              ▼
            RAG          PLACES         TOOLS
             │             │              │
             └─────────────┼──────────────┘
                           ▼
                    DECISION ENGINE
                           │
                           ▼
                     BEST NEXT STEP
                           │
                           ▼
                         USER
```

That is the architectural identity of RAAHAT.

---

# 71. Final One-Line Architecture

> **React/Flutter → Firebase Auth → FastAPI → AI Orchestrator → LLM + Hybrid RAG + Google Places + PostgreSQL → Decision & Ranking Engine → Guidance / Services / Navigation / Agentic Actions, with Flutter additionally supporting Local DB + Gemma + Offline RAG when connectivity is unavailable.**
