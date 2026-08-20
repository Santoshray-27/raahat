# RAAHAT — RAG Architecture, Research & Evaluation Specification

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Owner:** Satwik — AI/RAG/Backend  
**Purpose:** Define what RAAHAT's RAG does, how it works, what data it needs, what research is required, and how we prove that it is accurate.

---

# 1. Core Decision

RAAHAT will use:

> **Hybrid + metadata-aware + contextualized + reranked RAG, controlled by an AI orchestrator.**

Pipeline:

```text
User Query
   ↓
Query Understanding
   ↓
Intent / Region / Language / Emergency Metadata
   ↓
Metadata Filtering
   ↓
┌───────────────────────┐
│ Parallel Retrieval    │
│                       │
│ BM25       +  Vector  │
└────────────┬──────────┘
             ↓
       Result Fusion
             ↓
        Top 30–50
             ↓
          Reranker
             ↓
         Top 5–10
             ↓
 Authority / Safety Check
             ↓
      Grounded Context
             ↓
            LLM
             ↓
 Grounded Answer + Sources
```

The goal is **not maximum architectural complexity**. The goal is maximum retrieval correctness and groundedness for safety-sensitive roadside/emergency questions.

---

# 2. What RAG Is Responsible For

RAG provides trusted textual knowledge for questions such as:

- What should I do after a road accident?
- What should I do if someone is bleeding heavily?
- What should I do while waiting for an ambulance?
- What should I do after a tyre puncture?
- Is it safe to continue driving?
- What should I do if my vehicle breaks down on a highway?
- What should I do if a vehicle catches fire?
- Which emergency procedure applies to this situation?
- Which region-specific emergency information is relevant?

RAG should combine the user's situation with verified knowledge.

---

# 3. What RAG Is NOT Responsible For

Do not use RAG as the primary system for:

| Requirement | Correct component |
|---|---|
| Current coordinates | GPS |
| Nearby hospitals | Google Places |
| Nearby mechanics | Google Places |
| Nearby towing | Google Places |
| Live provider availability | Actual provider/agent interaction |
| Navigation | Google Routes/Maps |
| User account | Firebase |
| User/incident records | PostgreSQL |
| Offline cached providers | Flutter local DB |
| Offline language reasoning | Gemma |
| Safety-critical deterministic escalation | Rules/decision engine |

Example:

> “Nearest hospital?”

Use **Google Places**, not RAG.

> “What should I do while waiting for an ambulance?”

Use **RAG**.

> “Call this mechanic and ask whether they can come.”

Use the **agent/tool layer**.

---

# 4. Position in the Complete RAAHAT Architecture

```text
User
 ↓
React / Flutter / Sarvam
 ↓
FastAPI
 ↓
Authentication + Validation
 ↓
AI Orchestrator
 ↓
Query Understanding
 ↓
┌──────────────┬───────────────┬──────────────┐
│              │               │              │
LLM           RAG          Google Places   PostgreSQL
│              │               │              │
└──────────────┴───────────────┴──────────────┘
                       ↓
                Decision Engine
                       ↓
                Service Ranking
                       ↓
                  Action Plan
                       ↓
              User / Voice / Tools
```

The orchestrator decides whether RAG is necessary.

---

# 5. Query Understanding

The raw query is first converted into structured information.

Example:

> “Bhai accident hua hai aur mere dost ka khoon bahut nikal raha hai, kya karu?”

Possible output:

```json
{
  "intent": "emergency_guidance",
  "incident_type": "road_accident",
  "emergency_type": "severe_bleeding",
  "severity": "critical",
  "language": "hi",
  "region": "India",
  "requires_services": true
}
```

This structure is used to improve retrieval.

---

# 6. Query Rewriting / Enrichment

The original query remains available, but the retriever can receive a normalized query.

Example:

```text
Original:
"Highway par tyre puncture ho gaya kya karu?"

Normalized:
"roadside tyre puncture highway safety procedure"
```

For multilingual queries:

```text
Original language
+
normalized semantic query
+
language metadata
```

This should be evaluated rather than assumed to improve quality.

