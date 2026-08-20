# RAAHAT — Offline AI Architecture, On-Device RAG & Gemma Specification

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Team:** Solution Savvy  
**Primary owner:** Saanvi — Flutter/mobile integration; Satwik — AI/RAG/runtime  
**Purpose:** Define the offline AI subsystem: what works without internet, how route-aware data is packaged, how local retrieval works, how Gemma is used, how Flutter communicates with it, what must be researched, and how offline quality/performance will be measured.

> **Important:** Offline AI is not intended to reproduce the complete online RAAHAT system. It is a deliberately smaller, safety-oriented local system that remains useful when connectivity disappears.

---

# 1. Executive Decision

The offline architecture should be:

```text
                    FLUTTER APP
                         │
                 Network Detector
                         │
              ┌──────────┴──────────┐
              │                     │
           ONLINE                 OFFLINE
              │                     │
              ▼                     ▼
          FastAPI              Local Runtime
              │                     │
        Online RAG +             GPS
        Google APIs                 │
              │                 Local DB
              │                     │
              │             Local Retrieval
              │                     │
              │              Offline RAG
              │                     │
              │                  Gemma
              │                     │
              └──────────┬──────────┘
                         ▼
                  Unified Response
                         │
                         ▼
                      Flutter
```

The key principle is:

> **The user should experience one RAAHAT application, while the intelligence source changes transparently between cloud and device.**

---

# 2. What Offline AI Must Solve

The problem statement explicitly requires usefulness under low-network/offline conditions.

RAAHAT should remain useful for:

- accessing pre-downloaded emergency guidance
- understanding a user's basic roadside situation
- searching cached emergency knowledge
- finding cached emergency contacts
- finding cached roadside providers
- using GPS to determine current coordinates
- identifying relevant cached services near the current location
- providing concise safety guidance
- working without calling FastAPI
- working without calling Google APIs
- working without an internet LLM

It does **not** need to reproduce every online feature.

---

# 3. Online vs Offline Responsibility

| Capability | Online | Offline |
|---|---|---|
| GPS | Yes | Yes |
| Cached route | Yes | Yes |
| Google Places | Yes | No |
| Live provider discovery | Yes | No |
| PostgreSQL | Yes | No |
| Firebase authentication | Yes | Existing session only |
| Remote RAG | Yes | No |
| Local RAG | Optional | Yes |
| Remote LLM | Yes | No |
| Gemma | Optional | Yes |
| Emergency guidance | Yes | Yes |
| Cached emergency contacts | Yes | Yes |
| Cached providers | Yes | Yes |
| Navigation | Online mapping | Cached route information / limited local guidance |
| Agentic phone call | Online | No |
| Live provider availability | Online | No |
| Route-aware offline package | Downloaded online | Consumed offline |

---

# 4. Why We Should NOT Try to Make Everything Offline

Trying to reproduce:

```text
Google Places
+
Google Routes
+
remote RAG
+
full LLM
+
provider calling
```

offline would make the project unnecessarily large and fragile.

Instead:

```text
Offline = survival / continuity layer
Online = full RAAHAT intelligence
```

This is both technically defensible and much easier to demonstrate.

---

# 5. The Route-Aware Offline Concept

The strongest offline feature is the route-aware package.

Before a journey:

```text
User
 ↓
Enters origin + destination
 ↓
Online route calculation
 ↓
RAAHAT builds route corridor
 ↓
Collects relevant emergency/roadside data
 ↓
Builds offline package
 ↓
User downloads package
```

Later:

```text
Internet disappears
        ↓
GPS continues working
        ↓
Current coordinates obtained
        ↓
Compare against route corridor
        ↓
Search local cached services
        ↓
Retrieve local emergency guidance
        ↓
Gemma generates concise response
```

This is much stronger than simply caching “5 km around the current location” because the user can prepare the entire journey.

---

# 6. Route Corridor vs Single Radius

A simple approach:

```text
cache 5 km around current position
```

has a major weakness:

> The user may travel far away before connectivity disappears.

Instead:

```text
Origin
  ╲
   ╲
    ╲
     ╲─────────────── Destination
      route corridor
```

The offline package covers relevant segments along the planned route.

A configurable corridor width can be researched.

Example concept:

```text
Route
████████████████████████████
     cached service zones
```

Do not hard-code the final width until tested.

---

# 7. Offline Package

