# RAAHAT — Implementation & Status Report

**Hackathon:** SquidHack 2026  
**Problem Statement:** SW-17 — AI-Powered Roadside Emergency & Assistance Navigator  
**Team:** Solution Savvy  
**Owner:** Santosh Ray (React Web + FastAPI Backend + Maps/Places/Routes + Fallback + Integration)

---

## 🚀 Executive Summary

All of Santosh's deliverables for **RAAHAT** have been completely built, integrated, and verified:
- **FastAPI Core Backend** running with Pydantic schemas, standard response envelopes `{success, data, meta, request_id}`, and CORS.
- **Mock-First Intelligence & Deterministic Classifier** covering English, Hindi, and Hinglish queries (*puncture, accident, bleeding/khoon, breakdown/kharab, fuel, stranded, fire*).
- **Automatic Provider Fallback System:** Google Places (New API) / Google Routes → OpenStreetMap Overpass / OSRM → Realistic Mock Fallback.
- **React Web App (Dark Emergency UX):** Built with Vite + TypeScript, featuring SOS Triage, Guidance Steps, Vendor Cards with `CALL` / `NAVIGATE` actions, Nearby Directory, Safe Route Corridor Planner, and Offline Pack Generator.
- **Server-Side Gemini AI Upgrade:** Gemini 1.5 Flash integrated server-side behind the classifier interface.
- **Firebase Auth Support:** `firebase-admin` Bearer token verification with dev bypass mode.
- **Offline Pack Generator:** JSON bundle generation with SHA-256 manifest verification for Flutter / Web offline usage.

---

## 🧪 Verification & Test Results

### 1. Backend Pytest Suite
- **Result:** **PASS (8/8 tests passed in 0.58s)**
- `test_emergency_puncture`: Verified Hindi/Hinglish puncture query, category mapping, guidance steps, vendor recommendation, and `availability_status="UNKNOWN"`.
- `test_emergency_accident_critical`: Verified severity escalation to `CRITICAL`, `is_life_threatening=True`, and 112 emergency dial action.
- `test_emergency_validation_error`: Verified 422 standard error envelope.
- `test_health_endpoint`: Verified `/api/v1/health`.
- `test_offline_pack_creation_and_download`: Verified SHA-256 checksum & JSON pack download endpoint.
- `test_routes_plan`: Verified safe corridor routing.
- `test_services_nearby` & `test_services_search_post`: Verified nearby directory search.

### 2. Frontend React Web Build
- **Result:** **PASS (`npx vite build` succeeded in 1.48s)**
- Bundle generated cleanly: `dist/index.html` (0.68 kB), `dist/assets/index.js` (244 kB).

---

## 🔒 Secrets & Environment Setup

Secrets extracted from `apikey.txt` have been securely stored in `backend/.env` and `backend/firebase-key.json`:
- `GOOGLE_PLACES_API_KEY`, `GOOGLE_ROUTES_API_KEY`, `GOOGLE_MAPS_JS_KEY`
- `GEMINI_API_KEY`
- `FIREBASE_CREDENTIALS_PATH`
- `.gitignore` configured to block `.env`, `firebase-key.json`, `node_modules`, `__pycache__`, `dist`.

---

## 🤝 Team Hand-off & Integration Points

### 1. For Satwik Misra (AI / RAG / Voice)
- **RAG Endpoint:** `POST /api/v1/rag/query` is ready. Pass your LangChain/Vector DB output here or set `AI_SERVICE_URL=http://localhost:8001` in `.env`.
- **Voice Endpoint:** `POST /api/v1/voice/assist` is stubbed and ready for Sarvam audio processing.

### 2. For Saanvi Gupta (Flutter Mobile App)
- **Directory:** `apps/mobile/` placeholder created with `README.md`.
- **API Contracts:** All REST endpoints strictly adhere to `contracts/04_RAAHAT_API_CONTRACTS_INTEGRATION_GUIDE.md`.
- **Offline Pack Download:** Download region packs with SHA-256 checksums from `GET /api/v1/offline-packs/{id}/download`.

---

## 🎬 2-Minute Golden Path Demo Script

1. **Start Backend & Frontend:**
   - Backend: `cd raahat/backend && uvicorn app.main:app --reload`
   - Frontend: `cd raahat/apps/web && npm run dev`
2. **Step 1 — Emergency SOS Triage:**
   - Open `http://localhost:5173`.
   - Click chip or type: *"Tyre puncture ho gaya hai highway par, urgent repair chahiye"*.
   - Click **TRIGGER SOS**. Show auto-detected `PUNCTURE` category, safety guidance steps, and recommended mechanics with `CALL` and `NAVIGATE` buttons.
3. **Step 2 — Life-Threatening Escalation:**
   - Type: *"Car accident near bypass, bleeding profusely"*.
   - Show `CRITICAL` severity badge, life-threatening alert, and 112 direct call action.
4. **Step 3 — Nearby Help & Directory:**
   - Click **Nearby Help** tab. Filter by category (Mechanic, Puncture, Hospital).
5. **Step 4 — Safe Corridor Route Planner:**
   - Click **Safe Routes** tab. Plan route to destination. View emergency coverage along the corridor.
6. **Step 5 — Offline Pack Generator:**
   - Click **Offline Packs** tab. Generate pack for "Indore Highway Corridor", show SHA-256 checksum, and click download JSON bundle.

---

## 🚀 Deployment Instructions

### Backend (Render / Railway / Docker)
- **Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Env Vars:** Copy contents of `backend/.env.example` into your host environment settings.

### Web Frontend (Vercel / Netlify)
- **Root Directory:** `apps/web`
- **Build Command:** `npm run build` or `npx vite build`
- **Output Directory:** `dist`
