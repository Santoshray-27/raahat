import React, { useState, useEffect } from 'react';
import { Navigation, MapPin, Crosshair, ArrowRight } from 'lucide-react';
import { requestApi, RoutePlanResponse, ServiceProvider } from '../api/client';

export const RoutePlanner: React.FC = () => {
  const [originLat, setOriginLat] = useState('22.7196');
  const [originLng, setOriginLng] = useState('75.8577');
  const [destLat, setDestLat] = useState('23.2599');
  const [destLng, setDestLng] = useState('77.4126');
  const [route, setRoute] = useState<RoutePlanResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setOriginLat(pos.coords.latitude.toFixed(4));
          setOriginLng(pos.coords.longitude.toFixed(4));
        },
        () => {} // keep defaults
      );
    }
  }, []);

  const handlePlanRoute = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await requestApi<RoutePlanResponse>('/routes/plan', 'POST', {
        origin: { latitude: parseFloat(originLat), longitude: parseFloat(originLng) },
        destination: { latitude: parseFloat(destLat), longitude: parseFloat(destLng) },
        prefer_safe_corridors: true
      });
      setRoute(data);
    } catch (err: any) {
      setError(err.message || 'Route calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const safetyColor = (tier: string) => {
    if (tier === 'RECOMMENDED_SAFE') return { bg: '#F0FDF4', color: '#16A34A', border: '#BBF7D0' };
    if (tier === 'CAUTION_HAZARD') return { bg: '#FFFBEB', color: '#D97706', border: '#FDE68A' };
    return { bg: '#FEF2F2', color: '#EF4444', border: '#FECACA' };
  };

  return (
    <div className="container">
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800, margin: '0 0 6px 0', color: '#0F172A' }}>
          Route Planner
        </h1>
        <p style={{ color: '#64748B', margin: 0, fontSize: '0.92rem' }}>
          Plan optimized driving routes and locate emergency services along your path.
        </p>
      </div>

      {/* Route Input */}
      <div className="card" style={{ padding: '24px', marginBottom: '24px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr auto', gap: '16px', alignItems: 'end' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', color: '#64748B', marginBottom: '6px', fontWeight: 600 }}>
              <Crosshair size={12} style={{ marginRight: '4px' }} /> Origin
            </label>
            <div style={{ display: 'flex', gap: '6px' }}>
              <input className="input" value={originLat} onChange={(e) => setOriginLat(e.target.value)} placeholder="Lat" style={{ padding: '10px 12px' }} />
              <input className="input" value={originLng} onChange={(e) => setOriginLng(e.target.value)} placeholder="Lng" style={{ padding: '10px 12px' }} />
            </div>
          </div>

          <ArrowRight size={20} color="#94A3B8" style={{ marginBottom: '12px' }} />

          <div>
            <label style={{ display: 'block', fontSize: '0.82rem', color: '#64748B', marginBottom: '6px', fontWeight: 600 }}>
              <MapPin size={12} style={{ marginRight: '4px' }} /> Destination
            </label>
            <div style={{ display: 'flex', gap: '6px' }}>
              <input className="input" value={destLat} onChange={(e) => setDestLat(e.target.value)} placeholder="Lat" style={{ padding: '10px 12px' }} />
              <input className="input" value={destLng} onChange={(e) => setDestLng(e.target.value)} placeholder="Lng" style={{ padding: '10px 12px' }} />
            </div>
          </div>

          <button className="btn btn-primary" onClick={handlePlanRoute} disabled={loading} style={{ marginBottom: '1px' }}>
            {loading ? <><div className="spinner" style={{ width: 14, height: 14, borderWidth: 2, borderTopColor: 'white' }} /> Planning...</> : <><Navigation size={16} /> Plan Route</>}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="card" style={{ padding: '16px 20px', marginBottom: '20px', borderLeft: '4px solid #EF4444', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span style={{ color: '#DC2626', fontSize: '0.88rem' }}>{error}</span>
          <button className="btn btn-danger" onClick={handlePlanRoute} style={{ padding: '8px 16px', fontSize: '0.82rem' }}>Retry</button>
        </div>
      )}

      {/* Route Result */}
      {route && (() => {
        const sc = safetyColor(route.safety_tier || 'RECOMMENDED_SAFE');
        return (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div className="card" style={{ padding: '24px' }}>
              <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem', color: '#0F172A' }}>Route Summary</h3>

              <div style={{ display: 'flex', gap: '24px', marginBottom: '20px', flexWrap: 'wrap' }}>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Distance</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#0F172A' }}>{Number(route.total_distance_km).toFixed(1)} km</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Duration</div>
                  <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#2563EB' }}>{Number(route.total_duration_minutes).toFixed(0)} min</div>
                </div>
                <div>
                  <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Safety</div>
                  <span className="badge" style={{ backgroundColor: sc.bg, color: sc.color, border: `1px solid ${sc.border}`, fontSize: '0.78rem' }}>
                    {route.safety_tier || 'RECOMMENDED_SAFE'}
                  </span>
                </div>
              </div>

              {/* Provider Source */}
              <div style={{ fontSize: '0.8rem', color: '#64748B', marginBottom: '16px' }}>
                Provider: <strong style={{ color: '#2563EB' }}>{route.provider_source}</strong>
              </div>

              {/* Segments */}
              {route.segments?.length > 0 && (
                <>
                  <strong style={{ color: '#0F172A', display: 'block', marginBottom: '8px', fontSize: '0.9rem' }}>Segments:</strong>
                  {route.segments.map((seg, idx) => (
                    <div key={idx} style={{ backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', padding: '10px 14px', borderRadius: '8px', marginBottom: '6px', borderLeft: '3px solid #16A34A' }}>
                      <div style={{ fontWeight: 600, color: '#0F172A', fontSize: '0.88rem' }}>{seg.summary}</div>
                      <div style={{ fontSize: '0.8rem', color: '#64748B' }}>{seg.distance_km} km · ~{seg.duration_minutes} min</div>
                    </div>
                  ))}
                </>
              )}
            </div>

            {/* Corridor Services */}
            <div className="card" style={{ padding: '24px' }}>
              <h3 style={{ margin: '0 0 16px 0', fontSize: '1.1rem', color: '#0F172A' }}>Corridor Emergency Services</h3>
              {route.nearby_emergency_services?.length > 0 ? (
                route.nearby_emergency_services.map((service: ServiceProvider) => (
                  <div key={service.provider_id} style={{ backgroundColor: '#F8FAFC', border: '1px solid #E2E8F0', padding: '12px 14px', borderRadius: '10px', marginBottom: '10px' }}>
                    <div style={{ fontWeight: 600, color: '#0F172A', fontSize: '0.92rem' }}>{service.name}</div>
                    <div style={{ fontSize: '0.8rem', color: '#64748B', marginTop: '4px' }}>
                      📞 {service.contact?.phone_primary || 'No phone listed'} · {Number(service.distance_km).toFixed(1)} km away
                    </div>
                  </div>
                ))
              ) : (
                <p style={{ color: '#94A3B8', fontSize: '0.88rem' }}>No corridor services available for this route.</p>
              )}
            </div>
          </div>
        );
      })()}
    </div>
  );
};