Conceptually:

```text
RAAHAT Offline Pack
│
├── manifest.json
│
├── route/
│   ├── route geometry
│   ├── route metadata
│   └── route segments
│
├── services/
│   ├── hospitals
│   ├── police
│   ├── ambulances
│   ├── mechanics
│   ├── puncture shops
│   ├── towing
│   └── vehicle service centers
│
├── emergency/
│   ├── emergency contacts
│   └── regional information
│
├── rag/
│   ├── documents
│   ├── chunks
│   ├── metadata
│   ├── vector index
│   └── lexical index
│
└── model/
    └── Gemma runtime/model
```

The actual serialization should be selected during implementation.

---

# 8. Manifest

Every offline package should have a manifest.

Example:

```json
{
  "pack_id": "route_001",
  "version": "1",
  "created_at": "...",
  "expires_at": "...",
  "origin": {},
  "destination": {},
  "route_hash": "...",
  "data_version": "...",
  "model_version": "...",
  "knowledge_version": "..."
}
```

The manifest lets the application know:

- what it downloaded
- when it was created
- which route it belongs to
- which data version it contains
- whether an update is available

---

# 9. Offline State Machine

The app should explicitly model connectivity.

```text
              ┌─────────────┐
              │    ONLINE   │
              └──────┬──────┘
                     │
              connection lost
                     ▼
              ┌─────────────┐
              │ OFFLINE     │
              └──────┬──────┘
                     │
              connection returns
                     ▼
              ┌─────────────┐
              │ SYNCING     │
              └──────┬──────┘
                     ▼
              ┌─────────────┐
              │    ONLINE   │
              └─────────────┘
```

The user should see the state clearly.

Example:

```text
🟢 Online
🟠 Limited connectivity
🔴 Offline
```

---

# 10. Offline Request Router

All AI requests should go through a single application-level interface.

Conceptually:

```text
AIService
   │
   ├── if online
   │      → FastAPI
   │
   └── if offline
          → LocalAIService
```

This avoids scattering online/offline logic throughout the Flutter application.

---

# 11. Unified AI Interface

Example conceptual API:

```text
assist(query, context)
```

Online implementation:

```text
Flutter
 ↓
FastAPI
 ↓
AI Orchestrator
 ↓
RAG + Tools + LLM
```

Offline implementation:

```text
Flutter
 ↓
LocalAIService
 ↓
Local Retrieval
 ↓
Gemma
```

Both return the same response schema.

---

# 12. Unified Response Schema

Example:

```json
{
  "mode": "offline",
  "answer": "...",
  "incident_type": "puncture",
  "severity": "medium",
  "services": [],
  "sources": [],
  "confidence": 0.82,
  "limitations": [
    "Provider data may be stale."
  ]
}
```

This lets the UI remain consistent.

---

# 13. Gemma's Role

Gemma is the **local language/reasoning layer**.

It should:

- understand the user's text
- summarize local retrieved evidence
- classify basic incident descriptions
- produce concise guidance
- handle conversational interaction
- generate natural-language output from local context

It should NOT be trusted as a standalone source of current emergency information.

The safe architecture is:

```text
User
 ↓
Local retrieval
 ↓
Trusted cached context
 ↓
Gemma
 ↓
Grounded response
```

Not:

```text
User
 ↓
Gemma's internal knowledge
 ↓
Emergency instruction
```

---

# 14. Current Gemma Options to Research

The model choice should remain a benchmark decision.

Google's current Gemma family includes small models designed for edge/mobile deployment; the current Gemma 4 family includes E2B and E4B variants aimed at ultra-mobile/edge scenarios. citeturn0search0turn0search2

Gemma 3n was also explicitly designed for phones, tablets and laptops and includes parameter-efficient techniques for reducing memory requirements. citeturn0search11

Therefore the research shortlist should include:

```text
Gemma 4 E2B
Gemma 4 E4B
Gemma 3n E2B
Gemma 3n E4B
```

The final selection must depend on:

- supported Android runtime
- RAM
- latency
- quality
- multilingual performance
- package size
- device used during judging

Do not lock the model solely because “2B” sounds appropriate.

---

# 15. Quantization

Mobile deployment generally requires a compressed/quantized model.

Google's current Gemma documentation provides mobile-optimized quantized checkpoints, including E2B/E4B variants, and describes model formats intended for mobile deployment. citeturn0search0

