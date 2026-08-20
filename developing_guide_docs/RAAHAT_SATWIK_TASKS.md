# RAAHAT — Satwik Task & Execution Plan

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Team:** Solution Savvy  
**Team Member:** Satwik Misra  
**Primary Domains:** AI/RAG + AI Orchestration + FastAPI AI Integration + Offline AI + Sarvam Voice + PostgreSQL + Firebase + Agentic AI

---

# 1. Purpose

This is Satwik's personal execution guide for building the intelligence layer of RAAHAT.

It is intended to be provided to Satwik's AI coding/research assistant together with all common project documents:

- RAAHAT PRD
- Complete feature/functionality document
- System architecture document
- RAG architecture document
- Offline AI architecture document
- API Contracts & Integration Guide

Those documents explain the complete project.

This document explains:

- what Satwik owns
- what he must build
- what he must research
- what he must deliver to Santosh and Saanvi
- what dependencies he has on them
- how to avoid being blocked by their work
- how his phases synchronize with the rest of the team
- what should be prioritized during the 24-hour hackathon

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
- PostgreSQL
- Firebase
- agentic AI
- AI evaluation

### Santosh Ray

Primary areas:

- React
- FastAPI core backend
- APIs
- Google Maps / Places / Routes
- alternative API research
- frontend/backend integration
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

# 3. Satwik's Core Mission

Satwik owns the **intelligence layer** of RAAHAT.

The target architecture is:

```text
User
 ↓
React / Flutter / Voice
 ↓
FastAPI
 ↓
Emergency AI Orchestrator
 ├── Incident Understanding
 ├── RAG
 ├── LLM
 ├── Service Intelligence
 ├── Safety Logic
 ├── Voice
 └── Agentic Actions
 ↓
Structured Response
```

For offline mobile operation:

```text
Flutter
 ↓
Offline Orchestrator
 ↓
Local Retrieval
 ↓
Gemma
 ↓
Grounded Response
```

The central principle is:

> **The model should not be treated as the source of truth. Retrieved, verified knowledge is the source of truth; the model interprets and communicates it.**

---

# 4. What Satwik Does NOT Own Alone

Satwik should not independently take over:

- React UI
- Flutter UI
- Google Maps frontend
- Google Places provider implementation
- core deployment work
- overall API contract ownership
- mobile UI architecture

These belong primarily to Santosh/Saanvi.

However, Satwik must integrate his AI layer with their APIs and clients.

---

# 5. Phase Overview

```text
PHASE 0
Architecture + AI plan + environment
        ↓
PHASE 1
RAG architecture + AI foundations + schemas + research-independent work
        ↓
PHASE 2
RAG ingestion + evaluation + AI orchestration
        ↓
PHASE 3
Offline AI + Sarvam voice + advanced intelligence
        ↓
PHASE 4
Agentic AI + full-system integration
        ↓
PHASE 5
Testing + optimization + demo + deployment support
```

The phases are deliberately synchronized with:

```text
Saanvi:
research → knowledge handoff → Flutter/offline

Santosh:
API/backend → external providers → integration/deployment

Satwik:
AI foundation → RAG → orchestration → offline AI → advanced features
```

---

# 6. Dependency Philosophy

The biggest danger is:

```text
Saanvi researches
      ↓
Satwik waits
```

This must NOT happen.

Instead:

```text
SAANVI PHASE 1
Research + knowledge collection
        │
        ▼
SATWIK PHASE 1
RAG architecture + ingestion skeleton
        │
        ▼
SATWIK PHASE 2
Real knowledge ingestion
```

Likewise:

```text
SANTOSH PHASE 1
API contracts + mock backend
        │
        ▼
SATWIK PHASE 2/3
AI integration
```

Satwik must always have an independent AI task available.

---

# PHASE 0 — COMPLETE AI/ARCHITECTURE UNDERSTANDING

## Goal

Before coding, ensure the AI assistant understands the entire RAAHAT architecture.

---

# 7. Read the Common Documents

The AI assistant must receive:

1. PRD
2. complete feature/functionality document
3. architecture document
4. RAG architecture document
5. offline AI architecture document
6. API Contracts & Integration Guide
7. this Satwik task document

It must understand:

```text
Problem
 ↓
Emergency assistance
 ↓
Online AI
 ↓
RAG
 ↓
Google service results
 ↓
Decision/orchestration
 ↓
Voice
 ↓
Offline AI
 ↓
Agentic actions
```

---

# 8. Freeze the AI Boundary

The primary public endpoint is:

```text
POST /api/v1/emergency-assistance
```

Satwik's AI layer should plug into this endpoint.

The client should NOT need to know:

```text
which LLM
which vector database
which reranker
which embedding model
which retrieval algorithm
```

The AI subsystem remains behind the FastAPI contract.

---

# 9. AI Environment Setup

Set up:

- Python
- FastAPI
- LLM SDKs
- Groq
- Sarvam
- RAG dependencies
- embedding model
- vector store
- reranking dependencies if selected
- PostgreSQL
- testing tools

Potential tools:

```text
FastAPI
Pydantic
Groq
Sarvam
sentence-transformers / compatible embedding runtime
pgvector if used
PostgreSQL
```

Exact libraries depend on the final RAG architecture and benchmarking.

---

# 10. AI Configuration

Never hard-code:

```text
API keys
model names
provider URLs
database credentials
```

Use environment variables.

Potential configuration:

```text
GROQ_API_KEY
SARVAM_API_KEY
DATABASE_URL
LLM_MODEL
EMBEDDING_MODEL
RERANKER_MODEL
```

---

# PHASE 1 — AI FOUNDATIONS + RAG ARCHITECTURE

## Goal

While Saanvi researches the knowledge, Satwik prepares everything necessary to ingest it immediately when it arrives.

---

# 11. Finalize RAG Architecture

The target is not:

```text
"simple vector search + LLM"
```

The goal is high retrieval accuracy.

The architecture should be evaluated around:

```text
Query
 ↓
Query understanding
 ↓
Hybrid retrieval
 ├── semantic/vector
 ├── lexical/BM25
 └── metadata/filter retrieval
 ↓
Candidate fusion
 ↓
Reranking
 ↓
Context filtering
 ↓
Grounded generation
 ↓
Citation/source mapping
 ↓
Safety validation
 ↓
Response
```

---

# 12. RAG Strategy

The preferred initial architecture should be:

```text
Hybrid RAG
+
Reranking
+
Metadata filtering
+
Query rewriting where useful
+
Grounded generation
```

More complex techniques should only be added when they improve measurable accuracy.

Possible future components:

```text
Graph RAG
Agentic retrieval
Multi-query retrieval
Hierarchical retrieval
```

Do not add complexity merely to say that the system uses advanced RAG.

---

# 13. Vectorless Retrieval

Research/implement lexical retrieval where useful.

Potential:

```text
BM25
```

Purpose:

- exact emergency terminology
- names
- Hindi/Hinglish phrases
- service names
- important keywords

---

# 14. Vector Retrieval

Implement semantic retrieval.

Potential pipeline:

```text
document
 ↓
chunk
 ↓
embedding
 ↓
vector index
```

At query time:

```text
query
 ↓
embedding
 ↓
similarity search
```

---

# 15. Hybrid Retrieval

Combine:

```text
BM25 score
+
vector similarity
```

through a fusion mechanism.

Potential:

```text
Reciprocal Rank Fusion
```

or another measured ranking method.

The exact method should be benchmarked.

---

# 16. Reranking

Evaluate a reranker after candidate retrieval.

Pipeline:

```text
Top 20 candidates
 ↓
reranker
 ↓
Top 5 contexts
 ↓
LLM
```

The goal is to reduce irrelevant context.

---

# 17. Metadata Filtering

Use metadata such as:

```text
topic
emergency_type
severity
language
region
source_authority
source_date
offline_eligible
```

Example:

```text
query = severe bleeding
language = hi
region = India
```

The retriever can prioritize relevant Hindi/India/official content.

---

# 18. Query Rewriting

Research whether query rewriting improves:

```text
Hinglish
short queries
ambiguous emergency descriptions
voice transcripts
```

Example:

```text
"gaadi ruk gayi"
```

could be interpreted as:

```text
vehicle breakdown / stranded vehicle
```

Do not blindly rewrite every query.

---

