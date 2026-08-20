# RAAHAT — Detailed Product Requirements & Technical Design Document

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Team:** Solution Savvy  
**Status:** Architecture/PRD baseline — ready to begin implementation  
**Date:** 20 August 2026

---

## 0. Purpose

This document consolidates the decisions, architecture, constraints, research conclusions, and open questions discussed by Solution Savvy.

It is the team's **single source of truth** before and during development.

The goal is to remove architectural confusion while keeping implementation details flexible enough to refine during coding.

---

# 1. Hackathon Context

## SquidHack 2026

- 24-hour offline hackathon at SAGE University, Indore.
- The final project must be built during the hackathon.
- Open-source libraries and AI tools are permitted.
- Judging:
  - Innovation & Creativity — 30%
  - Technical Implementation — 25%
  - Problem Relevance — 20%
  - UX & Design — 10%
  - Scalability & Impact — 15%

## Strategic implications

Optimize for:

1. Strong problem relevance.
2. Visible innovation.
3. A working live demo.
4. Technically defensible architecture.
5. Features realistically achievable within 24 hours.

Explicit team constraints:

- No hardware / IoT.
- No computer vision.
- No deep ML / deep-learning training.
- No expensive infrastructure.
- No blockchain unless it genuinely solves a requirement.
- No fabricated live availability.
- AI tools are allowed, but the team understands and can explain the resulting system.

---

# 2. Team

## Satwik Misra

Primary responsibilities:

- Backend / FastAPI
- AI development
- RAG
- LLM orchestration
- Groq
- Sarvam AI
- STT/TTS
- Voice agent
- Web scraping / Selenium
- Offline RAG
- Blockchain knowledge: Polygon, Solidity, Remix

### Existing voice-agent progress

- FastAPI POST endpoint created.
- Endpoint connected to Sarvam voice-agent workflow.
- Test requests/responses successfully verified.
- Basic Sarvam → FastAPI → response → Sarvam loop is proven.

## Santosh Ray

Primary responsibilities:

- React frontend
- Backend/API support
- Integration
- Product implementation
- Deployment support

Additional strength:

- Has previous deployment experience.

## Saanvi Gupta

Primary responsibilities:

- Flutter/mobile development
- Android
- Research
- Mobile/offline implementation
- AI-assisted development

---

# 3. Existing Team Arsenal

## AI / LLM

- LLM APIs
- Groq
- Sarvam
- LLM orchestration
- Structured outputs
- AI agents

## RAG

- Standard RAG
- Multi-RAG
- Offline RAG
- Web-data RAG
- Document RAG
- Knowledge-base construction

## Voice

- Sarvam STT
- Sarvam TTS
- Voice assistants
- Voice agents
- Multilingual voice

## Data

- Web scraping
- Selenium
- Data extraction
- Web → structured data → knowledge base

## Web / Backend

- React
- FastAPI
- REST APIs
- PostgreSQL
- Firebase Authentication

## Mobile

- Flutter
- Android
- Local/offline AI concept
- Gemma-class small local models

## Blockchain

- Polygon
- Solidity
- Remix

Blockchain is not currently a core part of RAAHAT.

---

# 4. Relevant Previous Experience

## CrisisAI / Rapid Crisis Response

- Crisis-response workflows
- AI classification
- RAG
- Information retrieval
- Emergency/crisis context

## NyayMitra

- Legal information systems
- AI/RAG
- Knowledge assistance

## LexChain

- Contract analysis
- Risk identification
- AI
- Blockchain

## BioFit3D

- Healthcare
- ML/data processing
- FastAPI/backend

## Sports Team Selection System

- Full-stack application
- APIs
- Database
- Authentication
- Role-based workflows

These projects are experience advantages, not projects to copy or submit again.

---

# 5. Problem Statement — SW-17

## AI-Powered Roadside Emergency & Assistance Navigator

Road accident victims and stranded road users can struggle to quickly find the correct emergency or roadside assistance, especially during the critical golden hour.

The system should:

1. Identify user location.
2. Find nearby emergency services.
3. Provide nearby hospitals, police stations and ambulance services.
4. Locate towing, puncture repair, mechanics and vehicle service centers.
5. Prioritize services according to the user's situation.
6. Provide navigation and contact information.
7. Support conversational AI.
8. Provide relevant emergency guidance.
9. Work usefully in low-network/offline conditions.
10. Support different regions/countries.
11. Integrate multiple service providers.
12. Maintain reliable/accurate information.
13. Protect location and personal information.

---

# 6. Product Definition

## RAAHAT is NOT a Google Maps replacement.

Core positioning:

> **Google Maps tells you what is nearby. RAAHAT tells you what to do next.**

Google Maps is treated as infrastructure for location/service discovery and navigation.

RAAHAT adds:

- Situation understanding
- Emergency classification
- Severity assessment
- Service prioritization
- Emergency guidance
- Conversational assistance
- Multilingual interaction
- Offline emergency intelligence
- Optional agentic actions

We deliberately do not rebuild mapping infrastructure.

---

# 7. Core Product Philosophy

The fundamental problem is not:

> “Where is the nearest mechanic?”

The deeper problem is:

> **“I am in an unfamiliar and possibly stressful situation. I don't necessarily know what help I need or what I should do next.”**

### Google Maps

“What is around me?”

### RAAHAT

“What happened → what do I need → what should I do → who can help → what should I do next?”

---

# 8. Primary User Scenarios

Initial scenarios:

1. Road accident + injury.
2. Vehicle breakdown.
3. Tyre puncture.
4. Fuel emergency.
5. Stranded at night.
6. Low/no connectivity.

These scenarios become decision-engine and demo test cases.

---

# 9. High-Level Product Flow

```text
User
 |
 +-- React Web
 |
 +-- Flutter Mobile
 |
 +-- Sarvam Voice Agent
 |
 v
FastAPI
 |
 v
AI / Query Understanding
 |
 v
Decision / Orchestration Layer
 |
 +----------------------+----------------------+
 |                      |                      |
 v                      v                      v
RAG / Guidance     Google Places         PostgreSQL
 |                      |                      |
 +----------------------+----------------------+
                        |
                        v
                 Ranking / Decision
                        |
                        v
                  Action Plan
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
     Guidance        Services        Actions
                                      |
                              Call / Navigate / SOS
```

---

# 10. Frontend Strategy

## React

Primary web interface for:

- Route planning
- Emergency setup
- Map
- Service results
- AI conversation
- Service details
- Emergency status
- Provider information
- Optional admin/verification interface

## Flutter

Mobile/offline emergency application for:

- GPS
- Local cached data
- Offline AI
- Offline RAG
- Emergency UI
- Call/SOS
- Route data
- Mobile-first voice interaction

React and Flutter should share the same FastAPI backend and product logic. They should not duplicate the entire application unnecessarily.

---

# 11. Backend

## FastAPI

Core backend responsibilities:

- Authentication verification
- Request validation
- AI orchestration
- RAG orchestration
- Google Places integration
- Service ranking
- Incident management
- User/route data
- Tool/action execution
- Security controls
- API layer for React, Flutter and Sarvam

---

# 12. Authentication

## Firebase Authentication

Firebase is used for authentication only.

```text
React / Flutter
      |
      v
Firebase Auth
      |
      v
Firebase ID Token
      |
      v
FastAPI
      |
      v
Token verification
      |
      v
PostgreSQL
```

Application data does not need to live in Firebase.

---

# 13. Database

## PostgreSQL

Planned application database.

Potential entities:

- users
- user_profiles
- routes
- incidents
- service_providers
- service_categories
- provider_verification
- regions
- emergency_contacts
- service_metadata
- action_logs
- minimal conversation/session metadata where required

Do not store unnecessary location history.

---

# 14. Google Maps / Places Strategy

## Decision

Use Google Maps Platform as the **primary online location and service-discovery infrastructure**.

Reasons:

- Existing access.
- Strong POI ecosystem.
- Familiar navigation UX.
- Faster hackathon implementation.
- No reason to reinvent mapping infrastructure.

Potential services:

### Places Nearby Search

Discover nearby candidates.

### Place Details

Fetch details only for selected/relevant candidates.

### Routes API

Calculate route distance/duration when required.

### Google Maps

Navigation handoff.

---

# 15. Google Maps vs RAAHAT

If a judge asks:

> “How do you compete with Google Maps?”

Answer:

> “We don't try to replace Google Maps. Google Maps has already solved mapping and navigation extremely well. We use that infrastructure and build an emergency intelligence layer on top of it. Google Maps can show what is nearby; RAAHAT understands the emergency, determines what type of help is needed, prioritizes relevant services, provides contextual guidance, and then uses Maps for navigation.”

---

# 16. Alternative Mapping Stack

Possible alternatives:

- OpenStreetMap + Overpass
- OSRM
- GraphHopper
- Valhalla

Current decision:

**Google is primary.**

OSM can later be considered as fallback/enrichment/offline source if needed.

---

# 17. Service Data Architecture

Different sources serve different purposes.

## Google Places

Dynamic online service discovery:

- nearby services
- place details
- locations
- navigation-related data

## PostgreSQL

Controlled structured application data:

- curated providers
- provider metadata
- verification
- regional emergency information
- saved routes
- incidents
- application state

## Device Local Database

Offline copy:

- cached route services
- emergency contacts
- cached service metadata
- offline knowledge indexes
- last-synchronized information

---

# 18. Do NOT Put Everything Into RAG

### RAG handles:

- emergency guidance
- first-aid knowledge
- roadside safety
- roadside procedures
- regional emergency guidance
- trusted textual knowledge

### Structured retrieval handles:

- emergency numbers
- coordinates
- service IDs
- service categories
- provider metadata

### Google Places handles:

- live/online service discovery
- nearby places
- place details

### RAG should NOT be the primary mechanism for:

- nearest hospital
- nearest mechanic
- live coordinates
- live service discovery
- navigation
- live provider availability

---

# 19. RAG Architecture Decision

Preferred architecture:

> **Hybrid + contextual + metadata-aware + reranked + routed RAG**

Not:

- pure vector RAG
- pure BM25
- GraphRAG-only
- unrestricted Agentic RAG

---

# 20. RAG Pipeline

```text
User Query
    |
    v
Query Understanding
    |
    +-- intent
    +-- emergency type
    +-- severity
    +-- region
    +-- language
    |
    v
Metadata Filtering
    |
    v
+----------------------+
|   Hybrid Retrieval   |
|                      |
| BM25 + Vector Search |
+----------+-----------+
           |
           v
      Top 30-50
           |
           v
      Reranker
           |
           v
       Top 5-10
           |
           v
Source / Authority Check
           |
           v
Grounded LLM Generation
           |
           v
Answer + Source Metadata
```

---

# 21. Why Hybrid Retrieval?

Vector retrieval handles semantic similarity.

BM25/lexical retrieval helps with:

- exact terms
- names
- emergency numbers
- acronyms
- domain-specific terminology

Using both improves retrieval robustness.

---

# 22. Contextual Retrieval

Chunks should preserve document/section context.

Avoid indexing isolated fragments that lose meaning.

Each chunk should retain context such as:

- document
- section
- topic
- region
- emergency type
- source
- verification date

---

# 23. Metadata Filtering

Example metadata:

```json
{
  "region": "India",
  "state": "Madhya Pradesh",
  "language": "en",
  "domain": "first_aid",
  "emergency_type": "bleeding",
  "severity": "critical",
  "source_authority": "official",
  "last_verified": "YYYY-MM-DD"
}
```

Filter by metadata before semantic retrieval where possible.

---

# 24. Reranking

Use:

```text
Hybrid retrieval
    ↓
Top 30-50
    ↓
Reranker
    ↓
Top 5-10
    ↓
LLM
```