---

# 7. Metadata-Aware Retrieval

Every knowledge chunk should contain metadata.

Example:

```json
{
  "document_id": "doc_001",
  "chunk_id": "chunk_014",
  "source_name": "Official Emergency Guide",
  "source_url": "...",
  "authority_level": "official",
  "country": "India",
  "state": "Madhya Pradesh",
  "language": "en",
  "domain": "first_aid",
  "emergency_type": "bleeding",
  "severity": "critical",
  "retrieved_at": "2026-08-20",
  "last_verified": "2026-08-20",
  "version": "1"
}
```

Filters can include:

- country
- state
- region
- language
- domain
- emergency type
- severity
- authority level

---

# 8. Why Hybrid Retrieval?

## Vector retrieval

Good at semantic similarity.

Example:

```text
User:
"What should I do if a lot of blood is coming out?"

Source:
"Immediate management of severe external bleeding"
```

The wording differs, but the meaning matches.

## BM25 / lexical retrieval

Useful for:

- exact emergency numbers
- exact service names
- acronyms
- terminology
- named procedures
- exact phrases

Example:

```text
"112"
"ambulance"
"emergency number"
```

## Hybrid

```text
Semantic similarity
+
Exact lexical matching
```

This is the chosen baseline for RAAHAT.

---

# 9. Hybrid Retrieval Pipeline

```text
Query
 ↓
Metadata filter
 ↓
       ┌───────────────┐
       │               │
       ▼               ▼
     BM25           Vector
       │               │
       └───────┬───────┘
               ↓
         Result Fusion
               ↓
          Top 30–50
               ↓
            Reranker
               ↓
            Top 5–10
```

Fusion candidates to research:

1. Weighted score fusion
2. Reciprocal Rank Fusion (RRF)
3. Normalized-score fusion

Do not decide purely from theory. Benchmark them.

---

# 10. Reranking

Initial retrieval prioritizes recall.

The reranker improves final ordering.

```text
BM25 + Vector
      ↓
30–50 candidates
      ↓
Cross-encoder / reranker
      ↓
5–10 best chunks
```

Research:

- multilingual rerankers
- CPU/GPU requirements
- latency
- model size
- license
- quality on emergency queries

Run:

```text
Hybrid
vs
Hybrid + Reranker
```

and keep the reranker only if evaluation shows meaningful improvement.

---

# 11. Contextual Chunking

Do not index isolated fragments.

Bad:

```text
"Apply pressure."
```

Better:

```text
Document: Emergency First Aid Guide
Section: Severe External Bleeding
Topic: Immediate first-aid response

Chunk:
[relevant instructions]
```

Each chunk should retain enough document/section context to remain understandable after retrieval.

---

# 12. Chunking Research

Do not assume one chunk size is universally correct.

Test:

- small chunks
- medium chunks
- large chunks
- different overlap values
- semantic/heading-based boundaries
- contextualized chunks

Measure:

- Recall@K
- Precision@K
- MRR
- nDCG
- Context Precision
- Context Recall
- Faithfulness
- latency
- context/token usage

---

# 13. Knowledge Domains

Start small and high quality.

## Domain A — Road accidents

Research:

- immediate actions
- secondary-collision prevention
- safe positioning
- emergency escalation
- contacting emergency services

## Domain B — First aid

Research:

- severe bleeding
- unconsciousness
- breathing problems
- burns
- fractures
- head injury
- spinal injury
- shock
- seizures
- other high-value emergency scenarios

## Domain C — Vehicle breakdown

Research:

- safe stopping
- hazard lights
- highway breakdown safety
- when not to continue
- waiting for assistance

## Domain D — Tyre/puncture

Research:

- puncture safety
- highway stopping
- tyre changing safety
- when to stop driving
- roadside precautions

## Domain E — Vehicle fire

Research:

- immediate safety
- evacuation
- emergency escalation
- hazards

## Domain F — Roadside/towing safety

Research:

- towing precautions
- waiting safely
- recovery procedures

## Domain G — Regional emergency information

Research:

- national emergency numbers
- police
- ambulance
- fire
- regional emergency services
- official sources

---

# 14. Data Research Priority

Research in this order:

### Priority 1
Emergency procedures.

### Priority 2
Emergency numbers and regional information.

### Priority 3
Accident/roadside safety.

### Priority 4
Breakdown/puncture/towing guidance.

### Priority 5
Multilingual equivalents.

Do not spend the first hours collecting hundreds of low-value documents.

---

# 15. Source Hierarchy

Use:

### Tier 1 — Official

- government
- official emergency services
- official health authorities
- official transport/highway authorities
- recognized public emergency organizations

### Tier 2 — Institutional

- major hospitals
- recognized medical institutions
- established emergency organizations
- reputable safety organizations

### Tier 3 — Secondary

Only when necessary.

Avoid:

- random blogs
- SEO content
- anonymous posts
- social-media claims
- AI-generated articles
- unverified medical advice

For safety-critical content, source authority matters more than corpus size.

---

# 16. Research Dataset

Create a structured research file.

Recommended fields:

```text
id
title
domain
topic
emergency_type
severity
country
state
region
language
source_name
source_url
authority_level
retrieved_at
last_verified
version
content
notes
```

This dataset becomes the input to ingestion.

---

# 17. Knowledge Ingestion Pipeline

```text
Trusted websites / PDFs / documents
                ↓
          Text extraction
                ↓
              Cleaning
                ↓
           Boilerplate removal
                ↓
            Deduplication
                ↓
          Metadata extraction
                ↓
        Contextual enrichment
                ↓
             Chunking
                ↓
       ┌────────┴─────────┐
       ▼                  ▼
   Embeddings            BM25
       ▼                  ▼
 Vector index        Lexical index
```

---

# 18. Cleaning

Remove:

- navigation menus
- advertisements
- cookie text
- repeated headers
- unrelated footers
- duplicate paragraphs
- irrelevant page boilerplate

Preserve:

- headings
- numbered instructions
- warnings
- tables where meaningful
- source identity
- document context

---

# 19. Deduplication

The same guidance may occur on many websites.

Deduplicate using:

- normalized text
- source/document identity
- similarity
- document version

Prefer the authoritative source.

---

# 20. Conflicting Sources

If sources disagree:

```text
Official
   >
Institutional
   >
Secondary
```

If two authoritative sources conflict:

1. Research the latest official version.
2. Preserve both source records.
3. Do not silently merge contradictory instructions.
4. Mark unresolved conflict.
5. Use conservative/safe fallback where appropriate.

---

# 21. Embedding Model Research

Compare candidate embedding models on:

- English retrieval
- Hindi retrieval
- Hinglish retrieval
- cross-language retrieval
- model size
- latency
- CPU requirements
- vector dimensions
- license
- offline suitability

Required experiments:

```text
English → English
Hindi → Hindi
Hindi → English
English → Hindi
Hinglish → English
```

The model should be selected using the team's actual evaluation queries.

---

# 22. Vector Store Research

Candidates:

- PostgreSQL + pgvector
- FAISS
- Qdrant
- Chroma
- another lightweight option if justified

Compare:

- setup complexity
- filtering
- persistence
- latency
- FastAPI integration
- offline compatibility
- storage
- hackathon reliability

PostgreSQL + pgvector is attractive because PostgreSQL is already part of RAAHAT, but it must still be validated.

---

# 23. BM25 Research

Evaluate:

- implementation options
- tokenizer
- multilingual behavior
- exact-match behavior
- integration with vector retrieval
- persistence
- offline operation

A simple reliable implementation is preferable to unnecessary infrastructure.

---

# 24. Reranker Research

Compare:

- cross-encoder rerankers
- multilingual rerankers
- latency
- memory
- license
- quality
- offline feasibility

Benchmark:

```text
Hybrid
vs
Hybrid + reranker
```

---

# 25. Generation Model Research

Candidates include the team's available Groq-hosted models and Gemma for offline.

Compare:

- instruction following
- structured output
- multilingual ability
- context length
- latency
- hallucination behavior
- cost
- rate limits