Quantization trades:

```text
model quality
     ↕
memory / compute
```

Research:

- 4-bit
- 8-bit
- model-specific mobile formats

Measure actual performance on the target Android device.

---

# 16. Mobile Runtime

The team should investigate Google's current AI Edge stack.

Google documents mobile Gemma deployment through AI Edge tooling and the MediaPipe LLM Inference API, with Android and iOS support. citeturn0search5

Research:

```text
Gemma
 ↓
mobile-optimized format
 ↓
AI Edge / MediaPipe / supported runtime
 ↓
Android device
```

Do not assume that a desktop GGUF setup is automatically the best Flutter/Android deployment path.

---

# 17. Alternative Local Runtime

For desktop development/testing, llama.cpp/Ollama can be useful.

Google documents running quantized Gemma through Ollama/llama.cpp with lower compute requirements, including CPU-only laptop operation. citeturn0search4

But:

> Ollama should not automatically become the production mobile runtime.

Use it as a development/benchmark tool unless the Android integration is proven suitable.

---

# 18. Local Embeddings

Offline RAG requires local retrieval.

A promising candidate is **EmbeddingGemma**, which Google describes as a lightweight embedding model designed for retrieval on everyday devices and lists at 308M parameters. citeturn0search1

Research:

```text
EmbeddingGemma
vs
smaller multilingual embedding alternatives
```

Measure:

- English retrieval
- Hindi retrieval
- Hinglish retrieval
- memory
- latency
- model size
- Android compatibility

---

# 19. Local RAG Architecture

```text
                     USER
                       │
                       ▼
                  Flutter App
                       │
                       ▼
                  Local AI Service
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
        Query Parser         GPS Context
             │                   │
             └─────────┬─────────┘
                       ▼
                 Local Metadata
                     Filter
                       │
              ┌────────┴────────┐
              ▼                 ▼
          Local BM25       Local Vector
              │                 │
              └────────┬────────┘
                       ▼
                    Fusion
                       ▼
                   Rerank
                       ▼
                  Top Context
                       ▼
                     Gemma
                       ▼
                Grounded Answer
```

---

# 20. Do We Need the Full Online RAG Offline?

No.

Offline RAG should be smaller.

Online:

```text
large knowledge base
+
full retrieval
+
full metadata
+
remote reranker
+
remote LLM
```

Offline:

```text
route-specific knowledge
+
critical emergency knowledge
+
cached local providers
+
small retrieval index
+
Gemma
```

This reduces:

- storage
- RAM
- latency
- complexity

---

# 21. Offline Knowledge Selection

The package should prioritize:

## Highest priority

- emergency procedures
- severe bleeding guidance
- accident safety
- vehicle fire
- breakdown safety
- puncture safety
- emergency contacts

## Medium priority

- towing guidance
- mechanic-related guidance
- highway-specific safety

## Lower priority

- general educational information

The offline package is a **safety pack**, not a mirror of the internet.

---

# 22. Local Service Data

When preparing a route:

```text
Google Places
 ↓
discover relevant services
 ↓
normalize
 ↓
store selected fields locally
```

Possible fields:

```json
{
  "place_id": "...",
  "name": "...",
  "category": "hospital",
  "latitude": 0,
  "longitude": 0,
  "phone": "...",
  "address": "...",
  "hours": "...",
  "retrieved_at": "..."
}
```

The offline UI must clearly indicate that this data may become stale.

---

# 23. Offline Service Ranking

Current location:

```text
GPS = (lat, lng)
```

Cached services:

```text
Hospital A
Hospital B
Hospital C
```

Local ranking can use deterministic logic:

```text
distance
+
service category
+
emergency relevance
+
cached metadata quality
```

Do not ask Gemma to calculate distances or invent provider rankings.

---

# 24. GPS + Offline AI

GPS can continue supplying coordinates without internet.

Flow:

```text
GPS
 ↓
current coordinates
 ↓
route corridor check
 ↓
local service query
 ↓
nearest relevant services
```

Gemma can explain the result:

```text
"There is a cached hospital approximately
X km from your current position."
```

The distance should come from deterministic geospatial calculation, not LLM estimation.

---

# 25. Geospatial Search

Research local implementation options.

Candidate:

```text
Haversine distance
```

For larger datasets:

```text
R-tree / spatial index / geohash
```

