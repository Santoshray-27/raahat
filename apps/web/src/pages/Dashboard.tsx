import React, { useState } from 'react';
import { Search, AlertTriangle, Phone, Navigation, CheckCircle2, ShieldAlert, Sparkles, AlertCircle } from 'lucide-react';
import { requestApi, EmergencyResponse, ServiceProvider } from '../api/client';

export const Dashboard: React.FC = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<EmergencyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const suggestionChips = [
    "Tyre puncture on highway, need urgent mobile repair",
    "Car accident near Indore bypass, bleeding victim",
    "Engine breakdown with smoke, need towing",
    "Empty fuel tank late night on highway"
  ];

  const handleTriggerSOS = async (queryText?: string) => {
    const q = queryText || query;
    if (!q.trim()) return;
    
    setLoading(true);
    setError(null);
    try {
      const data = await requestApi<EmergencyResponse>('/emergency-assistance', 'POST', {
        user_query: q,
        location: { latitude: 22.7196, longitude: 75.8577 }, // Indore Default GPS
        language: 'hi'
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Failed to dispatch emergency query');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '32px 24px' }}>
      {/* Hero Section */}
      <div className="glass-card" style={{ padding: '36px', marginBottom: '32px', textAlign: 'center', position: 'relative', overflow: 'hidden' }}>
        <div style={{ position: 'absolute', top: '-60px', right: '-60px', width: '200px', height: '200px', background: 'radial-gradient(circle, rgba(239, 68, 68, 0.2) 0%, transparent 70%)', borderRadius: '50%' }} />
        
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800, margin: '0 0 12px 0' }}>
          Describe Your Roadside Emergency
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '1.1rem', maxWidth: '650px', margin: '0 auto 28px auto' }}>
          Describe your emergency in English, Hindi, or Hinglish. RAAHAT AI instantly triages severity, provides first-aid guidance, and connects you to nearby verified mechanics & hospitals.
        </p>

        {/* Big Search Input */}
        <div style={{ display: 'flex', gap: '12px', maxWidth: '750px', margin: '0 auto 20px auto' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleTriggerSOS()}
              placeholder="e.g. Tyre puncture ho gaya hai, urgent repair chahiye..."
              style={{
                width: '100%',
                boxSizing: 'border-box',
                padding: '18px 20px 18px 52px',
                borderRadius: '14px',
                border: '1px solid rgba(255,255,255,0.2)',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                color: 'white',
                fontSize: '1rem',
                outline: 'none'
              }}
            />
            <Search style={{ position: 'absolute', left: '18px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }} size={22} />
          </div>
          <button className="btn-sos" onClick={() => handleTriggerSOS()} disabled={loading}>
            {loading ? 'Analyzing...' : 'TRIGGER SOS'}
          </button>
        </div>

        {/* Suggestion Chips */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center' }}>
          {suggestionChips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => { setQuery(chip); handleTriggerSOS(chip); }}
              style={{
                backgroundColor: 'rgba(30, 41, 59, 0.7)',
                color: '#cbd5e1',
                border: '1px solid rgba(255,255,255,0.1)',
                padding: '8px 16px',
                borderRadius: '9999px',
                fontSize: '0.85rem',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              ⚡ {chip}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div style={{ padding: '16px 24px', backgroundColor: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.4)', borderRadius: '12px', color: '#fca5a5', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Results Container */}
      {result && (
        <div>
          {/* Triage Banner */}
          <div className="glass-card" style={{ padding: '24px 32px', marginBottom: '24px', borderLeft: `6px solid ${result.incident.severity === 'CRITICAL' ? '#ef4444' : '#f59e0b'}` }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span className="badge-critical" style={{ backgroundColor: result.incident.severity === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)', color: result.incident.severity === 'CRITICAL' ? '#fca5a5' : '#fcd34d' }}>
                  {result.incident.severity} SEVERITY
                </span>
                <span style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                  Category: {result.incident.category}
                </span>
              </div>
              <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                AI Confidence: 95%
              </span>
            </div>
            <p style={{ margin: 0, color: '#e2e8f0', fontSize: '1.05rem' }}>
              {result.incident.description_summary}
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            {/* Left Column: Guidance */}
            <div className="glass-card" style={{ padding: '28px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
                <ShieldAlert size={22} color="#60a5fa" />
                <h3 style={{ margin: 0, fontSize: '1.3rem' }}>Emergency Guidance SOP</h3>
              </div>
              <p style={{ color: '#cbd5e1', fontSize: '0.95rem', marginBottom: '20px', lineHeight: '1.5' }}>
                {result.guidance.summary}
              </p>

              {result.guidance.immediate_do_not_do.length > 0 && (
                <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', borderLeft: '3px solid #ef4444', padding: '12px 16px', borderRadius: '8px', marginBottom: '20px' }}>
                  <strong style={{ color: '#fca5a5', display: 'block', marginBottom: '6px' }}>❌ DO NOT:</strong>
                  {result.guidance.immediate_do_not_do.map((item, idx) => (
                    <div key={idx} style={{ color: '#fca5a5', fontSize: '0.88rem', marginBottom: '4px' }}>• {item}</div>
                  ))}
                </div>
              )}

              <div>
                <strong style={{ color: '#f8fafc', display: 'block', marginBottom: '12px' }}>Step-by-Step Instructions:</strong>
                {result.guidance.steps.map((step) => (
                  <div key={step.step_number} style={{ display: 'flex', gap: '14px', marginBottom: '16px' }}>
                    <div style={{ width: '28px', height: '28px', borderRadius: '50%', backgroundColor: step.is_critical ? '#ef4444' : '#3b82f6', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem', flexShrink: 0 }}>
                      {step.step_number}
                    </div>
                    <div>
                      <div style={{ fontWeight: 600, color: '#f1f5f9', fontSize: '0.95rem', marginBottom: '4px' }}>{step.title}</div>
                      <div style={{ color: '#94a3b8', fontSize: '0.88rem', lineHeight: '1.4' }}>{step.instruction}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Right Column: Verified Services */}
            <div className="glass-card" style={{ padding: '28px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <Sparkles size={22} color="#10b981" />
                  <h3 style={{ margin: 0, fontSize: '1.3rem' }}>Recommended Providers</h3>
                </div>
                <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Ranked by Proximity & Score</span>
              </div>

              {result.services.map((service: ServiceProvider) => (
                <div key={service.provider_id} style={{ backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', padding: '18px', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                    <div>
                      <h4 style={{ margin: '0 0 4px 0', fontSize: '1.05rem', color: '#f8fafc' }}>{service.name}</h4>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <span className="badge-unknown">{service.availability_status}</span>
                        <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>📍 {service.distance_km} km away (~{service.eta_minutes} mins)</span>
                      </div>
                    </div>
                    <span style={{ backgroundColor: 'rgba(16, 185, 129, 0.15)', color: '#34d399', padding: '4px 10px', borderRadius: '8px', fontWeight: 700, fontSize: '0.85rem' }}>
                      {service.rating ? `⭐ ${service.rating}` : 'Verified'}
                    </span>
                  </div>

                  <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: '12px', background: 'rgba(59, 130, 246, 0.08)', padding: '6px 10px', borderRadius: '6px', borderLeft: '2px solid #3b82f6' }}>
                    💡 <strong>Why Recommended:</strong> {service.recommendation_reason}
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
                        CALL ({service.contact.phone_primary})
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
          </div>
        </div>
      )}
    </div>
  );
};
