import React, { useState } from 'react';
import { Download, ShieldAlert, CheckCircle, FileText, Lock } from 'lucide-react';
import { requestApi } from '../api/client';

export const OfflinePack: React.FC = () => {
  const [region, setRegion] = useState('Indore Highway Corridor');
  const [pack, setPack] = useState<any | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGeneratePack = async () => {
    setLoading(true);
    try {
      const data = await requestApi<any>('/offline-packs', 'POST', {
        region_name: region,
        route_id: "demo_route_123",
        include_categories: ['AMBULANCE', 'POLICE', 'MECHANIC', 'PUNCTURE_REPAIR', 'HOSPITAL']
      });
      setPack(data);
    } catch (err) {
      console.error('Offline pack creation failed', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto', padding: '32px 24px' }}>
      <div style={{ marginBottom: '28px' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 800, margin: '0 0 8px 0' }}>
          Offline Region Emergency Pack Generator
        </h2>
        <p style={{ color: '#94a3b8', margin: 0 }}>
          Download offline region data bundles containing emergency contacts, verified mechanics, hospitals, and SHA256 verified manifests for zero-connectivity situations.
        </p>
      </div>

      <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <div style={{ flex: 1 }}>
            <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '6px' }}>Target Region Name</label>
            <input
              type="text"
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              placeholder="e.g. Indore Highway Corridor"
              style={{ width: '100%', boxSizing: 'border-box', padding: '14px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.2)', backgroundColor: 'rgba(15, 23, 42, 0.8)', color: 'white' }}
            />
          </div>
          <button
            onClick={handleGeneratePack}
            disabled={loading}
            style={{
              backgroundColor: '#10b981',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              padding: '14px 24px',
              fontWeight: 700,
              cursor: 'pointer',
              marginTop: '22px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            <Download size={18} />
            {loading ? 'GENERATING PACK...' : 'GENERATE OFFLINE PACK'}
          </button>
        </div>
      </div>

      {pack && (
        <div className="glass-card" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <CheckCircle size={24} color="#10b981" />
              <h3 style={{ margin: 0 }}>Offline Pack Ready: {pack.manifest.pack_id}</h3>
            </div>
            <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '4px 12px', borderRadius: '8px', fontWeight: 600, fontSize: '0.85rem' }}>
              SHA-256 Verified
            </span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '24px', backgroundColor: 'rgba(15, 23, 42, 0.6)', padding: '18px', borderRadius: '12px' }}>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>TOTAL SERVICE PROVIDERS</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc' }}>{pack.manifest.total_providers} Verified Vendors</div>
            </div>
            <div>
              <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>FILE CHECKSUM (SHA-256)</div>
              <div style={{ fontSize: '0.78rem', color: '#60a5fa', fontFamily: 'monospace', wordBreak: 'break-all' }}>{pack.manifest.sha256_checksum}</div>
            </div>
          </div>

          <a
            href={`http://localhost:8000/api/v1/offline-packs/${pack.manifest.pack_id}/download`}
            target="_blank"
            rel="noreferrer"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              backgroundColor: '#3b82f6',
              color: 'white',
              padding: '12px 24px',
              borderRadius: '10px',
              textDecoration: 'none',
              fontWeight: 700
            }}
          >
            <Download size={18} />
            DOWNLOAD JSON BUNDLE FOR FLUTTER / WEB
          </a>
        </div>
      )}
    </div>
  );
};