The final method should be selected based on package size and mobile performance.

---

# 26. Offline Decision Engine

Some decisions should remain deterministic.

Example:

```text
incident = vehicle_fire
        ↓
severity = critical
        ↓
recommended action = evacuate + emergency escalation
```

Gemma should explain the result.

It should not be responsible for inventing the decision rules.

Architecture:

```text
Incident classifier
       ↓
Deterministic safety rules
       ↓
Retrieved evidence
       ↓
Gemma explanation
```

---

# 27. Offline Emergency Flow

Example:

> “Accident hua hai aur mere friend ko bleeding ho rahi hai.”

Flow:

```text
Voice/Text
   ↓
Local parser
   ↓
Incident = accident
   ↓
Emergency = bleeding
   ↓
Severity = critical
   ↓
Local RAG
   ↓
Relevant cached guidance
   ↓
Gemma
   ↓
Concise response
   ↓
Flutter emergency UI
```

---

# 28. Offline Puncture Flow

```text
User:
"Tyre puncture ho gaya."
        ↓
Local classification
        ↓
puncture
        ↓
Local service index
        ↓
nearby cached puncture shops
        ↓
Local RAG
        ↓
safe roadside guidance
        ↓
Gemma
        ↓
Flutter
```

---

# 29. Offline Multi-Intent Flow

Example:

> “Accident hua hai, bleeding ho rahi hai aur hospital chahiye.”

The local orchestrator should recognize:

```text
Intent 1 = emergency guidance
Intent 2 = service discovery
```

Then:

```text
RAG → guidance
Local service DB → hospitals
GPS → distance
Gemma → response composition
```

---

# 30. Offline Voice

Voice is optional for the first offline MVP.

Potential future architecture:

```text
Offline speech input
       ↓
local speech-to-text
       ↓
offline orchestrator
       ↓
local RAG + Gemma
       ↓
offline text-to-speech
```

However, do not make offline voice a dependency for the hackathon core.

The online Sarvam voice system remains the primary voice experience.

---

# 31. Offline Voice Research

If time permits, research:

- Android speech recognition availability
- offline speech recognition
- Whisper-family small models
- Vosk
- platform-native offline speech APIs
- offline TTS

Measure:

- package size
- Hindi performance
- latency
- RAM
- battery

---

# 32. Offline Agentic Calling

This should be treated as **unsupported offline** unless a phone call can be initiated through native telephony.

The full agentic mechanic-calling workflow requires:

```text
network
+
provider communication
+
voice infrastructure
```

Therefore:

```text
Offline:
Show cached provider + phone number
→ user can call manually if cellular service works

Online:
AI agent can handle provider interaction
```

This distinction must be explicit.

---

# 33. Offline Authentication

Firebase authentication is primarily online.

The app should support an existing authenticated session as appropriate, but the offline AI should not depend on making a fresh authentication request before every operation.

Research:

- Firebase auth persistence
- token expiration behavior
- offline session handling

Do not weaken security merely to make offline mode convenient.

---

# 34. Local Database

The Flutter app needs local storage for:

- offline package manifest
- route
- providers
- emergency contacts
- RAG chunks
- indexes
- settings
- cached timestamps

Possible technologies should be benchmarked.

Candidates:

- SQLite
- Drift
- Isar
- Hive

The choice should prioritize:

- Flutter support
- reliability
- indexing
- binary storage
- querying
- offline performance

---

# 35. Local Storage Separation

Do not store everything in one giant table.

Conceptual structure:

```text
OfflinePack
   │
   ├── Route
   ├── Service
   ├── EmergencyContact
   ├── Document
   ├── Chunk
   └── Metadata
```

---

# 36. Package Integrity

Before installing an offline pack:

```text
download
 ↓
verify manifest
 ↓
verify package integrity
 ↓
install atomically
 ↓
activate
```

If installation fails:

```text
keep previous valid pack
```

Never leave the application with a partially installed knowledge base.

---

# 37. Package Updates

When online:

```text
Check version
 ↓
new package available?
 ↓
download
 ↓
verify
 ↓
replace old version
```

Use atomic replacement.

---

# 38. Staleness

Every cached service should have:

```text
retrieved_at
```

Every knowledge document should have:

```text
verified_at
```

UI should indicate:

```text
Cached
Updated 2 hours ago
```

or:

```text
Cached data may be outdated.
```