The reranker is intended to improve precision before generation.

---

# 25. GraphRAG Decision

GraphRAG is NOT the primary RAG architecture.

Reason:

Most RAAHAT questions do not require global graph reasoning.

Complex relationships can often be represented using PostgreSQL.

GraphRAG can be revisited later only if a concrete requirement justifies it.

Do not use GraphRAG merely because it sounds advanced.

---

# 26. Agentic RAG Decision

A controlled agentic layer IS desired.

It should act as a router/orchestrator, not an unrestricted autonomous agent.

Example:

```text
User:
"Accident hua hai. Dost injured hai.
Nearest hospital batao aur kya karna chahiye?"

Router:
 |
 +--> RAG → emergency guidance
 |
 +--> Google Places → hospitals
 |
 +--> PostgreSQL → emergency numbers
 |
 v
Response synthesis
```

---

# 27. Grounded Generation

LLM responses must be grounded in retrieved evidence.

If evidence is insufficient:

- do not fabricate
- state uncertainty
- use an appropriate fallback

For safety-critical information, factual grounding is more important than conversational creativity.

---

# 28. RAG Source Strategy

Preferred hierarchy:

1. Official government/emergency/recognized medical sources.
2. Reputable institutional sources.
3. Other verified sources only where justified.

Store source metadata:

- source URL
- source authority
- region
- retrieval date
- verification date
- topic
- version

---

# 29. Offline Architecture

Major product concept:

> **Route-Aware Offline Emergency Intelligence**

---

# 30. Before the Journey

User enters a route:

```text
Indore → Bhopal
```

The app prepares an emergency data pack around the route.

Potential contents:

- emergency services
- hospitals
- police
- ambulances/providers
- mechanics
- puncture services
- towing
- emergency contacts
- emergency guidance
- relevant offline RAG data
- required route/map data

The route should be treated as an emergency corridor rather than caching only the starting-point radius.

---

# 31. When Network Disappears

GPS/GNSS can still provide current coordinates.

Offline flow:

```text
GPS
 ↓
Current coordinates
 ↓
Local spatial query
 ↓
Nearby cached candidates
 ↓
Deterministic decision/ranking
 ↓
Gemma
 ↓
Offline RAG
 ↓
Response
```

---

# 32. Critical Offline Separation

### GPS

Answers:

> Where am I?

### Local database

Answers:

> What cached services are within the selected radius?

### Decision engine

Answers:

> Which service types are relevant?

### Gemma

Answers:

> What does the user mean and how should the result be communicated?

### Offline RAG

Answers:

> What verified guidance applies?

Gemma should NOT perform raw geographic searching.

---

# 33. Offline Gemma

The app will provide an offline AI package.

Conceptually:

```text
RAAHAT Offline Pack
- Gemma model
- Offline RAG/index
- emergency guidance
- emergency contacts
- route/service cache
- required local data
```

The model is downloaded before travel.

Exact model/runtime is implementation work.

---

# 34. Offline Limitations

Offline mode can provide:

- GPS coordinates
- cached services
- cached emergency contacts
- cached guidance
- local AI
- local RAG

Offline mode cannot guarantee:

- live service availability
- fresh provider status
- live traffic
- new service discovery
- real-time external information

The UI should show the last synchronization time where relevant.

---

# 35. Agentic Action Layer

Major advanced feature under consideration:

> **RAAHAT can contact a roadside provider on the user's behalf after explicit permission.**

Example:

```text
User:
"My car broke down. Can you ask this mechanic
if they can come?"

RAAHAT:
"I found a mechanic 2.1 km away.
Would you like me to call them?"

[YES, CALL]

Agent
 ↓
Outbound call
 ↓
Mechanic
 ↓
AI explains:
- user situation
- location
- required service
 ↓
Mechanic responds
 ↓
AI understands response
 ↓
RAAHAT reports result
```

Possible confirmation:

- Can they come?
- Estimated arrival
- Service they can provide
- Approximate cost if provider states one

This is preferable to fabricating a static availability field.