# 19. RAG Data Schema

Prepare a canonical document schema.

Example:

```json
{
  "document_id": "doc_001",
  "title": "Roadside Safety",
  "content": "...",
  "topic": "roadside_safety",
  "emergency_type": "VEHICLE_BREAKDOWN",
  "severity": "MEDIUM",
  "language": "en",
  "region": "India",
  "source_authority": "OFFICIAL",
  "source_url": "https://example.org",
  "last_verified": "2026-08-20",
  "offline_eligible": true
}
```

---

# 20. Chunking Strategy

Research and implement chunking that preserves meaning.

Avoid:

```text
blind fixed-size chunks only
```

Evaluate:

```text
semantic sections
heading-aware chunks
overlap
metadata preservation
```

Every chunk should retain source metadata.

---

# 21. Source Tracking

Every retrieved chunk should map back to:

```text
document_id
source_id
title
URL
authority
verification date
```

This allows the final answer to expose trustworthy sources.

---

# 22. RAG Ingestion Pipeline

Build:

```text
Raw source
 ↓
cleaning
 ↓
normalization
 ↓
metadata
 ↓
chunking
 ↓
embedding
 ↓
indexing
```

This should be runnable repeatedly.

Do not manually upload every document one by one during the final hours.

---

# 23. RAG Evaluation Dataset

Saanvi will provide research-based queries.

Prepare the evaluation pipeline.

Expected format:

```json
{
  "query": "...",
  "language": "hi",
  "expected_intent": "TYRE_PUNCTURE",
  "expected_topics": [
    "safe_positioning",
    "hazard_lights"
  ],
  "required_sources": []
}
```

---

# 24. RAG Metrics

Track:

### Retrieval

```text
Recall@K
Precision@K
MRR
nDCG
Hit Rate
```

### Answer

```text
Groundedness
Faithfulness
Answer relevance
Citation correctness
```

### System

```text
latency
token usage
cost
```

---

# 25. Minimum Evaluation Target

Before calling RAG “done”:

```text
test dataset
+
baseline
+
improved architecture
+
measured result
```

For example:

```text
Vector only
      ↓
Hybrid
      ↓
Hybrid + reranker
```

Compare results.

Do not claim:

> “Our RAG is more accurate”

without a test.

---

# PHASE 1B — AI ORCHESTRATOR FOUNDATION

## Goal

Build the system that decides which subsystem should be called.

---

# 26. Emergency Orchestrator

Concept:

```text
User message
 ↓
Orchestrator
 ├── classify incident
 ├── estimate severity
 ├── determine required services
 ├── retrieve knowledge
 ├── retrieve nearby services
 ├── generate guidance
 └── construct response
```

---

# 27. Structured Incident Classification

The model should produce structured output:

```json
{
  "incident_type": "TYRE_PUNCTURE",
  "severity": "MEDIUM",
  "confidence": 0.94,
  "required_service_categories": [
    "PUNCTURE_REPAIR",
    "MECHANIC"
  ]
}
```

Do not rely only on free-form LLM text.

---

# 28. Severity Rules

The system should distinguish:

```text
LOW
MEDIUM
HIGH
CRITICAL
UNKNOWN
```

Safety-critical categories should have deterministic constraints.

For example:

```text
severe bleeding
vehicle fire
serious accident
```

should trigger high-priority guidance and emergency service discovery.

---

# 29. Deterministic Safety Layer

Do not let the LLM freely decide all safety behavior.

Use:

```text
AI interpretation
      ↓
deterministic safety rules
      ↓
RAG grounding
      ↓
generation
```

The safety layer can enforce:

```text
critical emergency guidance
emergency service categories
warnings
```

---

# 30. Service Recommendation Logic

AI can determine:

```text
what service category is needed
```

The backend/provider layer determines:

```text
which actual services exist nearby
```

Therefore:

```text
AI:
"Need nearest hospital + ambulance"

Places:
"Here are the actual nearby providers"
```

This separation is important.

---

# PHASE 2 — REAL RAG + AI ORCHESTRATION

## Goal

Saanvi's research becomes usable AI intelligence.

---

# 31. Receive Saanvi's Research

Expected handoff:

```text
sources
documents
structured knowledge
multilingual terminology
evaluation queries
expected answer points
offline-critical information
```

Do not ask her to redo research unless a specific gap is discovered.

---

# 32. Ingest Knowledge

Run:

```text
source
 ↓
clean
 ↓
chunk
 ↓
metadata
 ↓
embedding
 ↓
BM25
 ↓
vector index
```

Verify:

```text
document count
chunk count
embedding count
metadata completeness
```

---

# 33. Build Retrieval Pipeline

Initial:

```text
query
 ↓
query preprocessing
 ↓
BM25
+
vector search
 ↓
fusion
 ↓
rerank
 ↓
top contexts
```

---

# 34. Build Grounded Prompt

The LLM should receive:

```text
system rules
+
user situation
+
structured incident
+
retrieved context
+
service data
+
safety constraints
```

It should not receive irrelevant documents.

---

# 35. Citation Mapping

The answer should map claims to sources where possible.

Example:

```json
{
  "source_id": "src_001",
  "title": "Official Emergency Guidance",
  "authority_level": "OFFICIAL"
}
```

---

# 36. Hallucination Control

Implement rules such as:

```text
If context does not contain the answer:
    do not fabricate.
```

Possible response:

```text
"I don't have enough verified information to answer that reliably."
```

For safety-critical questions:

```text
prefer verified guidance
```

---

# 37. AI Response Schema

The AI layer should return a structured response.

Example:

```json
{
  "incident": {
    "incident_type": "TYRE_PUNCTURE",
    "severity": "MEDIUM",
    "confidence": 0.94
  },
  "guidance": {
    "title": "Immediate safety steps",
    "steps": [],
    "safety_note": "..."
  },
  "services_required": [
    "PUNCTURE_REPAIR",
    "MECHANIC"
  ],
  "sources": [],
  "ai": {
    "mode": "ONLINE",
    "rag_used": true
  }
}
```

---

# 38. AI Model Strategy

Current online architecture can use:

```text
Groq
```

for fast LLM inference where appropriate.

Sarvam is used for:

```text
voice/STT/TTS
```

Do not use one model/provider for every task if specialized services are better.

---

# 39. LLM Responsibilities

The online LLM may handle:

```text
intent interpretation
query understanding
response generation
multilingual response
conversation
```

It should NOT independently determine:

```text
real provider existence
exact distance
live availability
GPS location
```

Those come from trusted APIs/data.

---

# PHASE 3 — OFFLINE AI

## Goal

Build the mobile AI subsystem that remains useful when the network disappears.

---

# 40. Offline Architecture

Target:

```text
Flutter
 ↓
Offline Orchestrator
 ↓
GPS
 ↓
Local service search
 +
Local RAG
 ↓
Gemma
 ↓
grounded response
```

---

# 41. Route-Aware Offline Package

The agreed concept:

```text
User enters route
 ↓
backend obtains route
 ↓
route corridor is determined
 ↓
relevant services are collected
 ↓
emergency knowledge is packaged
 ↓
package downloaded
```

The package should cover the journey rather than only:

```text
current location ± 5 km
```

---

# 42. Offline Package Contents

Potential:

```text
route
route geometry
service locations
service categories
addresses
phone numbers
source metadata
emergency knowledge
RAG chunks
embeddings/index
package version
checksum
expiry
```

Only include what is necessary.

---

# 43. Local Retrieval

The mobile app should be able to perform:

```text
query
 ↓
local retrieval
 ↓
relevant cached chunks
```

Possible combination:

```text
local vector retrieval
+
lexical retrieval
```

---

# 44. Gemma's Role

Gemma is not the knowledge base.

Correct:

```text
Local RAG
 ↓
verified context
 ↓
Gemma
 ↓
natural response
```

Incorrect:

```text
Gemma
 ↓
invent emergency instructions
```

---

# 45. Offline Location Intelligence

GPS provides:

```text
latitude
longitude
accuracy
```

The system then searches cached services.

Gemma should NOT calculate geospatial distance.

Use deterministic code.

---

# 46. Offline Response Contract

Offline responses should conceptually match online responses.

Example:

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
      "Provider availability cannot be verified offline."
    ]
  }
}
```

This lets Flutter use one UI structure.

---

# 47. Offline Failure Hierarchy

If Gemma fails:

```text
Gemma
 ↓ failure
