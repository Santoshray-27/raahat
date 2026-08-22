import React, { useState } from 'react';
import { Download, CheckCircle, Package } from 'lucide-react';
import { requestApi, getDownloadUrl, OfflinePackData } from '../api/client';

export const OfflinePack: React.FC = () => {
  const [region, setRegion] = useState('Indore Highway Corridor');
  const [selectedCategories, setSelectedCategories] = useState<string[]>(['AMBULANCE', 'POLICE', 'MECHANIC', 'PUNCTURE_REPAIR', 'HOSPITAL']);
  const [pack, setPack] = useState<OfflinePackData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [packs, setPacks] = useState<OfflinePackData[]>([]);

  const allCategories = ['AMBULANCE', 'POLICE', 'HOSPITAL', 'MECHANIC', 'PUNCTURE_REPAIR', 'TOWING', 'FUEL_DELIVERY', 'FIRE_BRIGADE'];

  const toggleCategory = (cat: string) => {
    setSelectedCategories(prev =>
      prev.includes(cat) ? prev.filter(c => c !== cat) : [...prev, cat]
    );
  };

  const handleGeneratePack = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await requestApi<OfflinePackData>('/offline-packs', 'POST', {
        region_name: region,
        route_id: 'demo_route_123',
        include_categories: selectedCategories
      });
      setPack(data);
      setPacks(prev => [data, ...prev]);
    } catch (err: any) {
      setError(err.message || 'Offline pack creation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800, margin: '0 0 6px 0', color: '#0F172A' }}>
          Offline Emergency Pack
        </h1>
        <p style={{ color: '#64748B', margin: 0, fontSize: '0.92rem' }}>
          Download offline data bundles containing emergency contacts and verified services for zero-connectivity situations.
        </p>
      </div>

      {/* Create Pack */}
      <div className="card" style={{ padding: '24px', marginBottom: '24px' }}>
        <h3 style={{ margin: '0 0 16px 0', fontSize: '1rem', color: '#0F172A' }}>Create New Pack</h3>

        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', fontSize: '0.82rem', color: '#64748B', marginBottom: '6px', fontWeight: 600 }}>Region Name</label>
          <input
            className="input"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
            placeholder="e.g. Indore Highway Corridor"
            style={{ maxWidth: '400px' }}
          />
        </div>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ display: 'block', fontSize: '0.82rem', color: '#64748B', marginBottom: '8px', fontWeight: 600 }}>Categories to Include</label>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            {allCategories.map(cat => (
              <button
                key={cat}
                className={selectedCategories.includes(cat) ? 'chip chip-active' : 'chip'}
                onClick={() => toggleCategory(cat)}
                style={{ fontSize: '0.8rem', padding: '6px 12px' }}
              >
                {cat.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        <button className="btn btn-success" onClick={handleGeneratePack} disabled={loading} style={{ gap: '8px' }}>
          {loading ? (
            <><div className="spinner" style={{ width: 14, height: 14, borderWidth: 2, borderTopColor: 'white' }} /> Generating...</>
          ) : (
            <><Package size={16} /> Generate Offline Pack</>
          )}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="card" style={{ padding: '16px 20px', marginBottom: '20px', borderLeft: '4px solid #EF4444' }}>
          <span style={{ color: '#DC2626', fontSize: '0.88rem' }}>{error}</span>
        </div>
      )}

      {/* Generated Pack Result */}
      {pack && (
        <div className="card" style={{ padding: '24px', marginBottom: '24px', borderLeft: '4px solid #16A34A' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <CheckCircle size={22} color="#16A34A" />
            <h3 style={{ margin: 0, fontSize: '1.05rem', color: '#0F172A' }}>Pack Ready</h3>
            <span className="badge badge-live" style={{ fontSize: '0.72rem' }}>SHA-256 Verified</span>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px', backgroundColor: '#F8FAFC', padding: '16px', borderRadius: '10px', border: '1px solid #E2E8F0' }}>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Pack ID</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0F172A' }}>{pack.manifest.pack_id}</div>
            </div>
            <div>
              <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>Providers</div>
              <div style={{ fontSize: '0.9rem', fontWeight: 700, color: '#0F172A' }}>{pack.manifest.total_providers} verified</div>
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <div style={{ fontSize: '0.75rem', color: '#64748B', fontWeight: 600, textTransform: 'uppercase', marginBottom: '2px' }}>SHA-256 Checksum</div>
              <code style={{ fontSize: '0.72rem', color: '#2563EB', wordBreak: 'break-all' }}>{pack.manifest.sha256_checksum}</code>
            </div>
          </div>

          <a
            href={getDownloadUrl(pack.manifest.pack_id)}
            target="_blank"
            rel="noreferrer"
            className="btn btn-primary"
            style={{ textDecoration: 'none' }}
          >
            <Download size={16} /> Download JSON Bundle
          </a>
        </div>
      )}

      {/* Pack History */}
      {packs.length > 1 && (
        <div>
          <h3 style={{ fontSize: '1rem', color: '#0F172A', marginBottom: '12px' }}>Previous Packs</h3>
          {packs.slice(1).map((p, idx) => (
            <div key={idx} className="card" style={{ padding: '14px 20px', marginBottom: '8px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <span style={{ fontWeight: 600, fontSize: '0.88rem', color: '#0F172A' }}>{p.manifest.pack_id}</span>
                <span style={{ fontSize: '0.78rem', color: '#64748B', marginLeft: '12px' }}>{p.manifest.total_providers} providers</span>
              </div>
              <a
                href={getDownloadUrl(p.manifest.pack_id)}
                target="_blank" rel="noreferrer"
                className="btn btn-outline" style={{ fontSize: '0.78rem', padding: '6px 12px' }}
              >
                <Download size={12} /> Download
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
