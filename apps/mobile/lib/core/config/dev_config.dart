// ============================================================
// DEVELOPMENT-ONLY CONFIGURATION — DO NOT SHIP TO PRODUCTION
// ============================================================
//
// Set [kDevelopmentUiBypass] to `true` to skip the backend
// `/users/me` synchronisation step in AuthGate.
//
// Use this ONLY when the RAAHAT backend is offline and you
// need to work on/test Flutter UI without a running server.
//
// When set to `false` (default for production), the full
// production flow is restored:
//   Firebase Auth → ID token → ApiClient → GET /users/me → MainNavigationShell
//
// TO RESTORE PRODUCTION BEHAVIOUR: set the flag to `false`.
// ============================================================

/// Development-only flag that bypasses the backend `/users/me`
/// synchronisation in [AuthGate].
///
const bool kDevelopmentUiBypass = false; // ← flip to false for production