Do not choose solely by benchmark reputation.

---

# 26. Grounded Generation

Final prompt should contain:

```text
SYSTEM SAFETY RULES

USER QUERY

STRUCTURED INCIDENT

LANGUAGE / REGION

RETRIEVED EVIDENCE

OPTIONAL SERVICE RESULTS

RESPONSE FORMAT
```

Rules:

1. Use retrieved evidence.
2. Do not invent facts.
3. Do not invent emergency numbers.
4. Do not invent provider availability.
5. Do not contradict authoritative evidence.
6. Admit uncertainty.
7. Keep emergency guidance concise.
8. Prefer safer escalation when evidence is insufficient.

---

# 27. Sources / Citations

Backend should retain:

```json
{
  "source_name": "...",
  "source_url": "...",
  "authority_level": "official",
  "last_verified": "..."
}
```

The UI can expose:

```text
Source: Official Emergency Guidance
Verified: 20 Aug 2026
```

Citation support itself should be evaluated.

---

# 28. RAG Response Modes

## Guidance

```text
"What should I do?"
```

Return:

- immediate actions
- warnings
- escalation

## Guidance + Services

```text
"What should I do and where can I get help?"
```

Combine RAG + Google Places.

## Knowledge

```text
"Why shouldn't I continue driving?"
```

Return grounded explanation.

## No-answer

If evidence is inadequate:

```text
I don't have enough verified information
to safely answer that specific question.
```

Then use appropriate emergency fallback.

---

# 29. Safety Boundary

For:

- low retrieval confidence
- missing authoritative evidence
- conflicting evidence
- safety-critical uncertainty

the system should **not confidently improvise**.

This is a product requirement, not merely an evaluation preference.

---

# 30. Offline RAG

Online:

```text
FastAPI
 ↓
Remote RAG
 ↓
Groq/selected LLM
```

Offline:

```text
Flutter
 ↓
Local DB
 ↓
Local retrieval
 ↓
Offline RAG
 ↓
Gemma
```

The offline knowledge base should be a compact, high-value subset.

---

# 31. Offline Knowledge Package

Conceptually:

```text
offline_pack/
├── metadata.json
├── emergency_contacts.json
├── providers.json
├── route.json
├── rag/
│   ├── chunks
│   ├── vector_index
│   └── bm25_index
└── model/
    └── gemma/
```

Exact runtime/index formats depend on the selected libraries.

---

# 32. Offline RAG Research

Measure:

- package size
- RAM usage
- storage
- retrieval latency
- Gemma inference latency
- battery impact
- multilingual performance
- quality degradation vs online RAG

---

# 33. Evaluation Strategy

Evaluate the RAG in layers:

```text
Retrieval
   ↓
Ranking
   ↓
Grounding
   ↓
Answer relevance
   ↓
Safety
   ↓
End-to-end usefulness
```

A fluent answer is not evidence of a good RAG system.

---

# 34. Golden Evaluation Dataset

Create a manually reviewed set.

Minimum useful target:

```text
50–100 queries
```

Better:

```text
100–300 queries
```

Each record should include:

```text
query
language
region
intent
emergency_type
severity
relevant_document_ids
relevant_chunk_ids
expected_answer_points
safety_level
```

---

# 35. Query Categories

Include:

### Easy

> “What should I do after a tyre puncture?”

### Paraphrase

> “My car suddenly lost tyre pressure while driving.”

### Hindi

> “Highway par tyre puncture ho gaya, kya karna chahiye?”

### Hinglish

> “Accident ho gaya hai, bleeding ho rahi hai, kya karu?”

### Ambiguous

> “My car stopped. What do I do?”

### Multi-intent

> “There was an accident, someone is bleeding and I need a hospital.”

### Multi-hop

> “What should I do first and which emergency service should I contact?”

---

# 36. Retrieval Metrics

## Recall@K

Measures how much relevant evidence appears within top K.

Track:

```text
Recall@5
Recall@10
Recall@20
```

## Precision@K

Measures how much of top K is relevant.

