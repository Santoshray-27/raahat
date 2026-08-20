import React, { useState, useEffect } from 'react';
import { ShieldAlert, MapPin, Navigation, Download, Wifi, WifiOff, Menu, X } from 'lucide-react';
import { requestApi } from '../api/client';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const [apiOnline, setApiOnline] = useState<boolean | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await requestApi<any>('/health');
        setApiOnline(true);
      } catch {
        setApiOnline(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: 'dashboard', label: 'Emergency', icon: ShieldAlert },
    { id: 'services', label: 'Nearby Help', icon: MapPin },
    { id: 'routes', label: 'Route Planner', icon: Navigation },
    { id: 'offline', label: 'Offline Pack', icon: Download },
  ];

  return (
    <nav style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 32px',
      height: '64px',
      borderBottom: '1px solid #E2E8F0',
      backgroundColor: '#FFFFFF',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: '0 1px 3px rgba(15, 23, 42, 0.04)'
    }}>
      {/* Logo */}
      <div
        style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}
        onClick={() => { setActiveTab('dashboard'); setMobileOpen(false); }}
        role="button"
        aria-label="Go to home"
      >
        <div style={{
          backgroundColor: '#EF4444',
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}>
          <span style={{ fontSize: '1.2rem' }}>🚑</span>
        </div>
        <div>
          <span style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0F172A', letterSpacing: '0.3px' }}>RAAHAT</span>
          <span style={{ fontSize: '0.65rem', display: 'block', color: '#94A3B8', fontWeight: 500 }}>AI Emergency Navigator</span>
        </div>
      </div>

      {/* Desktop Nav */}
      <div style={{ display: 'flex', gap: '4px' }} className="nav-desktop">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              aria-label={tab.label}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 16px',
                borderRadius: '10px',
                border: 'none',
                backgroundColor: isActive ? '#EFF6FF' : 'transparent',
                color: isActive ? '#2563EB' : '#64748B',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.88rem',
                cursor: 'pointer',
                transition: 'all 150ms ease',
                fontFamily: 'inherit'
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Right side: status pill + mobile menu */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          fontSize: '0.78rem',
          fontWeight: 600,
          padding: '5px 12px',
          borderRadius: '9999px',
          border: '1px solid',
          borderColor: apiOnline ? '#BBF7D0' : apiOnline === false ? '#FECACA' : '#E2E8F0',
          backgroundColor: apiOnline ? '#F0FDF4' : apiOnline === false ? '#FEF2F2' : '#F8FAFC',
          color: apiOnline ? '#16A34A' : apiOnline === false ? '#EF4444' : '#94A3B8'
        }}>
          {apiOnline ? <Wifi size={12} /> : apiOnline === false ? <WifiOff size={12} /> : <div className="spinner" style={{ width: 12, height: 12, borderWidth: 2 }} />}
          {apiOnline ? 'LIVE' : apiOnline === false ? 'Offline' : '...'}
        </div>

        {/* Mobile hamburger */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle menu"
          style={{
            display: 'none',
            background: 'none',
            border: 'none',
            color: '#64748B',
            cursor: 'pointer',
            padding: '4px'
          }}
          className="nav-mobile-btn"
        >
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile dropdown - rendered but hidden via inline. Real hiding via CSS media query if needed. */}
      {mobileOpen && (
        <div style={{
          position: 'absolute',
          top: '64px',
          left: 0,
          right: 0,
          backgroundColor: '#FFFFFF',
          borderBottom: '1px solid #E2E8F0',
          padding: '8px 16px',
          boxShadow: '0 4px 12px rgba(15,23,42,0.08)',
          zIndex: 49
        }}>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setMobileOpen(false); }}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  width: '100%',
                  padding: '12px 16px',
                  borderRadius: '10px',
                  border: 'none',
                  backgroundColor: isActive ? '#EFF6FF' : 'transparent',
                  color: isActive ? '#2563EB' : '#475569',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: '0.95rem',
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                  textAlign: 'left'
                }}
              >
                <Icon size={18} />
                {tab.label}
              </button>
            );
          })}
        </div>
      )}
    </nav>
  );
};