Never present stale provider data as live availability.

---

# 39. Offline Data Expiry

Do not blindly delete expired data.

A safer policy:

```text
Fresh
 ↓
Stale
 ↓
Very stale
```

The data may still be useful as a fallback, but its status must be visible.

Emergency guidance and provider data should have different freshness policies.

---

# 40. Security

Offline package can contain:

- service locations
- phone numbers
- route information
- emergency knowledge

Protect against casual tampering.

Research:

- encrypted local storage
- package integrity
- secure key storage
- Android Keystore
- secure deletion

Avoid storing unnecessary personal data.

---

# 41. Privacy

Offline mode can actually improve privacy because:

```text
GPS
 ↓
local processing
 ↓
local answer
```

does not require sending every query to a remote server.

This can be a strong judge-facing privacy advantage.

Do not claim “zero data leaves the device” unless the implementation truly guarantees it.

---

# 42. Model Privacy

A downloaded local model:

```text
Gemma weights
+
local retrieval
```

can operate without sending the user's query to a remote LLM.

Google describes EmbeddingGemma as suitable for local retrieval and RAG without internet connectivity. citeturn0search1

---

# 43. Device Requirements Research

The team must test on the **actual phone used for the final demo**.

Record:

```text
Device model
Android version
RAM
Storage
CPU
GPU/NPU if exposed
battery
```

Then measure:

```text
model load time
first-token latency
tokens/sec
peak RAM
storage
battery
retrieval latency
total response latency
```

Do not rely only on laptop benchmarks.

---

# 44. Model Benchmark

Compare at least two candidate models if feasible.

Example:

| Model | Size | Load Time | RAM | Tokens/sec | Quality | Hindi | Offline |
|---|---:|---:|---:|---:|---:|---:|---|
| Gemma candidate A | — | — | — | — | — | — | ✓ |
| Gemma candidate B | — | — | — | — | — | — | ✓ |

Use actual measurements.

---

# 45. Local RAG Benchmark

Compare:

```text
No RAG + Gemma
vs
Local Vector RAG + Gemma
vs
Local Hybrid RAG + Gemma
```

This is especially important.

If Gemma alone produces a plausible answer but local RAG improves grounding, that becomes a powerful demonstration.

---

# 46. Offline Metrics

Use both quality and systems metrics.

## Retrieval

- Recall@K
- Precision@K
- MRR
- nDCG

## Generation

- Faithfulness
- Answer Relevancy
- Factual Correctness
- Safety Pass Rate

## Mobile

- model load time
- first-token latency
- tokens/sec
- P50/P95 response latency
- peak RAM
- package size
- battery impact

---

# 47. Offline Quality Degradation

Compare online vs offline:

```text
Online RAG
      vs
Offline RAG
```

Measure:

```text
retrieval quality
answer quality
safety
latency
```

The goal is not identical performance.

The goal is:

> **Useful and safe performance under connectivity loss.**

---

# 48. Offline Golden Dataset

Create a smaller offline test set:

```text
50–100 queries
```

Prioritize:

- accident
- bleeding
- puncture
- breakdown
- vehicle fire
- stranded roadside
- emergency contacts
- Hindi/Hinglish

Each query should have:

```text
expected intent
expected evidence
expected answer points
safety requirement
```

---

# 49. Offline Safety Tests

Explicitly test:

### Test A
No relevant local evidence.

Expected:

```text
safe fallback
```

### Test B
Conflicting local evidence.

Expected:

```text
uncertainty / conservative response
```

### Test C
Stale provider.

Expected:

```text
show stale status
```

### Test D
Wrong route.

Expected:

```text
do not falsely claim provider is nearby
```

### Test E
GPS unavailable.

Expected:

```text
tell user location is unavailable
```

### Test F
No offline pack.

Expected:

```text
graceful limited mode
```

---

# 50. Offline Failure Matrix

| Failure | Expected behavior |
|---|---|
| No internet | Switch local |
| No offline pack | Show limited emergency mode |
| No GPS | Ask for location / show limitation |
| Stale service | Mark stale |
| Local RAG miss | Safe fallback |
| Gemma unavailable | Show cached guidance |
| Model load failure | Use deterministic cached responses |
| Corrupt package | Revert to previous pack |
| Low storage | Refuse package / warn |
| Low battery | Optional low-power mode |

---

# 51. Graceful Degradation

This is critical.

