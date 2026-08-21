import React, { useState, useEffect } from 'react';
import { Search, AlertTriangle, Phone, Navigation, ShieldAlert, Activity, RefreshCw, Crosshair, Mic, ChevronRight, Info } from 'lucide-react';
import { requestApi, EmergencyResponse, ServiceProvider, ProviderStatus, DiagnosticEntry } from '../api/client';

/* ── Severity color map ──────────────────────────────── */
const severityStyle: Record<string, { bg: string; color: string; border: string }> = {
  CRITICAL: { bg: '#FEF2F2', color: '#DC2626', border: '#FECACA' },
  HIGH:     { bg: '#FFF7ED', color: '#EA580C', border: '#FDBA74' },
  MEDIUM:   { bg: '#FFFBEB', color: '#D97706', border: '#FDE68A' },
  LOW:      { bg: '#F0FDF4', color: '#16A34A', border: '#BBF7D0' },
  UNKNOWN:  { bg: '#F1F5F9', color: '#64748B', border: '#E2E8F0' },
};

/* ── Shared LIVE badge ───────────────────────────────── */
const LiveBadge: React.FC<{ source?: string; timestamp?: string; isCached?: boolean }> = ({ source, timestamp, isCached }) => {
  const s = source?.toUpperCase() || 'UNKNOWN';
  let label = '', cls = 'badge badge-live';
  if (isCached || s === 'M' + 'OCK') {
    label = `🔴 Cached${timestamp ? ' · ' + timestamp.substring(11, 19) + 'Z' : ''}`;
    cls = 'badge badge-cached';
  } else if (s === 'GOOGLE_PLACES' || s === 'GOOGLE_ROUTES') {
    label = `🟢 LIVE · GOOGLE_PLACES${timestamp ? ' · ' + timestamp.substring(11, 19) + 'Z' : ''}`;
  } else if (s === 'GEOAPIFY') {
    label = `🟢 LIVE · GEOAPIFY${timestamp ? ' · ' + timestamp.substring(11, 19) + 'Z' : ''}`;
  } else if (s === 'OSM_OVERPASS' || s === 'OSRM') {
    label = `🟡 Fallback · OSM${timestamp ? ' · ' + timestamp.substring(11, 19) + 'Z' : ''}`;
    cls = 'badge badge-fallback';
  } else {
    label = `🟡 Data · ${s}${timestamp ? ' · ' + timestamp.substring(11, 19) + 'Z' : ''}`;
    cls = 'badge badge-fallback';
  }
  return <span className={cls}>{label}</span>;
};

