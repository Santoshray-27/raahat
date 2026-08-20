# RAAHAT — Project Report
## SquidHack 2026 · Team Solution Savvy · SW-17

---

## What Was Built

RAAHAT (**R**oadside **A**ssistance **A**nd **H**elp **A**nytime **T**ool) is a full-stack AI-powered roadside emergency assistance platform designed for Indian highways. It combines:

- **FastAPI Backend** with real-time data from Google Places/Routes API → Geoapify → OSM/OSRM fallback chain
- **Gemini AI** for incident severity classification (Hindi/English/Hinglish)
- **React + TypeScript Frontend** with premium light-theme UI
- **Offline Pack System** for zero-connectivity emergency data bundles
- **Firebase Auth** integration (dev-mode bypass for hackathon)

### Key Features
1. **Emergency SOS** — Describe any roadside situation → AI classifies severity, provides step-by-step guidance, and finds verified nearby services
2. **Nearby Help Directory** — Browse 8 categories of emergency services with real-time GPS
3. **Route Planner** — Plan driving routes with corridor emergency services
4. **Offline Emergency Packs** — Download data bundles with SHA-256 verified manifests
5. **Multi-Provider Fallback** — Google Places → Geoapify → OSM, never fails silently
6. **Telemetry Dashboard** — Real-time provider status, latency tracking, diagnostics

---

## Full Project Audit Results

### Backend (Checks 1–10)

| # | Check | Result | Details |
|---|-------|--------|---------|
| 1 | `pytest -v` (15 tests) | ✅ PASS | 15/15 passed in ~41s |
| 2 | `/health` → success:true, mode:live | ✅ PASS | mode=live, auth_disabled=true |
| 3 | Emergency puncture → LIVE source | ✅ PASS | source=GOOGLE_PLACES, type=PUNCTURE, severity=LOW |
| 4 | Accident+bleeding Hindi → CRITICAL | ✅ PASS | severity=CRITICAL |
| 5 | `/services/nearby` limit=3 | ✅ PASS | Exactly 3 services, source=GOOGLE_PLACES |
| 6 | `/routes/plan` Indore→Bhopal | ✅ PASS | 192.98 km, 235.4 min, provider=GOOGLE_ROUTES |
| 7 | `/offline-packs` creation | ✅ PASS | pack_id + SHA-256 checksum generated |
| 8 | `/providers/status` | ✅ PASS | google_places=OPERATIONAL, geoapify=OPERATIONAL |
| 9 | `/diagnostics` non-empty | ✅ PASS | 3+ entries with provider_source + latency |
| 10 | Git secrets check | ✅ PASS | No .env, firebase-key, apikey tracked |

### Frontend (Checks 11–14)

| # | Check | Result | Details |
|---|-------|--------|---------|
| 11 | `npm run build` | ✅ PASS | Clean compile, 189 KB JS bundle |
| 12 | Light theme confirmed | ✅ PASS | White backgrounds, dark text, no dark colors |
| 13 | All pages functional | ✅ PASS | Emergency, Nearby, Routes, Offline all render |
| 14 | grep mock/sample/dummy/fake | ✅ PASS | Zero matches in src/pages and src/components |

### Integration (Checks 15–16)

| # | Check | Result | Details |
|---|-------|--------|---------|
| 15 | All pages use API client | ✅ PASS | Every page imports from `../api/client`, no raw fetch |
| 16 | Golden path works | ✅ PASS | Puncture query → guidance + 3 LIVE services + CALL/NAVIGATE |

### **OVERALL VERDICT: ✅ PROJECT DONE**

---

## Architecture

```
┌─────────────────────────────────────────────┐
│  React Frontend (Vite + TypeScript)         │
│  apps/web/src/                              │
│  ├── api/client.ts (API layer)              │
│  ├── pages/ (Dashboard, Nearby, Routes...)  │
│  └── components/ (Navbar)                   │
└──────────────┬──────────────────────────────┘
               │ HTTP (localhost:8000)
┌──────────────▼──────────────────────────────┐
│  FastAPI Backend                             │
│  backend/app/                                │
│  ├── api/v1/ (routes, services, emergency)   │
│  ├── providers/ (google, geoapify, osm)      │
│  ├── services/ (gemini, ranking, offline)     │
│  └── core/ (config, telemetry, auth)          │
└──────────────┬──────────────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
 Google     Geoapify    OSM/OSRM
 Places     Places      Overpass
 Routes     Routing     Routing
```

---

## What Santosh Must Do Next

### Immediate (Before Demo)
1. **Start backend**: `cd backend && python -m uvicorn app.main:app --port 8000`
2. **Start frontend**: `cd apps/web && npm run dev`
3. **Test golden path**: Open browser → type a puncture scenario → verify LIVE badges

### Deployment
1. **Backend**: Deploy to Railway/Render/GCP Cloud Run
   - Set all `.env` variables as environment secrets
   - Never commit `.env` or `firebase-key.json`
2. **Frontend**: Deploy to Vercel/Netlify
   - Update `API_BASE_URL` in `apps/web/src/api/client.ts` to production URL
3. **Firebase**: Enable Firebase Auth in production (set `AUTH_DISABLED=false`)

### Team Handoff
- **Satwik & Saanvi**: Frontend sends `user_query` field (backend accepts both `user_query` and `message`)
- **API Contracts**: See `contracts/04_RAAHAT_API_CONTRACTS_INTEGRATION_GUIDE.md`
- **Provider Chain**: Google → Geoapify → OSM (automatic failover, no config needed)

### Future Enhancements (P1)
- Voice input (Mic button placeholder already in UI)
- Leaflet map integration for route visualization
- Push notifications for service ETAs
- Production Firebase auth flow

---

*Generated: August 20, 2026 · RAAHAT v1.0.0*
