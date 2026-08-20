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
      <div style={{ minHeight: '100vh', backgroundColor: '#090d16', color: '#f8fafc' }}>
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main>
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'services' && <NearbyServices />}
          {activeTab === 'routes' && <RoutePlanner />}
          {activeTab === 'offline' && <OfflinePack />}
        </main>
      </div>
    </AuthProvider>
  );
};

export default App;