Track:

```text
Precision@5
Precision@10
```

## MRR

Rewards finding the first relevant result high in the ranking.

## nDCG@K

Useful when relevance is graded:

```text
3 = highly relevant
2 = useful
1 = marginal
0 = irrelevant
```

BEIR commonly evaluates retrieval using nDCG, MAP, Recall, Precision and MRR. citeturn0search2turn0search11

---

# 37. RAG-Specific Metrics

## Context Precision

Measures whether useful retrieved chunks are ranked effectively. RAGAS uses an average-precision-style formulation where relevant items appearing earlier contribute more. citeturn0search0turn0search1

## Context Recall

Measures how much of the information needed for the reference answer was retrieved. It requires reference information and therefore belongs primarily in offline evaluation. citeturn0search1

---

# 38. Generation Metrics

## Faithfulness

Question:

> Are answer claims supported by retrieved context?

Conceptually:

```text
supported claims
----------------
total claims
```

RAGAS defines faithfulness around consistency between response claims and retrieved context. citeturn0search0

## Answer Relevancy

Does the answer actually address the user's question?

## Factual Correctness

Does the answer agree with a trusted reference?

## Citation Support

Does each cited source actually support the claim?

---

# 39. Safety Metric

Create a custom safety evaluation.

Each answer should be checked for:

- invented emergency numbers
- unsafe instructions
- unsupported medical claims
- wrong emergency escalation
- false service availability
- unsupported certainty
- missing critical warning

For RAAHAT:

> **Safety should be a hard gate, not merely an average metric.**

---

# 40. Latency Metrics

Measure:

```text
embedding latency
BM25 latency
vector latency
fusion latency
reranker latency
generation latency
total latency
```

Track:

```text
P50
P95
```

Voice needs particularly low perceived latency.

---

# 41. Context Efficiency

Measure:

- chunks retrieved
- chunks sent to LLM
- token count
- answer length
- irrelevant context
- retrieval latency

Goal:

> Maximum useful evidence with minimum context noise.

---

# 42. Ablation Testing

This is important for defending the architecture.

Test:

```text
A. Vector only

B. BM25 only

C. Hybrid

D. Hybrid + reranker

E. Hybrid + reranker + metadata

F. Hybrid + reranker + metadata + contextual chunks
```

Measure each version.

Example:

| Version | Recall@10 | nDCG@10 | Faithfulness | P95 latency |
|---|---:|---:|---:|---:|
| Vector | — | — | — | — |
| BM25 | — | — | — | — |
| Hybrid | — | — | — | — |
| + Reranker | — | — | — | — |
| + Metadata | — | — | — | — |
| + Contextual chunks | — | — | — | — |

Never claim an architectural component improves accuracy until this experiment shows it.

---

# 43. Failure Modes To Test

## Retrieval failures

- correct document not retrieved
- wrong region
- wrong language
- outdated document
- duplicate documents
- too much noise
- too little context

## Generation failures

- hallucination
- ignores retrieved evidence
- answers a different question
- overlong response
- unsupported certainty
- wrong emergency escalation

## Data failures

- conflicting sources
- malformed documents
- missing metadata
- stale verification date

---

# 44. Debugging Flow

When a RAG answer is bad:

```text
1. Was intent correct?
        ↓
2. Was region/language correct?
        ↓
3. Were metadata filters correct?
        ↓
4. Did BM25 retrieve useful evidence?
        ↓
5. Did vector search retrieve useful evidence?
        ↓
6. Did fusion preserve it?
        ↓
7. Did reranker rank it highly?
        ↓
8. Was it passed to the LLM?
        ↓
9. Did LLM follow grounding rules?
        ↓
10. Did the final answer remain faithful?
```

This prevents randomly changing prompts/models when the actual problem is retrieval.

---

# 45. Research Work — Satwik

## Workstream 1 — Knowledge sources

Find authoritative sources for:

- accident safety
- first aid
- bleeding
- vehicle breakdown
- tyre/puncture
- vehicle fire
- towing
- emergency numbers

Deliverable:

```text
sources.csv
```

## Workstream 2 — Embeddings

Compare multilingual candidates.

## Workstream 3 — Vector storage

Compare pgvector / FAISS / Qdrant / Chroma.

## Workstream 4 — BM25

Select implementation.

## Workstream 5 — Fusion

Compare RRF / weighted fusion / normalized fusion.

## Workstream 6 — Reranker

Benchmark candidate models.

## Workstream 7 — Chunking

Run chunk-size/overlap experiments.

## Workstream 8 — Multilingual

Test Hindi, English and Hinglish.

## Workstream 9 — Offline

Test local retrieval + Gemma.

## Workstream 10 — Evaluation

Build golden dataset and automated evaluation.

---

# 46. Research Work — Santosh

Santosh does not need to build the retrieval engine.

Research:

- service category terminology
- emergency service UX
- how guidance should be displayed
- citation/source UI
- explainable recommendation UI
- which user queries should trigger RAG
- user-friendly emergency response formats

---

# 47. Research Work — Saanvi

Research:

- offline knowledge requirements
- mobile storage constraints
- local database options
- offline package format
- offline RAG UX
- stale-data warnings
- multilingual mobile interaction
- Gemma mobile runtime requirements

---

# 48. Suggested RAG API

```text
POST /rag/query
```

Request:

```json
{
  "query": "What should I do if someone is bleeding?",
  "language": "en",
  "region": "India",
  "emergency_type": "bleeding",
  "severity": "critical"
}
```

Response:

```json
{
  "answer": "...",
  "sources": [],
  "retrieved_contexts": [],
  "retrieval_metadata": {
    "retriever": "hybrid",
    "reranked": true
  }
}
```

Evaluation-only metadata can be exposed in development.

---

# 49. Main Emergency API Integration

Users should normally interact with:

```text
POST /emergency-assistance
```

Internally:

```text
/emergency-assistance
       ↓
AI Orchestrator
       ├── RAG if knowledge needed
       ├── Google Places if service needed
       ├── PostgreSQL if structured data needed
       └── Tools if action needed
```

RAG remains a subsystem, not the entire backend.

---

# 50. RAG + Agentic AI

Example:

> “Accident hua hai. What should I do and find the nearest hospital.”

The agent routes:

```text
Query
 ↓
AI Router
 ↓
┌───────────────┬────────────────┐
│               │                │
RAG          Google Places     PostgreSQL
│               │                │
Guidance      Hospitals       emergency data
│               │                │
└───────────────┴────────────────┘
                ↓
          Decision Engine
                ↓
             Response
```

The agent should not call every subsystem for every query.

---

# 51. Recommended MVP

For the hackathon, start with:

```text
Trusted knowledge
 ↓
Cleaning + metadata
 ↓
Contextual chunking
 ↓
Embeddings
 ↓
Vector search
 +
BM25
 ↓
Fusion
 ↓
Reranker
 ↓
Top 5–10
 ↓
Groq LLM
 ↓
Grounded answer
```

Then benchmark.

Only add further complexity if it improves measured quality.

---

# 52. "Perfect Accuracy" Principle

Absolute perfect accuracy is unrealistic.

The practical objective is:

> **Maximize retrieval correctness, groundedness and safety while minimizing hallucination and irrelevant context.**

For RAAHAT, an honest answer such as:

> “I don't have enough verified information to answer that safely.”

is preferable to a confident fabricated instruction.

---

# 53. Judge-Facing Explanation

If asked:

### “What RAG are you using?”

> “We use a hybrid, metadata-aware RAG architecture. We combine semantic vector retrieval with BM25 lexical retrieval, fuse the candidate results, rerank them, and pass only the strongest evidence to the generation model. Our knowledge is source-controlled and tagged by region, language, emergency type and authority.”

### “Why not just vector RAG?”

> “Emergency queries contain both semantic meaning and exact terms. Vector retrieval handles semantic similarity, while BM25 handles exact terminology. We benchmark both individually and together.”

### “Why not GraphRAG?”

