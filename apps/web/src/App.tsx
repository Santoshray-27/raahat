import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Navbar } from './components/Navbar';
import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Signup } from './pages/Signup';
import { Dashboard } from './pages/Dashboard';
import { NearbyServices } from './pages/NearbyServices';
import { RoutePlanner } from './pages/RoutePlanner';
import { OfflinePack } from './pages/OfflinePack';
import Antigravity from './components/Antigravity';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        {/* Global particle cursor — fixed behind all pages */}
        <Antigravity
          count={300}
          magnetRadius={4}
          ringRadius={4.5}
          waveSpeed={0.4}
          waveAmplitude={0.8}
          particleSize={0.65}
          lerpSpeed={0.10}
          color="#1F4FD8"
          autoAnimate
          particleVariance={1}
          rotationSpeed={0}
          depthFactor={1}
          pulseSpeed={3}
          particleShape="capsule"
          fieldStrength={10}
        />
        <div style={{ position: 'relative', zIndex: 1, minHeight: '100vh', backgroundColor: 'transparent', color: '#0F172A', display: 'flex', flexDirection: 'column' }}>
          <Navbar />
          <main style={{ flex: 1 }}>
            <Routes>
              {/* Public Marketing Landing Page */}
              <Route path="/" element={<Landing />} />
              
              {/* Public Authentication Pages */}
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              
              {/* Protected App Routes */}
              <Route path="/app" element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/nearby" element={
                <ProtectedRoute>
                  <NearbyServices />
                </ProtectedRoute>
              } />
              <Route path="/route" element={
                <ProtectedRoute>
                  <RoutePlanner />
                </ProtectedRoute>
              } />
              <Route path="/offline" element={
                <ProtectedRoute>
                  <OfflinePack />
                </ProtectedRoute>
              } />

              {/* Catch-all redirect to Landing */}
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <footer style={{
            textAlign: 'center',
            padding: '20px 24px',
            borderTop: '1px solid #E2E8F0',
            backgroundColor: '#FFFFFF',
            color: '#94A3B8',
            fontSize: '0.8rem',
            fontWeight: 500
          }}>
            SquidHack 2026 · Team Solution Savvy · SW-17
          </footer>
        </div>
      </AuthProvider>
    </BrowserRouter>
  );
};

export default App;