Offline AI should have multiple fallback levels:

```text
Level 1
Gemma + Local RAG

       ↓ failure

Level 2
Local RAG + deterministic templates

       ↓ failure

Level 3
Cached emergency instructions

       ↓ failure

Level 4
Emergency contact information
```

The user should never be left with a blank screen.

---

# 52. Deterministic Emergency Fallbacks

For the most critical situations, maintain structured emergency templates.

Example:

```text
incident_type = severe_bleeding
```

may map to a reviewed set of emergency guidance.

The exact medical wording should come only from the team's verified sources.

This gives:

```text
LLM failure
→ still useful
```

---

# 53. Why Deterministic Fallback Matters

An offline model can:

- fail to load
- run slowly
- produce poor output
- misunderstand a query

Emergency guidance should not depend entirely on successful generation.

Architecture:

```text
Trusted emergency rule
        +
retrieved context
        +
Gemma explanation
```

not:

```text
Gemma decides everything
```

---

# 54. Offline Orchestrator

Conceptually:

```text
OfflineOrchestrator
│
├── NetworkState
├── GPSService
├── IncidentClassifier
├── SafetyRules
├── LocalServiceSearch
├── LocalRAG
├── GemmaRuntime
├── FallbackManager
└── ResponseFormatter
```

This should be a clean internal module rather than scattered functions.

---

# 55. Suggested Flutter Structure

Conceptual structure:

```text
lib/
├── core/
│   ├── network/
│   ├── location/
│   └── storage/
│
├── offline/
│   ├── offline_service.dart
│   ├── offline_orchestrator.dart
│   ├── package_manager.dart
│   ├── local_rag.dart
│   ├── gemma_service.dart
│   ├── fallback_manager.dart
│   └── local_service_search.dart
│
├── online/
│   └── api_service.dart
│
└── features/
    └── emergency/
```

This is an architectural suggestion, not a mandatory directory structure.

---

# 56. Backend Responsibilities for Offline

FastAPI does not run during actual offline operation.

But it prepares the offline package.

Possible endpoint:

```text
POST /offline-pack/create
```

Input:

```json
{
  "origin": {},
  "destination": {},
  "preferences": {
    "include_hospitals": true,
    "include_police": true,
    "include_ambulance": true,
    "include_mechanics": true,
    "include_puncture": true,
    "include_towing": true
  }
}
```

Output:

```text
offline package
```

---

# 57. Offline Pack Creation Flow

```text
User plans journey
        ↓
FastAPI
        ↓
Google Routes
        ↓
route corridor
        ↓
Google Places
        ↓
service collection
        ↓
knowledge selection
        ↓
RAG subset creation
        ↓
package generation
        ↓
Flutter downloads
        ↓
local verification
        ↓
package activated
```

---

# 58. What Should Be Cached From Google

Only cache what the application needs.

For each service:

- name
- category
- coordinates
- address
- phone if available
- relevant metadata
- retrieval timestamp
- source/provider ID if needed

Do not unnecessarily cache large provider payloads.

---

# 59. What Should NOT Be Cached

Avoid:

- unnecessary personal data
- complete Google responses
- irrelevant places
- massive map imagery
- unrelated documents
- entire internet pages

Keep the package focused.

---

# 60. Offline Package Size Budget

The team should define a practical target after benchmarking.

Track:

```text
model size
+
embedding model
+
vector index
+
BM25 index
+
provider data
+
route data
+
emergency knowledge
```

The package must be reasonable for a student's phone.

Do not choose a model first and discover later that the offline package is hundreds of MB or more than the target device can comfortably handle.

---

# 61. Important Model Decision

The team's original plan mentioned a small “2B” Gemma model.

That is a **starting hypothesis**, not the final technical decision.

As of 2026, Google offers newer small Gemma variants specifically targeting edge/mobile deployment, including Gemma 4 E2B/E4B, while Gemma 3n remains a relevant mobile-focused option. citeturn0search0turn0search11

Therefore:

> **Benchmark the current mobile-oriented Gemma candidates on the actual Android device before locking the model.**

---

# 62. Important Embedding Decision

The offline RAG needs an embedding model.

A particularly relevant current candidate is EmbeddingGemma, which Google describes as a lightweight model designed for local retrieval and lists at 308M parameters. citeturn0search1

But again:

> **Benchmark it against smaller/multilingual alternatives on the team's actual emergency query set.**