---

# 36. User Permission

The agent must not autonomously call a provider without authorization.

Preferred flow:

```text
Find provider
 ↓
Explain recommendation
 ↓
Ask user permission
 ↓
YES
 ↓
Execute call
```

---

# 37. Tool / Action Architecture

The backend should eventually expose controlled tools such as:

```json
{
  "action": "call_provider",
  "provider_id": "provider_id",
  "reason": "confirm roadside assistance",
  "requires_user_confirmation": true
}
```

Other possible tools:

- navigate
- call emergency number
- send SOS
- share location
- retrieve nearby services

The LLM can request a tool, but the backend controls whether it executes.

---

# 38. Voice Architecture

Voice does not need to be rebuilt from scratch.

Already proven:

```text
Sarvam Voice Agent
      ↓
FastAPI POST endpoint
      ↓
Test response
      ↓
Sarvam
```

Final integration:

```text
Sarvam
 ↓
FastAPI
 ↓
Emergency Orchestrator
 ↓
RAG / Google Places / DB / Tools
 ↓
Response
 ↓
Sarvam
```

Once the final endpoint is ready, configure the Sarvam agent with the endpoint, headers/body/schema required by the integration.

---

# 39. Multilingual

Use Sarvam and i18n for:

- Indian-language voice
- multilingual interaction
- multilingual UI where required

RAG should preserve language and region metadata.

---

# 40. Service Prioritization

The service ranking engine is a core differentiator.

Do not simply return the closest place.

Conceptually:

```text
Suitability for incident
        +
Distance
        +
Verification / freshness
        +
Accessibility
        +
Other relevant factors
```

Example:

### Tyre puncture

1. Puncture repair
2. Mobile mechanic
3. Towing
4. General vehicle service

### Accident + injury

1. Ambulance
2. Emergency hospital
3. Police
4. Towing

Exact scoring formula remains to be finalized.

---

# 41. Service Verification / Reliability

Avoid unsupported claims such as:

> “This ambulance is definitely available right now.”

Services should carry metadata such as:

- source
- last verified
- verification status
- confidence/freshness

Potential statuses:

- Live/verified
- Recently verified
- Unknown

The team's separate availability idea still needs discussion.

---

# 42. Security & Privacy

Requirements:

- HTTPS everywhere.
- Firebase authentication.
- FastAPI verifies Firebase tokens.
- PostgreSQL access is user-scoped.
- API keys stay server-side.
- Never expose Google/Sarvam/Groq secrets to React/Flutter.
- Collect minimum necessary personal data.
- Do not permanently track location by default.
- Store location only when required for:
  - active assistance
  - saved route
  - incident
  - explicit user action
- Keep sensitive offline data on-device where possible.
- Explicit permissions for location and calling.

---

# 43. UX Philosophy

Users may be:

- stressed
- injured
- driving
- stranded
- in low light
- unfamiliar with the area

Therefore:

- Minimize typing.
- Prefer voice.
- Use large obvious actions.
- Avoid overwhelming lists.
- Prioritize relevant services.
- Put CALL / NAVIGATE / SOS prominently.
- Explain why a service was recommended.

Example:

```text
RECOMMENDED

🚑 ABC Ambulance
2.3 km

Why:
You reported a road accident with injury.

[CALL] [NAVIGATE]
```

---

# 44. Core Differentiation

## USP 1 — Situation-Aware Emergency Decision Engine

User describes what happened.

RAAHAT determines:

- incident type
- severity
- required service categories
- priority
- next steps

## USP 2 — Voice-First Multilingual Emergency Copilot

Natural voice interaction, including Indian languages.

## USP 3 — Route-Aware Offline Emergency Intelligence

Emergency data is prepared before travel and remains useful when connectivity disappears.

## USP 4 — Agentic Assistance

With explicit permission, RAAHAT can potentially contact providers and communicate the user's situation.

These are the primary high-value differentiators.

---

# 45. Features We Should NOT Build Unless Justified

Do not spend hackathon time on:

- Rebuilding Google Maps.
- Custom deep-learning models.
- Computer vision.
- IoT/hardware.
- Blockchain without a real requirement.
- Full GraphRAG without a concrete use case.
- Fake live ambulance availability.
- Unrestricted autonomous agents.
- Excessive dashboards.
- Features that do not improve the emergency workflow.

---

# 46. 24-Hour Priority Model

## P0 — Must Work

1. React interface.
2. Flutter core/mobile interface.
3. FastAPI.
4. Firebase authentication.
5. PostgreSQL.
6. GPS/location.
7. Google Places discovery.
8. Situation understanding.
9. Deterministic decision engine.
10. Service ranking.
11. Basic RAG.
12. Emergency guidance.
13. Contact/navigation.
14. Strong end-to-end demo scenario.

## P1 — High Value

1. Sarvam voice.
2. Multilingual interaction.
3. Offline cached services.
4. Offline emergency guidance.
5. Route-aware offline pack.

## P2 — Wow Factor

1. Offline Gemma.
2. Offline RAG.
3. Agentic provider calling.
4. Advanced verification.
5. Advanced regional support.

Priority can be adjusted after the first vertical slice works.

---

# 47. Development Strategy

Do NOT build every module independently and integrate at the end.

Build one complete vertical slice first.

Recommended first scenario:

> **Vehicle breakdown / tyre puncture**

Flow:

```text
User
 ↓
React/Flutter
 ↓
FastAPI
 ↓
Situation understanding
 ↓
Required service
 ↓
Google Places
 ↓
Ranking
 ↓
Service card
 ↓
Call / Navigate
```

Once this works end-to-end, add:

- RAG
- voice
- multilingual
- offline
- agentic actions

This minimizes integration risk.

---

# 48. Initial API Contract

Conceptual request:

```json
{
  "user_id": "...",
  "message": "My car broke down on the highway",
  "location": {
    "latitude": 22.7,
    "longitude": 75.8
  },
  "language": "en",
  "mode": "online"
}
```

Conceptual response:

```json
{
  "incident": {
    "type": "vehicle_breakdown",
    "severity": "medium"
  },
  "required_services": [
    "mechanic",
    "towing"
  ],
  "guidance": [],
  "services": [],
  "actions": []
}
```

Exact schema is implementation work.

---

# 49. Accuracy & Evaluation

Create a realistic evaluation set covering:

- accident
- bleeding
- unconscious person
- puncture
- breakdown
- fuel emergency
- stranded at night
- multilingual queries
- ambiguous queries

Evaluate:

- classification accuracy
- retrieval quality
- source correctness
- groundedness
- hallucination
- service relevance
- ranking quality

Do not assume more RAG components automatically mean better accuracy.

---

# 50. Architecture Principles

### Principle 1
Use existing infrastructure rather than reinventing it.

### Principle 2
Use deterministic systems for deterministic problems.

### Principle 3
Use LLMs for language and semantic interpretation.

### Principle 4
Use RAG for knowledge, not live geospatial facts.

### Principle 5
Never allow the LLM to fabricate safety-critical information.

### Principle 6
Offline mode must honestly expose stale-data limitations.

### Principle 7
Autonomous actions require explicit permission when appropriate.

### Principle 8
Build the simplest working vertical slice before adding advanced features.

---

# 51. Consolidated Architecture