local RAG response
 ↓ failure
deterministic emergency guidance
 ↓ failure
cached emergency contacts
```

The application should degrade gracefully.

---

# 48. Offline Model Research

Evaluate:

```text
Gemma mobile variants
Gemma 3n / appropriate mobile model
Gemma 4 edge/mobile candidates if compatible
```

Measure on the actual target phone:

```text
model size
RAM
load time
latency
quality
battery
```

Do not choose based only on benchmark tables.

---

# 49. Embedding Model Research

Evaluate:

```text
EmbeddingGemma
other lightweight multilingual embedding models
```

Test:

```text
English
Hindi
Hinglish
```

The model should be selected based on actual retrieval performance.

---

# PHASE 3B — SARVAM VOICE

## Goal

Turn the emergency assistant into a conversational voice interface.

---

# 50. Existing Voice-Agent Foundation

Already completed:

```text
FastAPI POST endpoint
+
test cases
+
Sarvam integration
+
successful response
```

Do not rebuild this from zero.

---

# 51. Voice Architecture

```text
User voice
 ↓
Sarvam STT
 ↓
text
 ↓
Emergency Assistance API
 ↓
RAG + AI + Services
 ↓
response text
 ↓
Sarvam TTS
 ↓
user hears response
```

---

# 52. Voice Must Reuse RAG

Do NOT create:

```text
Voice RAG
```

and:

```text
Text RAG
```

separately.

Both should call:

```text
same AI/RAG orchestration
```

---

# 53. Multilingual Voice

Test:

```text
English
Hindi
Hinglish
```

Example:

```text
"Highway pe tyre puncture ho gaya"
```

The system should:

```text
understand
retrieve
respond
```

in the user's language when appropriate.

---

# 54. Voice Agent Future Extension

Potential:

```text
AI detects user needs mechanic
 ↓
proposes contact
 ↓
asks permission
 ↓
agent contacts provider
 ↓
converses
 ↓
returns result
```

This is an advanced feature.

It must not block the core system.

---

# PHASE 4 — AGENTIC AI

## Goal

Implement the provider-contact agent only if the core product is stable.

---

# 55. Agent Architecture

```text
User
 ↓
AI identifies need
 ↓
AI proposes action
 ↓
User permission
 ↓
Action execution
 ↓
Provider conversation
 ↓
result
 ↓
RAAHAT
```

---

# 56. Permission Boundary

Never:

```text
LLM → call mechanic automatically
```

Always:

```text
LLM
 ↓
"Would you like me to contact this mechanic?"
 ↓
User confirms
 ↓
action
```

---

# 57. Agent Tool Contracts

Potential tools:

```text
find_service
get_service_details
get_current_location
prepare_provider_message
contact_provider
get_action_status
```

The LLM chooses tools, but the backend enforces permissions.

---

# 58. Agent Output

Example:

```json
{
  "action_id": "act_123",
  "status": "CONFIRMATION_REQUIRED",
  "service_id": "svc_123",
  "reason": "Confirm whether a mechanic can reach your current location."
}
```

---

# PHASE 5 — FULL INTEGRATION + TESTING

## Goal

Make the intelligence layer reliable in the complete application.

---

# 59. Online End-to-End Flow

Test:

```text
React
 ↓
Firebase
 ↓
FastAPI
 ↓
Emergency Orchestrator
 ↓
Incident classification
 ↓
RAG
 ↓
Google/fallback services
 ↓
Service ranking
 ↓
LLM
 ↓
Response
```

---

# 60. Flutter Online Flow

Test:

```text
Flutter
 ↓
Firebase
 ↓
FastAPI
 ↓
AI/RAG
 ↓
Services
 ↓
Response
```

---

# 61. Flutter Offline Flow

Test:

```text
Flutter
 ↓
No internet
 ↓
GPS
 ↓
Local retrieval
 ↓
Gemma
 ↓
Cached services
 ↓
Offline response
```

---

# 62. Voice Flow

Test:

```text
Voice
 ↓
Sarvam STT
 ↓
Emergency API
 ↓
RAG
 ↓
services
 ↓
