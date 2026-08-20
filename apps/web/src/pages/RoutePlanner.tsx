import React, { useState } from 'react';
import { Navigation, ShieldCheck, AlertCircle, MapPin, ArrowRight } from 'lucide-react';
import { requestApi } from '../api/client';

export const RoutePlanner: React.FC = () => {
  const [destLat, setDestLat] = useState('22.9734');
  const [destLng, setDestLng] = useState('76.0508');
  const [route, setRoute] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handlePlanRoute = async () => {
    setLoading(true);
    try {
      const data = await requestApi<any>('/routes/plan', 'POST', {
        origin: { latitude: 22.7196, longitude: 75.8577 },
        destination: { latitude: parseFloat(destLat), longitude: parseFloat(destLng) },
        prefer_safe_corridors: true
      });
      setRoute(data);
    } catch (err) {
      console.error('Route calculation failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 8px 0' }}>
          Safe Emergency Route Corridor Planner
        </h2>
        <p style={{ color: '#94a3b8', margin: 0 }}>
          Generates optimized driving routes avoiding unlit or unsafe highway sections while highlighting emergency response points along your path.
        </p>
      </div>

      <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '16px', alignItems: 'center' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '6px' }}>Current Location (GPS)</label>
            <input type="text" disabled value="Indore City Center (22.7196, 75.8577)" style={{ width: '100%', boxSizing: 'border-box', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)', backgroundColor: 'rgba(15, 23, 42, 0.8)', color: '#cbd5e1' }} />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '6px' }}>Destination Coordinates (Lat, Lng)</label>
            <div style={{ display: 'flex', gap: '8px' }}>
              <input type="text" value={destLat} onChange={(e) => setDestLat(e.target.value)} placeholder="Latitude" style={{ width: '50%', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.2)', backgroundColor: 'rgba(15, 23, 42, 0.8)', color: 'white' }} />
              <input type="text" value={destLng} onChange={(e) => setDestLng(e.target.value)} placeholder="Longitude" style={{ width: '50%', padding: '12px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.2)', backgroundColor: 'rgba(15, 23, 42, 0.8)', color: 'white' }} />
            </div>
          </div>

          <button
            onClick={handlePlanRoute}
            disabled={loading}
            style={{
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              padding: '14px 24px',
              fontWeight: 700,
              cursor: 'pointer',
              marginTop: '22px'
            }}
          >
            {loading ? 'Calculating...' : 'PLAN ROUTE'}
          </button>
        </div>
      </div>

      {route && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <ShieldCheck size={22} color="#10b981" />
              <h3 style={{ margin: 0 }}>Route Safety Summary</h3>
            </div>
            <div style={{ display: 'flex', gap: '20px', marginBottom: '20px' }}>
              <div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>TOTAL DISTANCE</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f8fafc' }}>{route.total_distance_km} km</div>
              </div>
              <div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>ESTIMATED TIME</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#60a5fa' }}>{route.total_duration_minutes} mins</div>
              </div>
              <div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>SAFETY TIER</div>
                <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.2)', color: '#34d399', padding: '4px 10px', borderRadius: '6px', fontSize: '0.85rem', fontWeight: 700 }}>
                  {route.safety_tier}
                </span>
              </div>
            </div>

            <strong style={{ color: '#f8fafc', display: 'block', marginBottom: '10px' }}>Corridor Segments:</strong>
            {route.segments?.map((seg: any, idx: number) => (
              <div key={idx} style={{ backgroundColor: 'rgba(15, 23, 42, 0.6)', padding: '12px 16px', borderRadius: '8px', marginBottom: '8px', borderLeft: '3px solid #10b981' }}>
                <div style={{ fontWeight: 600, color: '#f1f5f9' }}>{seg.summary}</div>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>{seg.distance_km} km • ~{seg.duration_minutes} mins</div>
              </div>
            ))}
          </div>

          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <MapPin size={22} color="#f59e0b" />
              <h3 style={{ margin: 0 }}>Corridor Emergency Services</h3>
            </div>
            {route.nearby_emergency_services?.map((service: any) => (
              <div key={service.provider_id} style={{ backgroundColor: 'rgba(15, 23, 42, 0.6)', padding: '12px 16px', borderRadius: '8px', marginBottom: '10px' }}>
                <div style={{ fontWeight: 600, color: '#f8fafc' }}>{service.name}</div>
                <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>📞 {service.contact?.phone_primary || '112 Helpline'} • {service.distance_km} km away</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