---

# 63. Research Checklist — Model

- [ ] Gemma 4 E2B tested
- [ ] Gemma 4 E4B considered
- [ ] Gemma 3n E2B considered
- [ ] Gemma 3n E4B considered
- [ ] Quantization variants compared
- [ ] Actual Android device tested
- [ ] RAM measured
- [ ] load time measured
- [ ] tokens/sec measured
- [ ] Hindi quality measured
- [ ] English quality measured
- [ ] Hinglish quality measured
- [ ] package size measured

---

# 64. Research Checklist — Runtime

- [ ] AI Edge / MediaPipe LLM runtime investigated
- [ ] Android compatibility confirmed
- [ ] model format confirmed
- [ ] CPU path tested
- [ ] GPU acceleration investigated
- [ ] supported hardware acceleration verified
- [ ] fallback behavior understood

Google's mobile documentation specifically describes MediaPipe LLM Inference API as a way to run Gemma on Android/iOS. citeturn0search5

---

# 65. Research Checklist — Local RAG

- [ ] Embedding model selected
- [ ] Vector index selected
- [ ] BM25 selected
- [ ] Fusion strategy selected
- [ ] Local metadata filtering implemented
- [ ] Top-K benchmarked
- [ ] Chunk size benchmarked
- [ ] multilingual retrieval tested
- [ ] storage measured
- [ ] retrieval latency measured

---

# 66. Research Checklist — Offline Package

- [ ] Manifest
- [ ] Versioning
- [ ] Integrity verification
- [ ] Atomic installation
- [ ] Route storage
- [ ] Provider storage
- [ ] Emergency contacts
- [ ] RAG data
- [ ] Model
- [ ] Update mechanism
- [ ] Stale-data policy
- [ ] Delete/replace behavior

---

# 67. Research Checklist — UX

- [ ] Online indicator
- [ ] Offline indicator
- [ ] Offline pack download
- [ ] Download progress
- [ ] Package size display
- [ ] Last updated display
- [ ] Stale provider warning
- [ ] GPS unavailable state
- [ ] No-pack state
- [ ] Model loading state
- [ ] Offline fallback state

---

# 68. Research Checklist — Safety

- [ ] No-answer fallback
- [ ] deterministic emergency templates
- [ ] safety rules
- [ ] source verification
- [ ] stale-data warning
- [ ] no invented provider availability
- [ ] no invented emergency numbers
- [ ] no unsupported medical claims
- [ ] uncertainty handling
- [ ] model failure fallback

---

# 69. Offline Evaluation Matrix

| Test | Online | Offline | Expected |
|---|---|---|---|
| Accident guidance | ✓ | ✓ | Useful |
| Severe bleeding | ✓ | ✓ | Safe |
| Puncture guidance | ✓ | ✓ | Useful |
| Nearby cached service | ✓ | ✓ | Correct |
| Live Google Places | ✓ | ✗ | Explicit limitation |
| Emergency contacts | ✓ | ✓ | Available |
| GPS | ✓ | ✓ | Available |
| Agentic provider call | ✓ | Limited | Graceful fallback |
| RAG | ✓ | ✓ | Grounded |
| Gemma | Optional | ✓ | Local response |

---

# 70. Recommended Offline MVP

Do NOT attempt every offline feature first.

Build this first:

```text
Flutter
 ↓
Network detection
 ↓
Offline package
 ↓
GPS
 ↓
Local provider search
 ↓
Local emergency knowledge
 ↓
Gemma
 ↓
Grounded response
```

That is enough to demonstrate the core offline USP.

---

# 71. Recommended Development Sequence

## Phase 1 — Prove Gemma locally

```text
Gemma
 ↓
Android
 ↓
simple prompt
 ↓
response
```

No RAG yet.

## Phase 2 — Local retrieval

```text
documents
 ↓
embeddings
 ↓
local search
```

## Phase 3 — Gemma + RAG

```text
query
 ↓
retrieve
 ↓
Gemma
```

## Phase 4 — Offline provider data

```text
cached services
 ↓
GPS
 ↓
local ranking
```

## Phase 5 — Route pack

```text
route
 ↓
services
 ↓
RAG subset
 ↓
download
```

## Phase 6 — Unified online/offline router

```text
online → FastAPI
offline → Local AI
```

## Phase 7 — Failure handling