Sarvam TTS
```

---

# 63. Failure Testing

Test:

### RAG

```text
no context
bad retrieval
empty index
embedding failure
LLM failure
```

### Voice

```text
STT failure
TTS failure
provider timeout
```

### Offline

```text
model missing
model crash
corrupted package
empty local index
GPS unavailable
```

### External APIs

```text
Google failure
fallback failure
rate limit
```

---

# 64. RAG Evaluation

Use Saanvi's test dataset.

Measure:

```text
Recall@K
MRR
nDCG
answer relevance
groundedness
citation correctness
latency
```

Compare:

```text
baseline
vs
hybrid
vs
hybrid + reranking
```

---

# 65. AI Latency Budget

Measure:

```text
classification
+
retrieval
+
reranking
+
LLM
+
service search
```

Target a response that feels interactive.

Do not optimize blindly before measuring.

---

# 66. AI Cost Awareness

Track:

```text
LLM tokens
API calls
embedding cost
external API usage
```

Prefer free/low-cost options compatible with the hackathon.

---

# 67. Security

Protect:

```text
API keys
Firebase credentials
database credentials
user data
location
voice data
```

Do not commit:

```text
.env
service account JSON
API keys
```

---

# 68. PostgreSQL Responsibility

Satwik owns PostgreSQL integration.

Potential data areas:

```text
users
incidents
service metadata
RAG documents
RAG chunks
source metadata
offline packs
actions
```

The final schema should be kept aligned with the actual RAG and application requirements.

---

# 69. Firebase Responsibility

Satwik owns the Firebase-side coordination with the team.

Use Firebase primarily for:

```text
Authentication
```

The application should obtain:

```text
Firebase ID token
```

and send it to FastAPI.

---

# 70. Database/API Boundary

Never expose raw database rows.

Use:

```text
DB
 ↓
repository
 ↓
service
 ↓
Pydantic response
 ↓