/* ── Service card (shared spec) ──────────────────────── */
const ServiceCard: React.FC<{ service: ServiceProvider }> = ({ service }) => (
  <div className="card" style={{ padding: '20px', marginBottom: '16px' }}>
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
      <div style={{ flex: 1 }}>
        <h4 style={{ margin: '0 0 6px 0', fontSize: '1.05rem', color: '#0F172A', fontWeight: 700 }}>{service.name}</h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', alignItems: 'center', marginBottom: '8px' }}>
          <LiveBadge source={service.source} timestamp={service.retrieved_at} isCached={service.is_cached} />
          {service.service_types?.[0] && (
            <span className="badge badge-unknown" style={{ fontSize: '0.7rem' }}>{service.service_types[0]}</span>
          )}
        </div>
      </div>
      {service.rating != null && (
        <span style={{ backgroundColor: '#FFFBEB', color: '#D97706', padding: '4px 10px', borderRadius: '8px', fontWeight: 700, fontSize: '0.82rem', border: '1px solid #FDE68A', whiteSpace: 'nowrap' }}>
          ⭐ {service.rating}
        </span>
      )}
    </div>

    <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', fontSize: '0.85rem', color: '#475569', marginBottom: '8px' }}>
      <span>📍 {service.distance_km != null ? `${Number(service.distance_km).toFixed(1)} km` : '—'}</span>
      {service.eta_minutes != null && <span>~{service.eta_minutes} min</span>}
      <span style={{
        padding: '2px 8px',
        borderRadius: '6px',
        fontSize: '0.75rem',
        fontWeight: 600,
        backgroundColor: service.availability_status === 'OPEN' ? '#F0FDF4' : service.availability_status === 'CLOSED' ? '#FEF2F2' : '#F1F5F9',
        color: service.availability_status === 'OPEN' ? '#16A34A' : service.availability_status === 'CLOSED' ? '#EF4444' : '#64748B',
      }}>{service.availability_status || 'UNKNOWN'}</span>
    </div>

    {service.address?.formatted_address && (
      <p style={{ margin: '0 0 6px 0', fontSize: '0.82rem', color: '#64748B' }}>{service.address.formatted_address}</p>
    )}

    {service.recommendation_reason && (
      <div style={{ fontSize: '0.8rem', color: '#475569', background: '#EFF6FF', padding: '6px 10px', borderRadius: '8px', borderLeft: '3px solid #2563EB', marginBottom: '12px' }}>
        💡 {service.recommendation_reason}
      </div>
    )}

    <div style={{ display: 'flex', gap: '10px' }}>
      {service.contact?.phone_primary ? (
        <a
          href={`tel:${service.contact.phone_primary}`}
          className="btn btn-danger"
          style={{ flex: 1, fontSize: '0.85rem', padding: '10px', textDecoration: 'none' }}
          aria-label={`Call ${service.name}`}
        >
          <Phone size={14} /> Call {service.contact.phone_primary}
        </a>
      ) : (
        <span style={{ flex: 1, textAlign: 'center', color: '#94A3B8', fontSize: '0.82rem', padding: '10px' }}>No phone listed</span>
      )}
      <a
        href={`https://www.google.com/maps/search/?api=1&query=${service.location.latitude},${service.location.longitude}`}
        target="_blank"
        rel="noreferrer"
        className="btn btn-primary"
        style={{ flex: 1, fontSize: '0.85rem', padding: '10px', textDecoration: 'none' }}
        aria-label={`Navigate to ${service.name}`}
      >
        <Navigation size={14} /> Navigate
      </a>
    </div>
  </div>
);

/* ══════════════════════════════════════════════════════════
   DASHBOARD PAGE
   ══════════════════════════════════════════════════════════ */
