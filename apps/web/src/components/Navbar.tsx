import React from 'react';
import { ShieldAlert, MapPin, Navigation, Download, Wifi } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      borderBottom: '1px solid rgba(255,255,255,0.1)',
      backgroundColor: 'rgba(9, 13, 22, 0.95)',
      position: 'sticky',
      top: 0,
      zIndex: 50
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => setActiveTab('dashboard')}>
        <div style={{
          backgroundColor: '#ef4444',
          width: '38px',
          height: '38px',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px rgba(239, 68, 68, 0.5)'
        }}>
          <ShieldAlert size={22} color="white" />
        </div>
        <div>
          <span style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: '0.5px' }}>RAAHAT</span>
          <span style={{ fontSize: '0.75rem', display: 'block', color: '#94a3b8' }}>SquidHack SW-17 • AI Emergency Navigator</span>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        {[
          { id: 'dashboard', label: 'Emergency SOS', icon: ShieldAlert },
          { id: 'services', label: 'Nearby Help', icon: MapPin },
          { id: 'routes', label: 'Safe Routes', icon: Navigation },
          { id: 'offline', label: 'Offline Packs', icon: Download },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 18px',
                borderRadius: '10px',
                border: 'none',
                backgroundColor: isActive ? 'rgba(59, 130, 246, 0.2)' : 'transparent',
                color: isActive ? '#60a5fa' : '#94a3b8',
                fontWeight: isActive ? 600 : 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: '#10b981', backgroundColor: 'rgba(16, 185, 129, 0.1)', padding: '6px 14px', borderRadius: '9999px', border: '1px solid rgba(16, 185, 129, 0.3)' }}>
        <Wifi size={14} />
        <span>Core API Online</span>
      </div>
    </nav>
  );
};