client
```

---

# 71. Phase 1 Exit Criteria

Satwik can move to Phase 2 when:

- [ ] AI architecture is understood
- [ ] RAG architecture is finalized
- [ ] RAG schemas defined
- [ ] ingestion pipeline skeleton exists
- [ ] embedding pipeline works
- [ ] lexical retrieval works
- [ ] vector retrieval works
- [ ] hybrid retrieval prototype works
- [ ] evaluation framework exists
- [ ] AI response schema exists
- [ ] emergency orchestrator skeleton exists
- [ ] PostgreSQL environment is ready
- [ ] Firebase integration plan is ready
- [ ] existing Sarvam endpoint is preserved

Most importantly:

> **Satwik should be able to ingest Saanvi's research immediately when it arrives.**

---

# 72. Phase 2 Exit Criteria

- [ ] Saanvi's knowledge ingested
- [ ] RAG index populated
- [ ] hybrid retrieval working
- [ ] reranking tested
- [ ] evaluation dataset running
- [ ] source tracking working
- [ ] grounded generation working
- [ ] emergency classifier working
- [ ] service-category selection working
- [ ] FastAPI integration working
- [ ] React/Flutter can consume AI responses

---

# 73. Phase 3 Exit Criteria

- [ ] offline RAG working
- [ ] Gemma tested on target phone
- [ ] local retrieval working
- [ ] offline response contract working
- [ ] Sarvam voice working with RAG
- [ ] Hindi/Hinglish tested
- [ ] online/offline AI mode handled

---

# 74. Phase 4 Exit Criteria

Only if time allows:

- [ ] agentic provider contact
- [ ] permission workflow
- [ ] action status
- [ ] provider conversation
- [ ] failure handling

This is an advanced feature and must never block the core emergency system.

---

# 75. Phase 5 Exit Criteria

- [ ] online demo works
- [ ] offline demo works
- [ ] voice demo works
- [ ] RAG evaluation completed
- [ ] latency measured
- [ ] failure scenarios tested
- [ ] API integration stable
- [ ] deployment configuration supported
- [ ] judge-facing technical explanations ready

---

# 76. Handoff to Santosh

Satwik must provide:

```text
AI API contract
AI response schema
RAG endpoint
AI error codes
model/provider requirements
voice endpoint requirements
offline response contract
agentic action contract
```

Santosh should never have to guess:

```text
"What does the AI endpoint return?"
```

---

# 77. Handoff to Saanvi

Satwik must provide:

```text
offline AI interface
local RAG interface
Gemma model requirements
offline response schema
model loading states
failure states
mobile constraints
```

Saanvi should never have to guess:

```text
"What format should the offline AI return?"
```

---

# 78. What Satwik Can Work On Independently

If Saanvi is still researching:

```text
RAG architecture
retrieval pipeline
embedding
BM25
reranking
evaluation framework
AI schemas
orchestrator
Sarvam
Gemma research
PostgreSQL
Firebase
```

If Santosh is still building backend:

```text
AI subsystem
RAG
evaluation
voice
offline AI
database layer
```

Therefore:

> **Satwik should have the largest amount of dependency-free work in Phase 1.**

---

# 79. What Satwik Must Not Wait For

Do not wait for:

```text
Saanvi's final research
Santosh's final UI
Google API integration
Flutter completion
deployment
```

Use:

```text
mock documents
mock service data
mock API responses
sample queries
```

to build the AI system.

---

# 80. What Satwik Must Not Change Without Agreement

Do not independently change:

```text
API response structure
Flutter contract
React contract
Google provider architecture
offline UI
Firebase frontend behavior
```

If AI needs another field:

```text
propose
↓
discuss
↓
update API contract
↓
implement
```

---

# 81. AI Assistant Instructions

Satwik's AI assistant must behave as:

```text
Senior AI Engineer
+
RAG Engineer
+
FastAPI AI Engineer
+
LLM Orchestration Engineer
+
On-device AI Researcher
+
Voice AI Engineer
+
AI Evaluation Engineer
```

It must:

- understand the entire RAAHAT architecture
- preserve API contracts
- prioritize accuracy
- measure retrieval quality
- avoid hallucination
- use grounded generation
- separate AI reasoning from deterministic safety logic
- use mocks to avoid dependencies
- avoid unnecessary complexity
- prefer measurable improvements
- protect secrets
- distinguish verified information from generated content

---

# 82. AI Assistant Decision Rule

When Satwik asks:

> “What should I do now?”

the assistant must determine:

```text
current phase
↓
incomplete exit criteria
↓
dependencies
↓
highest-impact task
↓
next concrete implementation
```

It should not automatically assign:

```text
React
Flutter
Google API frontend
```

unless integration requires it.

---

# 83. Priority Rules

```text
P0 = blocks core product
P1 = core AI capability
P2 = integration
P3 = advanced intelligence
P4 = optional USP
```

Priority order:

```text
RAG correctness
>
Emergency orchestration
>
API integration
>
Offline AI
>
Voice
>
Agentic AI
>
polish
```

However, the existing Sarvam voice prototype should remain preserved because it is already partially built.

---

# 84. Anti-Overengineering Rule

Do not build:

```text
Graph RAG
+
Agentic RAG
+
Multi-agent RAG
+
Knowledge graph
+
complex memory
```

just because they sound impressive.

The rule is:

> **Complexity must earn its place through measurable improvement.**

If:

```text
Hybrid RAG + reranker
```

is more accurate and reliable than a complex architecture within the hackathon timeframe, use the simpler architecture.

---

# 85. AI Safety Rule

RAAHAT is an emergency assistance platform.

Therefore:

```text
LLM output
≠
verified fact
```

Safety-critical information must be grounded in:

```text
trusted sources
+
deterministic rules
+
clear uncertainty
```

Never invent:

- emergency numbers
- provider availability
- medical claims
- exact distances
- service status
- location facts

---

# 86. Location Intelligence Separation

Satwik's AI may determine:

```text
"User needs a hospital."
```

But it should NOT invent:

```text
"Hospital X is 1.2 km away."
```

That must come from:

```text
Google / fallback provider / cached data
```

Similarly:

```text
AI:
Need mechanic