```text
Gemma fails
 ↓
RAG/template fallback
```

## Phase 8 — Polish

Only now optimize UX and performance.

---

# 72. Golden Demo Flow

The strongest live demonstration:

```text
1. Open RAAHAT
        ↓
2. Plan a route
        ↓
3. "Prepare Offline Safety Pack"
        ↓
4. Download completes
        ↓
5. Show cached emergency/provider data
        ↓
6. Disable internet
        ↓
7. GPS remains active
        ↓
8. User says:
   "Highway par tyre puncture ho gaya"
        ↓
9. Local incident understanding
        ↓
10. Local service search
        ↓
11. Local RAG retrieves safety guidance
        ↓
12. Gemma generates response
        ↓
13. Nearby cached puncture/mechanic
        ↓
14. User sees:
   guidance + services + offline indicator
```

This is a much stronger demonstration than merely saying:

> “We downloaded Gemma.”

---

# 73. Judge-Facing Explanation

### “How does RAAHAT work without internet?”

> “Before a journey, RAAHAT can prepare a route-aware offline safety package containing critical emergency knowledge, emergency contacts and relevant roadside services along the planned route. If connectivity disappears, the phone's GPS still provides the current coordinates. RAAHAT searches the locally stored data, retrieves relevant emergency guidance and uses a quantized Gemma model on-device to produce a grounded response.”

### “Isn't Gemma just hallucinating?”

> “We don't use Gemma as the knowledge source. The local system first retrieves verified cached evidence. Gemma is used to interpret and communicate that evidence. For critical cases we also maintain deterministic fallback guidance.”

### “What if Gemma fails?”

> “The system degrades gracefully. It can fall back to cached RAG results or reviewed emergency templates rather than becoming unusable.”

### “Can it find a new mechanic offline?”

> “No live discovery is possible without connectivity. Instead, RAAHAT uses the route-aware service data downloaded before the journey and clearly marks it as cached data. Once connectivity returns, the service data can be refreshed.”

---

# 74. What Makes This Different From "Just Downloading Gemma"

The USP is the **system**, not the model.

```text
Route planning
      +
Route-aware caching
      +
Local geospatial search
      +
Local emergency knowledge
      +
Offline RAG
      +
Gemma
      +
Deterministic safety rules
      +
Graceful degradation
```

Gemma is only one component.

---

# 75. Final Offline Architecture

```text
                         USER
                           │
                           ▼
                    FLUTTER APP
                           │
                   Network Detector
                           │
              ┌────────────┴────────────┐
              │                         │
            ONLINE                   OFFLINE
              │                         │
              ▼                         ▼
          FastAPI                Offline Orchestrator
              │                         │
        ┌─────┴─────┐             ┌────┴─────┐
        │           │             │          │
      Remote       Google        GPS      Local DB
       RAG         APIs           │          │
        │           │             │     ┌────┴────┐
        │           │             │     │         │
        │           │             │   Services   RAG
        │           │             │               │
        │           │             │          Local Retrieval
        │           │             │               │
        │           │             │             Gemma
        │           │             │               │
        └─────┬─────┘             └───────┬───────┘
              │                           │
              └─────────────┬─────────────┘
                            ▼
                    Unified Response
                            │
                            ▼
                         FLUTTER
```

---

# 76. Final Engineering Principles

1. **Offline is a fallback/continuity architecture, not a duplicate cloud architecture.**
2. **Gemma is a generation/reasoning layer, not the source of truth.**
3. **Local RAG supplies evidence.**
4. **Deterministic rules handle safety-critical decisions.**
5. **GPS handles location.**
6. **Local service search handles cached providers.**
7. **The route-aware package is the key differentiator.**
8. **Every cached item has freshness metadata.**
9. **The system degrades gracefully.**
10. **Benchmark the actual device before locking the model.**
11. **Do not add offline voice unless the core offline AI is already reliable.**
12. **Do not claim live service availability while offline.**
13. **Do not claim zero network use unless the complete execution path has been verified.**
14. **Prefer a small, trusted offline knowledge base over a huge noisy one.**

---

# 77. Final Architecture in One Sentence

> **RAAHAT prepares a route-aware local safety package while online, then uses GPS, cached services, local retrieval and a quantized Gemma model to provide grounded roadside assistance when connectivity disappears, with deterministic emergency fallbacks when local AI is unavailable.**
