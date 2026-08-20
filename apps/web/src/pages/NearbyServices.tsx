import React, { useState, useEffect } from 'react';
import { MapPin, Phone, Navigation, Wrench, Truck, Fuel, Building2, ShieldAlert } from 'lucide-react';
import { requestApi, ServiceProvider } from '../api/client';

export const NearbyServices: React.FC = () => {
  const [services, setServices] = useState<ServiceProvider[]>([]);
  const [loading, setLoading] = useState(true);
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
    try {
      const url = cat === 'ALL'
        ? '/services/nearby?lat=22.7196&lng=75.8577&radius_km=15'
        : `/services/nearby?lat=22.7196&lng=75.8577&radius_km=15&category=${cat}`;
      const data = await requestApi<{ services: ServiceProvider[] }>(url);
      setServices(data.services);
    } catch (err) {
      console.error('Failed to load services', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNearby(selectedCategory);
  }, [selectedCategory]);

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 8px 0' }}>
          Nearby Emergency Directory
        </h2>
        <p style={{ color: '#94a3b8', margin: 0 }}>
          Find verified mechanics, hospitals, towing cranes, and fuel delivery providers within your location radius.
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

      {loading ? (
        <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>Scanning emergency radar...</div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
          {services.map((service) => (
            <div key={service.provider_id} className="glass-card" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
                <h3 style={{ margin: 0, fontSize: '1.15rem' }}>{service.name}</h3>
                <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '4px 10px', borderRadius: '8px', fontWeight: 700, fontSize: '0.85rem' }}>
                  {service.rating ? `⭐ ${service.rating}` : 'Verified'}
                </span>
              </div>

              <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                <span className="badge-unknown">{service.availability_status}</span>
                <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>📍 {service.distance_km} km (~{service.eta_minutes} mins)</span>
              </div>

              <div style={{ fontSize: '0.85rem', color: '#cbd5e1', marginBottom: '20px', lineHeight: '1.4' }}>
                {service.address.formatted_address || 'Verified Highway Corridor Location'}
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