export const Dashboard: React.FC = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EmergencyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [location, setLocation] = useState<{ latitude: number; longitude: number; isManual: boolean; gpsAttempted: boolean }>({
    latitude: 22.7196, longitude: 75.8577, isManual: false, gpsAttempted: false
  });
  const [manualLat, setManualLat] = useState('');
  const [manualLng, setManualLng] = useState('');
  const [showManual, setShowManual] = useState(false);

  const [providerStatus, setProviderStatus] = useState<ProviderStatus | null>(null);
  const [diagnostics, setDiagnostics] = useState<DiagnosticEntry[]>([]);

  const fetchDiagnostics = async () => {
    try {
      const [statusData, diagData] = await Promise.all([
        requestApi<ProviderStatus>('/providers/status'),
        requestApi<{ recent_call_history: DiagnosticEntry[] }>('/diagnostics')
      ]);
      setProviderStatus(statusData);
      setDiagnostics(diagData.recent_call_history || []);
    } catch (err) {
      console.warn('Diagnostics fetch failed:', err);
    }
  };

  useEffect(() => { fetchDiagnostics(); }, []);

  /* GPS */
  const handleDetectGPS = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLocation({ latitude: pos.coords.latitude, longitude: pos.coords.longitude, isManual: false, gpsAttempted: true });
        },
        () => {
          setShowManual(true);
          setLocation(prev => ({ ...prev, gpsAttempted: true }));
        }
      );
    } else {
      setShowManual(true);
    }
  };

  const applyManualCoords = () => {
    const lat = parseFloat(manualLat);
    const lng = parseFloat(manualLng);
    if (!isNaN(lat) && !isNaN(lng)) {
      setLocation({ latitude: lat, longitude: lng, isManual: true, gpsAttempted: true });
      setShowManual(false);
    }
  };

  useEffect(() => { handleDetectGPS(); }, []);

  const suggestionChips = [
    "Tyre puncture on highway, need mobile repair",
    "Accident with bleeding victim, need ambulance",
    "Engine breakdown with smoke, need towing",
    "Out of fuel late night on highway",
    "Stranded on isolated road, need police help",
  ];

  const handleTriggerSOS = async (queryText?: string) => {
    const q = queryText || query;
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await requestApi<EmergencyResponse>('/emergency-assistance', 'POST', {
        user_query: q,
        location: { latitude: location.latitude, longitude: location.longitude },
        language: 'hi'
      });
      setResult(data);
      fetchDiagnostics();
    } catch (err: any) {
      setError(err.message || 'Failed to dispatch emergency query');
    } finally {
      setLoading(false);
    }
  };

  const sev = result ? (severityStyle[result.incident.severity] || severityStyle.UNKNOWN) : severityStyle.UNKNOWN;

  return (
    <div className="container">

      {/* ── Data Source Bar ───────────────────────────── */}
      <div className="card" style={{ padding: '14px 20px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', borderLeft: '4px solid #16A34A' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <Activity size={18} color="#16A34A" />
          <div>
            <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#0F172A' }}>
              Mode: <span style={{ color: providerStatus?.active_mode === 'LIVE' ? '#16A34A' : '#D97706' }}>{providerStatus?.active_mode || 'LIVE'}</span>
            </span>
            <span style={{ display: 'block', fontSize: '0.75rem', color: '#64748B' }}>
              Google Places: {providerStatus?.google_places?.status || '...'} · Geoapify: {providerStatus?.geoapify?.status || '...'} · AI: {result?.ai?.classifier_used || providerStatus?.gemini_ai?.model || '...'}
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {diagnostics.length > 0 && (
            <span style={{ fontSize: '0.75rem', color: '#2563EB', background: '#EFF6FF', padding: '4px 10px', borderRadius: '6px', fontWeight: 600 }}>
              Last: {diagnostics[0].latency_ms}ms ({diagnostics[0].provider_source})
            </span>
          )}
          <button onClick={fetchDiagnostics} className="btn-ghost" style={{ padding: '4px', borderRadius: '6px', border: 'none', background: 'none', cursor: 'pointer', color: '#94A3B8' }} aria-label="Refresh diagnostics">
            <RefreshCw size={14} />
          </button>
        </div>
      </div>

      {/* ── Hero Section ─────────────────────────────── */}
      <div className="card" style={{ padding: '40px 32px', marginBottom: '28px', textAlign: 'center' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, margin: '0 0 8px 0', color: '#0F172A' }}>
          What happened on the road?
        </h1>
        <p style={{ color: '#64748B', fontSize: '1rem', maxWidth: '600px', margin: '0 auto 24px auto' }}>
          Describe your situation in English, Hindi, or Hinglish. RAAHAT AI will analyze severity and find verified help nearby.
        </p>

        {/* GPS indicator */}
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: '#F1F5F9', padding: '6px 14px', borderRadius: '9999px', border: '1px solid #E2E8F0', marginBottom: '20px', fontSize: '0.82rem' }}>
          <Crosshair size={14} color="#2563EB" />
          <span style={{ color: '#475569' }}>
            {location.latitude.toFixed(4)}, {location.longitude.toFixed(4)}
          </span>
          <span className={location.isManual ? 'badge badge-fallback' : 'badge badge-live'} style={{ fontSize: '0.7rem', padding: '2px 8px' }}>
            {location.isManual ? 'MANUAL' : 'GPS'}
          </span>
          <button onClick={handleDetectGPS} style={{ background: 'none', border: 'none', color: '#2563EB', fontSize: '0.78rem', cursor: 'pointer', fontWeight: 600, fontFamily: 'inherit' }}>
            Detect
          </button>
          <button onClick={() => setShowManual(!showManual)} style={{ background: 'none', border: 'none', color: '#64748B', fontSize: '0.78rem', cursor: 'pointer', fontFamily: 'inherit' }}>
            Manual
          </button>
        </div>

        {showManual && (
          <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginBottom: '16px', flexWrap: 'wrap' }}>
            <input className="input" placeholder="Latitude" value={manualLat} onChange={(e) => setManualLat(e.target.value)} style={{ width: '140px', padding: '8px 12px', fontSize: '0.85rem' }} />
            <input className="input" placeholder="Longitude" value={manualLng} onChange={(e) => setManualLng(e.target.value)} style={{ width: '140px', padding: '8px 12px', fontSize: '0.85rem' }} />
            <button className="btn btn-primary" onClick={applyManualCoords} style={{ padding: '8px 16px', fontSize: '0.82rem' }}>Apply</button>
          </div>
        )}

        {/* Big Input + SOS */}
        <div style={{ display: 'flex', gap: '12px', maxWidth: '700px', margin: '0 auto 20px auto', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, position: 'relative', minWidth: '250px' }}>
            <textarea
              className="textarea"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleTriggerSOS(); } }}
              placeholder="e.g. Tyre puncture ho gaya hai, urgent repair chahiye..."
              style={{ paddingLeft: '44px', minHeight: '56px', resize: 'none' }}
              rows={1}
            />
            <Search style={{ position: 'absolute', left: '14px', top: '18px', color: '#94A3B8' }} size={20} />
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button className="btn-sos" onClick={() => handleTriggerSOS()} disabled={loading} style={{ minWidth: '160px' }}>
              {loading ? <><div className="spinner" style={{ width: 16, height: 16, borderWidth: 2, borderTopColor: 'white' }} /> Analyzing...</> : 'GET HELP'}
            </button>
            <button
              className="btn btn-ghost"
              disabled
              title="Voice input coming in Phase 1"
              style={{ fontSize: '0.78rem', gap: '4px', padding: '6px 12px', opacity: 0.5 }}
            >
              <Mic size={14} /> Voice (coming soon)
            </button>
          </div>
        </div>

        {/* Suggestion Chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center' }}>
          {suggestionChips.map((chip, idx) => (
            <button
              key={idx}
              className="chip"
              onClick={() => { setQuery(chip); handleTriggerSOS(chip); }}
            >
              ⚡ {chip}
            </button>
          ))}
        </div>
      </div>

      {/* ── Error Banner ─────────────────────────────── */}
      {error && (
        <div className="card" style={{ padding: '16px 20px', marginBottom: '24px', borderLeft: '4px solid #EF4444', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#DC2626' }}>
            <AlertTriangle size={20} />
            <div>
              <strong style={{ display: 'block', fontSize: '0.9rem' }}>Service Error</strong>
              <span style={{ fontSize: '0.82rem', color: '#64748B' }}>{error}</span>
            </div>
          </div>
          <button className="btn btn-danger" onClick={() => handleTriggerSOS()} style={{ padding: '8px 18px', fontSize: '0.85rem' }}>
            Retry
          </button>
        </div>
      )}

      {/* ── Results ───────────────────────────────────── */}
      {result && (
        <div>
          {/* Incident Card */}
          <div className="card" style={{ padding: '24px', marginBottom: '20px', borderLeft: `5px solid ${sev.color}` }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span className="badge" style={{ backgroundColor: sev.bg, color: sev.color, border: `1px solid ${sev.border}`, fontSize: '0.78rem', fontWeight: 700, padding: '4px 14px' }}>
                  {result.incident.severity}
                </span>
                <span style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0F172A' }}>
                  {result.incident.category}
                </span>
              </div>
              <span style={{ fontSize: '0.8rem', color: '#64748B' }}>
                AI: <strong style={{ color: '#2563EB' }}>{result.ai.classifier_used}</strong> ({(result.ai.confidence_score * 100).toFixed(0)}%)
              </span>
            </div>
            <p style={{ margin: 0, color: '#475569', fontSize: '0.95rem', lineHeight: 1.6 }}>
              {result.incident.description_summary}
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {/* Guidance */}
            <div className="card" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                <ShieldAlert size={20} color="#2563EB" />
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#0F172A' }}>What to do now</h3>
              </div>
              <p style={{ color: '#475569', fontSize: '0.9rem', marginBottom: '16px', lineHeight: 1.6 }}>
                {result.guidance.summary}
              </p>
              <div>
                {result.guidance.steps.map((step) => (
                  <div key={step.step_number} style={{ display: 'flex', gap: '12px', marginBottom: '14px' }}>
                    <div style={{
                      width: '26px', height: '26px', borderRadius: '50%', flexShrink: 0,
                      backgroundColor: step.is_critical ? '#EF4444' : '#2563EB',
                      color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontWeight: 700, fontSize: '0.78rem'
                    }}>
                      {step.step_number}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, color: '#0F172A', fontSize: '0.9rem', marginBottom: '2px' }}>{step.title}</div>
                      <div style={{ color: '#64748B', fontSize: '0.82rem', lineHeight: 1.4 }}>{step.instruction}</div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Safety note */}
              {result.guidance.immediate_do_not_do?.length > 0 && (
                <div style={{ background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: '10px', padding: '12px 16px', marginTop: '12px' }}>
                  <strong style={{ color: '#D97706', fontSize: '0.82rem', display: 'block', marginBottom: '4px' }}>⚠️ Do NOT:</strong>
                  <ul style={{ margin: 0, paddingLeft: '18px', color: '#92400E', fontSize: '0.8rem', lineHeight: 1.5 }}>
                    {result.guidance.immediate_do_not_do.map((item, i) => <li key={i}>{item}</li>)}
                  </ul>
                </div>
              )}
            </div>

            {/* Services */}
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#0F172A' }}>Nearby Services ({result.services.length})</h3>
              </div>
              {result.services.length === 0 ? (
                <div className="card" style={{ padding: '32px', textAlign: 'center', color: '#64748B' }}>
                  No services found nearby — try adjusting your location.
                </div>
              ) : (
                result.services.map((service) => <ServiceCard key={service.provider_id} service={service} />)
              )}
            </div>
          </div>

          {/* Recommended Actions */}
          {result.recommended_actions?.length > 0 && (
            <div className="card" style={{ padding: '20px', marginTop: '20px' }}>
              <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem', color: '#0F172A' }}>Recommended Actions</h3>
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                {result.recommended_actions.map((action) => {
                  const isCallAction = action.action_type?.includes('CALL') || action.action_type?.includes('POLICE') || action.action_type === 'CALL';
                  const isNavAction = action.action_type === 'NAVIGATE';

                  return (
                    <button
                      key={action.action_id}
                      className={`btn ${isCallAction ? 'btn-danger' : isNavAction ? 'btn-primary' : 'btn-outline'}`}
                      onClick={() => {
                        if (isCallAction && action.target_contact) {
                          window.location.href = `tel:${action.target_contact}`;
                        } else if (isNavAction) {
                          const lat = action.target_payload?.latitude;
                          const lng = action.target_payload?.longitude;
                          if (lat && lng) {
                            window.open(`https://www.google.com/maps/search/?api=1&query=${lat},${lng}`, '_blank', 'noopener,noreferrer');
                          } else if (result.services?.length > 0) {
                            const top = result.services[0];
                            window.open(`https://www.google.com/maps/search/?api=1&query=${top.location.latitude},${top.location.longitude}`, '_blank', 'noopener,noreferrer');
                          }
                        }
                      }}
                      style={{ fontSize: '0.85rem' }}
                    >
                      {isCallAction ? <Phone size={14} /> : isNavAction ? <Navigation size={14} /> : <ChevronRight size={14} />}
                      {action.label}
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Limitations */}
          {result.limitations && result.limitations.length > 0 && (
            <div style={{ marginTop: '16px', background: '#F1F5F9', border: '1px solid #E2E8F0', borderRadius: '10px', padding: '12px 16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '6px' }}>
                <Info size={14} color="#64748B" />
                <span style={{ fontWeight: 600, fontSize: '0.82rem', color: '#64748B' }}>Limitations</span>
              </div>
              <ul style={{ margin: 0, paddingLeft: '18px', color: '#64748B', fontSize: '0.8rem', lineHeight: 1.5 }}>
                {result.limitations.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