> “Our core knowledge problem is retrieving authoritative emergency guidance. We don't currently need global graph reasoning. Adding GraphRAG without a demonstrated relational requirement would increase complexity without necessarily improving our target metrics.”

### “How do you know the RAG is accurate?”

> “We maintain a manually reviewed golden dataset and evaluate retrieval with Recall@K, Precision@K, MRR and nDCG. Generation is evaluated using faithfulness, answer relevance, factual correctness, source support and a dedicated safety evaluation. We also run ablation tests to prove whether each retrieval component actually improves the system.”

---

# 54. Final RAG Architecture

```text
                         USER
                           │
                           ▼
                    TEXT / VOICE
                           │
                           ▼
                        FASTAPI
                           │
                           ▼
                   AI ORCHESTRATOR
                           │
                           ▼
                  QUERY UNDERSTANDING
                           │
            ┌──────────────┼───────────────┐
            ▼              ▼               ▼
          Intent         Region          Language
            │              │               │
            └──────────────┼───────────────┘
                           ▼
                    RETRIEVAL QUERY
                           │
                           ▼
                    METADATA FILTER
                           │
                 ┌─────────┴─────────┐
                 ▼                   ▼
               BM25               VECTOR
                 │                   │
                 └─────────┬─────────┘
                           ▼
                         FUSION
                           ▼
                      TOP 30–50
                           ▼
                        RERANKER
                           ▼
                       TOP 5–10
                           ▼
                 AUTHORITY / SAFETY
                       VALIDATION
                           ▼
                    GROUNDED CONTEXT
                           ▼
                          GROQ
                           ▼
                   GROUNDED RESPONSE
                           │
                    ┌──────┴──────┐
                    ▼             ▼
                 SOURCES        SAFETY
                    │             │
                    └──────┬──────┘
                           ▼
                         USER
```

---

# 55. Final Research Checklist

## Knowledge
- [ ] Authoritative sources selected
- [ ] Accident guidance collected
- [ ] First-aid guidance collected
- [ ] Breakdown guidance collected
- [ ] Puncture guidance collected
- [ ] Vehicle-fire guidance collected
- [ ] Emergency numbers verified
- [ ] Region metadata added
- [ ] Language metadata added
- [ ] Verification dates recorded

## Retrieval
- [ ] Embedding model selected by benchmark
- [ ] Vector store selected
- [ ] BM25 selected
- [ ] Fusion method selected
- [ ] Reranker selected
- [ ] Metadata filters defined
- [ ] Chunk size tested
- [ ] Overlap tested
- [ ] Contextual chunking tested

## Generation
- [ ] LLM selected
- [ ] Grounding prompt built
- [ ] Structured output defined
- [ ] Source output defined
- [ ] No-answer behavior defined
- [ ] Safety rules defined

## Multilingual
- [ ] English tested
- [ ] Hindi tested
- [ ] Hinglish tested
- [ ] Cross-language retrieval tested

## Offline
- [ ] Gemma model selected
- [ ] Local embedding strategy selected
- [ ] Local vector index selected
- [ ] Local BM25 strategy selected
- [ ] Package size measured
- [ ] Offline latency measured

## Evaluation
- [ ] 50–100+ golden queries
- [ ] Recall@5/10/20
- [ ] Precision@5/10
- [ ] MRR
- [ ] nDCG
- [ ] Context Precision
- [ ] Context Recall
- [ ] Faithfulness
- [ ] Answer Relevancy
- [ ] Factual Correctness
- [ ] Citation support
- [ ] Safety pass rate
- [ ] P50/P95 latency
- [ ] Ablation tests

---

# 56. Engineering Principle

The RAAHAT RAG should not be judged by how sophisticated it sounds.

It should be judged by:

```text
Did we retrieve the right evidence?
            ↓
Did we rank it correctly?
            ↓
Did the LLM stay grounded?
            ↓
Did it answer the actual question?
            ↓
Was it safe?
            ↓
Could the user act on it?
```

The target architecture is therefore:

> **Retrieve the smallest amount of the most authoritative, relevant evidence needed to safely answer the user's situation.**
