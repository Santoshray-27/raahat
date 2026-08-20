import React, { useState } from 'react';
import { AuthProvider } from './auth/AuthContext';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { NearbyServices } from './pages/NearbyServices';
import { RoutePlanner } from './pages/RoutePlanner';
import { OfflinePack } from './pages/OfflinePack';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');

  return (
    <AuthProvider>
      <div style={{ minHeight: '100vh', backgroundColor: '#F7F9FC', color: '#0F172A', display: 'flex', flexDirection: 'column' }}>
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main style={{ flex: 1 }}>
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'services' && <NearbyServices />}
          {activeTab === 'routes' && <RoutePlanner />}
          {activeTab === 'offline' && <OfflinePack />}
        </main>
        <footer style={{
          textAlign: 'center',
          padding: '20px 24px',
          borderTop: '1px solid #E2E8F0',
          color: '#94A3B8',
          fontSize: '0.8rem',
          fontWeight: 500
        }}>
          SquidHack 2026 · Team Solution Savvy · SW-17
        </footer>
      </div>
    </AuthProvider>
  );
};

export default App;
