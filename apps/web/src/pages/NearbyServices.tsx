import React, { useState, useEffect } from 'react';
import { MapPin, Phone, Navigation, Wrench, Truck, Fuel, Building2, ShieldAlert } from 'lucide-react';
import { requestApi, ServiceProvider } from '../api/client';

export const NearbyServices: React.FC = () => {
  const [services, setServices] = useState<ServiceProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');

  const categories = [
    { id: 'ALL', label: 'All Services', icon: MapPin },
    { id: 'MECHANIC', label: 'Mechanic', icon: Wrench },
    { id: 'PUNCTURE_REPAIR', label: 'Puncture', icon: Wrench },
    { id: 'TOWING', label: 'Towing', icon: Truck },
    { id: 'FUEL_DELIVERY', label: 'Fuel', icon: Fuel },
    { id: 'HOSPITAL', label: 'Hospitals', icon: Building2 },
  ];

  const fetchNearby = async (cat: string) => {
    setLoading(true);
    setError(null);
    try {
      const url = cat === 'ALL'
        ? '/services/nearby?lat=22.7196&lng=75.8577&radius_km=15'
        : `/services/nearby?lat=22.7196&lng=75.8577&radius_km=15&category=${cat}`;
      const data = await requestApi<{ services: ServiceProvider[] }>(url);
      setServices(data.services || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load live services');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNearby(selectedCategory);
  }, [selectedCategory]);

  const renderLiveBadge = (source?: string, timestamp?: string, isCached?: boolean) => {
    const s = source?.toUpperCase() || 'UNKNOWN';
    if (isCached || s === 'MOCK') {
      return (
        <span style={{ backgroundColor: 'rgba(239, 68, 68, 0.2)', color: '#fca5a5', border: '1px solid rgba(239, 68, 68, 0.4)', padding: '4px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700 }}>
          🔴 Cached
        </span>
      );
    }
    if (s === 'GOOGLE_PLACES' || s === 'GOOGLE_ROUTES') {
      return (
        <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)', padding: '4px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700 }}>
          🟢 LIVE · GOOGLE_PLACES {timestamp ? `· ${timestamp.substring(11, 19)}Z` : ''}
        </span>
      );
    }
    if (s === 'GEOAPIFY') {
      return (
        <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)', padding: '4px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700 }}>
          🟢 LIVE · GEOAPIFY {timestamp ? `· ${timestamp.substring(11, 19)}Z` : ''}
        </span>
      );
    }
    if (s === 'OSM_OVERPASS' || s === 'OSRM') {
      return (
        <span style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fcd34d', border: '1px solid rgba(245, 158, 11, 0.4)', padding: '4px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700 }}>
          🟡 Fallback · OSM_OVERPASS {timestamp ? `· ${timestamp.substring(11, 19)}Z` : ''}
        </span>
      );
    }
    return (
      <span style={{ backgroundColor: 'rgba(245, 158, 11, 0.2)', color: '#fcd34d', border: '1px solid rgba(245, 158, 11, 0.4)', padding: '4px 10px', borderRadius: '6px', fontSize: '0.75rem', fontWeight: 700 }}>
        🟡 Data · {s} {timestamp ? `· ${timestamp.substring(11, 19)}Z` : ''}
      </span>
    );
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 8px 0' }}>
          Nearby Emergency Directory
        </h2>
        <p style={{ color: '#94a3b8', margin: 0 }}>
          Real-time API directory of mechanics, hospitals, towing cranes, and fuel providers from Google Places.
        </p>
      </div>

      {/* Category Filter Chips */}
      <div style={{ display: 'flex', gap: '12px', overflowX: 'auto', paddingBottom: '12px', marginBottom: '28px' }}>
        {categories.map((cat) => {
          const Icon = cat.icon;
          const isSelected = selectedCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                borderRadius: '12px',
                border: '1px solid',
                borderColor: isSelected ? '#3b82f6' : 'rgba(255,255,255,0.1)',
                backgroundColor: isSelected ? 'rgba(59, 130, 246, 0.2)' : 'rgba(15, 23, 42, 0.6)',
                color: isSelected ? '#60a5fa' : '#94a3b8',
                fontWeight: 600,
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              <Icon size={16} />
              {cat.label}
            </button>
          );
        })}
      </div>

      {error && (
        <div style={{ padding: '20px 24px', backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '12px', color: '#fca5a5', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>{error}</span>
          <button onClick={() => fetchNearby(selectedCategory)} style={{ backgroundColor: '#ef4444', color: 'white', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: 700 }}>
            Retry
          </button>
        </div>
      )}

      {loading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Scanning Google Places API radar...</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
          {services.map((service) => (
            <div key={service.provider_id} className="glass-card" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <h3 style={{ margin: 0, fontSize: '1.15rem' }}>{service.name}</h3>
                <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '4px 10px', borderRadius: '8px', fontWeight: 700, fontSize: '0.85rem' }}>
                  {service.rating ? `⭐ ${service.rating}` : 'Verified'}
                </span>
              </div>

              <div style={{ marginBottom: '12px' }}>
                {renderLiveBadge(service.source, service.retrieved_at, service.is_cached)}
              </div>

              <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                <span className="badge-unknown">{service.availability_status}</span>
                <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>📍 {service.distance_km} km (~{service.eta_minutes} mins)</span>
              </div>

              <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '20px', lineHeight: '1.4' }}>
                {service.address.formatted_address || 'Google Places Verified Location'}
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                {service.contact.phone_primary && (
                  <a
                    href={`tel:${service.contact.phone_primary}`}
                    style={{
                      flex: 1,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '6px',
                      backgroundColor: '#10b981',
                      color: 'white',
                      padding: '10px',
                      borderRadius: '8px',
                      textDecoration: 'none',
                      fontWeight: 600,
                      fontSize: '0.88rem'
                    }}
                  >
                    <Phone size={14} />
                    CALL
                  </a>
                )}
                <a
                  href={`https://www.google.com/maps/search/?api=1&query=${service.location.latitude},${service.location.longitude}`}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '6px',
                    backgroundColor: 'rgba(59, 130, 246, 0.2)',
                    color: '#60a5fa',
                    border: '1px solid rgba(59, 130, 246, 0.4)',
                    padding: '10px',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    fontWeight: 600,
                    fontSize: '0.88rem'
                  }}
                >
                  <Navigation size={14} />
                  NAVIGATE
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