```text
                         ┌─────────────────────┐
                         │        USER         │
                         └──────────┬──────────┘
                                    │
                  ┌─────────────────┼─────────────────┐
                  │                 │                 │
                  ▼                 ▼                 ▼
              React Web       Flutter Mobile    Sarvam Voice
                  │                 │                 │
                  └─────────────────┼─────────────────┘
                                    │
                                    ▼
                            ┌───────────────┐
                            │    FASTAPI    │
                            │ Core Backend  │
                            └───────┬───────┘
                                    │
                         ┌──────────┴──────────┐
                         │   AI ORCHESTRATOR  │
                         └──────────┬──────────┘
                                    │
        ┌───────────────┬───────────┼───────────────┬──────────────┐
        │               │           │               │              │
        ▼               ▼           ▼               ▼              ▼
      LLM             RAG       Google Places   PostgreSQL       TOOLS
        │               │           │               │              │
        │       ┌───────┴───────┐   │               │        ┌─────┼─────┐
        │       │ Hybrid        │   │               │        │     │     │
        │       │ BM25+Vector   │   │               │       Call  Nav   SOS
        │       │ + Reranking   │   │               │
        │       └───────────────┘   │               │
        │                           │               │
        └──────────────┬────────────┴───────────────┘
                       │
                       ▼
                DECISION ENGINE
                       │
                       ▼
                 SERVICE RANKING
                       │
                       ▼
                 ACTION PLAN
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Guidance     Services      Actions
```

Offline:

```text
                 FLUTTER
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Local DB   Gemma   Offline RAG
          │         │         │
          └─────────┼─────────┘
                    ▼
           Offline Decision Engine
                    │
                    ▼
               User Response
```

---

# 52. Open Decisions

These are deliberately NOT fully locked yet.

## A. Exact Google API implementation

Need to finalize:

- exact Places fields
- call strategy
- quotas
- caching
- route/navigation flow

## B. Exact service-ranking formula

Need to finalize:

- distance weight
- incident suitability
- verification
- accessibility
- other factors

## C. Availability strategy

Team has another idea that still needs discussion.

## D. Exact RAG implementation

Architecture is selected, but implementation details remain:

- embedding model
- vector database/index
- BM25 engine
- reranker
- chunking
- contextualization
- top-K
- multilingual retrieval
- offline index

## E. Offline implementation

Need to decide:

- exact Gemma model
- runtime
- local DB
- map caching
- local embeddings/index
- offline STT if required

## F. Agentic calling

Need to research:

- Exotel/Sarvam integration
- outbound call restrictions
- costs/trial credits
- caller identity
- disclosure
- call termination
- conversation handling

## G. Deployment

Handle later.

---

# 53. Immediate Build Plan

The team should now stop broad architectural research and begin implementation.

## Phase 1 — Foundation

1. Create Git repository.
2. Create React app.
3. Create Flutter app.
4. Create FastAPI project.
5. Configure PostgreSQL.
6. Configure Firebase Authentication.
7. Configure environment variables/secrets.
8. Define API contract.
9. Configure Google Maps/Places credentials.

## Phase 2 — First Vertical Slice

Build:

> **Puncture/breakdown scenario**

```text
User
 ↓
React/Flutter
 ↓
FastAPI
 ↓
Situation understanding
 ↓
Required service
 ↓
Google Places
 ↓
Ranking
 ↓
Service card
 ↓
Call / Navigate
```

## Phase 3

Add RAG.

## Phase 4

Connect Sarvam voice.

## Phase 5

Add offline architecture.

## Phase 6

Add agentic provider calling if time and infrastructure permit.

---

# 54. Definition of Done

A strong MVP should be able to demonstrate:

1. User reports a roadside problem in natural language or voice.
2. RAAHAT understands the situation.
3. RAAHAT determines severity.
4. RAAHAT identifies required service types.
5. Location is used to discover nearby candidates.
6. Appropriate services are prioritized.
7. Relevant emergency guidance is provided.
8. Contact/navigation actions are available.
9. The system explains why a service was recommended.
10. Cached emergency information remains usable when connectivity is lost.
11. The system does not fabricate unsupported facts.

Advanced demo:

> User explicitly authorizes RAAHAT to call a provider, and the agent communicates the situation on their behalf.

---

# 55. Final Product Statement

## RAAHAT

> **An AI-powered emergency decision and assistance platform that understands what happened to a road user, determines what help is needed, finds and prioritizes appropriate services using location intelligence, provides grounded emergency guidance, and remains useful during connectivity loss.**

Core principle:

> **Don't make the user figure out what to search for. Tell RAAHAT what happened.**