Places:
Actual mechanics
```

---

# 87. Final AI Architecture

```text
                         USER
                           │
                           ▼
                 React / Flutter / Voice
                           │
                           ▼
                         FastAPI
                           │
                           ▼
                Emergency Orchestrator
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
      Incident          RAG Engine      Service Intent
      Classifier             │                 │
          │                  │                 ▼
          │          ┌───────┼───────┐      Places
          │          │       │       │
          │         BM25   Vector  Reranker
          │          │       │       │
          │          └───────┼───────┘
          │                  ▼
          │             Grounded Context
          │                  │
          └────────────┬─────┘
                       ▼
                  Safety Layer
                       │
                       ▼
                      LLM
                       │
                       ▼
                Structured Response
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        React        Flutter       Voice
                                   │
                                  TTS
```

Offline:

```text
Flutter
   │
   ▼
Offline Orchestrator
   │
   ├── GPS
   ├── Cached Services
   ├── Local RAG
   └── Gemma
         │
         ▼
   Safety/Fallback
         │
         ▼
   Same Response Shape
```

---

# 88. Final 24-Hour Execution Priority

If time becomes extremely limited:

## Tier 1 — MUST WORK

```text
1. RAG
2. Emergency orchestration
3. FastAPI integration
4. Nearby services
5. Basic emergency guidance
```

## Tier 2 — SHOULD WORK

```text
6. Offline RAG
7. Gemma
8. Sarvam voice
9. Route-aware offline package
```

## Tier 3 — HIGH-VALUE USP

```text
10. Multilingual voice
11. advanced retrieval/reranking
12. agentic provider contact
```

## Tier 4 — OPTIONAL

```text
13. advanced agentic behavior
14. complex RAG variants
15. extra polish
```

---

# 89. Final Demo Flow — AI Perspective

The strongest technical demo should show:

```text
User:
"My tyre got punctured on the highway."
        ↓
AI understands:
TYRE_PUNCTURE
MEDIUM
        ↓
RAG:
verified safety guidance
        ↓
Service Intelligence:
nearest puncture/mechanic services
        ↓
Response
        ↓
User disables internet
        ↓
Same user asks again
        ↓
GPS + cached data + local RAG + Gemma
        ↓
Offline response
        ↓
User switches to voice
        ↓
Sarvam
        ↓
same RAAHAT intelligence
```

This demonstrates that the system is not merely:

```text
Chatbot + Google Maps
```

It is:

```text
Emergency Intelligence
+
RAG
+
Location Intelligence
+
Voice
+
Offline AI
```

---

# 90. Judge-Facing Technical Questions

## “Why RAG?”

> “Emergency guidance should be grounded in verified knowledge rather than generated purely from model memory.”

## “Why hybrid RAG?”

> “Emergency queries contain both semantic meaning and exact terminology, especially across multilingual and Hinglish input. Combining lexical and semantic retrieval improves recall.”

## “Why reranking?”

> “Initial retrieval generates candidates. Reranking helps select the most relevant evidence before generation.”

## “Why Gemma offline?”

> “When connectivity disappears, the mobile application still needs local intelligence. Gemma provides the local generation layer while cached RAG remains the knowledge source.”

## “Does Gemma know where hospitals are?”

> “No. Location and service information comes from GPS plus trusted/cached service data. Gemma interprets the retrieved information.”

## “Why not simply use an LLM?”

> “Because a generic LLM does not know the user's current service availability, verified local emergency information, or our curated knowledge base.”

## “Why not compete with Google Maps?”

> “We don't. We use mapping infrastructure as a foundation and add emergency-specific intelligence, prioritization, conversational assistance and offline capability on top.”

---

# 91. Final Definition of Done

Satwik's work is complete when:

> **RAAHAT has a reliable AI intelligence layer that can understand an emergency situation, classify it, determine required assistance, retrieve verified knowledge using high-quality RAG, integrate actual nearby service data, generate grounded guidance, support multilingual voice through Sarvam, operate offline through local retrieval and Gemma, gracefully fall back when AI components fail, and expose all of this through stable FastAPI contracts consumed by React and Flutter.**

At the same time:

> **The AI system must be measurable, grounded, testable and explainable enough for the team to defend its architecture before judges.**

---

# 92. One-Line Mission

> **Build RAAHAT's intelligence: a grounded, location-aware, multilingual AI system that can reason over verified knowledge online, continue helping offline with local RAG + Gemma, communicate through voice, and safely orchestrate the right emergency assistance.**
