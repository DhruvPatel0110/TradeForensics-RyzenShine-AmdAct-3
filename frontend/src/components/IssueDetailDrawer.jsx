import React from 'react';

export default function IssueDetailDrawer({
  isOpen,
  onClose,
  evidence,
  isLoadingEvidence,
  onOpenActionPlan
}) {
  if (!isOpen) return null;

  return (
    <div className="drawer-backdrop" onClick={onClose}>
      <div className="drawer-panel" onClick={(e) => e.stopPropagation()}>
        {/* Drawer Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="badge badge-red">{evidence?.issue_type || 'DIAGNOSIS'}</span>
              <span style={{ fontSize: '12px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                {evidence?.issue_id}
              </span>
            </div>
            <div style={{ fontSize: '20px', fontWeight: 600, color: 'var(--text-primary)' }}>
              {evidence?.entity_name || 'Loading issue...'}
            </div>
          </div>
          <button
            className="btn btn-secondary btn-sm"
            onClick={onClose}
            style={{ padding: '4px 8px' }}
          >
            ✕
          </button>
        </div>

        {isLoadingEvidence ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px', gap: '12px' }}>
            <div className="spinner" style={{ width: '28px', height: '28px', borderTopColor: 'var(--accent-red)' }} />
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>Fusing SQL KPIs, Tabular ML, and ChromaDB Quotes...</div>
          </div>
        ) : evidence ? (
          <>
            {/* Primary Driver & Severity Card */}
            <div style={{
              background: 'var(--bg-base)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '16px',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <div>
                <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.5px' }}>
                  Primary Symptom
                </div>
                <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--text-primary)', marginTop: '4px' }}>
                  {evidence.primary_driver}
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.5px' }}>
                  Severity Score
                </div>
                <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--font-mono)', color: 'var(--accent-red)' }}>
                  {evidence.severity_score}
                </div>
              </div>
            </div>

            {/* Deterministic Metrics Comparison Grid */}
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '10px' }}>
                Deterministic Metrics vs Baseline
              </div>
              <div className="grid-2" style={{ marginBottom: '0', gap: '10px' }}>
                <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-card)', borderRadius: 'var(--radius-sm)', padding: '12px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>LOW SCORE RATE (≤2★)</div>
                  <div style={{ fontSize: '18px', fontWeight: 600, fontFamily: 'var(--font-mono)', color: '#f87171', marginTop: '2px' }}>
                    {evidence.deterministic_kpis.low_score_rate_pct}%
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    Store: {evidence.deterministic_kpis.store_baseline_low_score_pct}% (+{evidence.deterministic_kpis.low_score_delta}%)
                  </div>
                </div>

                <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-card)', borderRadius: 'var(--radius-sm)', padding: '12px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>LATE SHIPMENT RATE</div>
                  <div style={{ fontSize: '18px', fontWeight: 600, fontFamily: 'var(--font-mono)', color: '#fbbf24', marginTop: '2px' }}>
                    {evidence.deterministic_kpis.late_delivery_rate_pct}%
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    Store: {evidence.deterministic_kpis.store_baseline_late_rate_pct}% (+{evidence.deterministic_kpis.late_rate_delta}%)
                  </div>
                </div>

                <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-card)', borderRadius: 'var(--radius-sm)', padding: '12px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>AVG DELAY ON LATE ORDERS</div>
                  <div style={{ fontSize: '18px', fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', marginTop: '2px' }}>
                    {evidence.deterministic_kpis.avg_delay_days} days
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    Past carrier promised deadline
                  </div>
                </div>

                <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-card)', borderRadius: 'var(--radius-sm)', padding: '12px' }}>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>EVALUATION SAMPLE (N)</div>
                  <div style={{ fontSize: '18px', fontWeight: 600, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', marginTop: '2px' }}>
                    {evidence.deterministic_kpis.sample_size.toLocaleString()}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                    From {evidence.deterministic_kpis.total_orders.toLocaleString()} total orders
                  </div>
                </div>
              </div>
            </div>

            {/* Tabular ML Risk & Drivers */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  LightGBM Segment Risk & Driver Attribution
                </div>
                <span className="badge badge-red">
                  {evidence.ml_risk_assessment.predicted_risk_pct}% Predicted Risk
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', background: 'var(--bg-card)', padding: '14px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-card)' }}>
                {evidence.ml_risk_assessment.top_drivers.map((d, i) => (
                  <div key={i} style={{ fontSize: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '3px' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>{d.display_name}</span>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--accent-red)' }}>
                        {d.importance_pct}%
                      </span>
                    </div>
                    <div style={{ height: '6px', background: '#1e1e24', borderRadius: '3px', overflow: 'hidden' }}>
                      <div style={{ width: `${d.importance_pct}%`, height: '100%', background: 'var(--accent-red)', borderRadius: '3px' }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Authentic Customer Complaint Quotes (ChromaDB) */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Authentic Customer Voice (ChromaDB RAG)
                </div>
                <span className="badge badge-neutral">Semantic Search</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {evidence.qualitative_quotes.length > 0 ? (
                  evidence.qualitative_quotes.map((q, i) => (
                    <div
                      key={i}
                      style={{
                        background: 'var(--bg-card)',
                        border: '1px solid var(--border-card)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '12px',
                        fontSize: '12px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                          <span style={{ color: '#ef4444', fontWeight: 600 }}>{q.review_score}★</span>
                          <span className="badge badge-neutral" style={{ fontSize: '10px' }}>{q.complaint_topic}</span>
                          {q.delay_days > 0 && (
                            <span style={{ color: 'var(--text-muted)', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                              +{q.delay_days}d delay
                            </span>
                          )}
                        </div>
                        <span style={{ fontSize: '10px', fontFamily: 'var(--font-mono)', color: 'var(--text-muted)' }}>
                          Sim: {q.similarity_score}
                        </span>
                      </div>
                      <div style={{ color: 'var(--text-primary)', fontStyle: 'italic', lineHeight: 1.4 }}>
                        "{q.review_snippet}"
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ color: 'var(--text-muted)', fontSize: '12px', fontStyle: 'italic' }}>
                    No direct text complaints in index for this entity.
                  </div>
                )}
              </div>
            </div>

            {/* CTA Button to Trigger Copilot Action Plan */}
            <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid var(--border-subtle)' }}>
              <button
                className="btn btn-primary"
                style={{ width: '100%', padding: '12px', fontSize: '14px' }}
                onClick={() => onOpenActionPlan(evidence.issue_id)}
              >
                Generate Grounded AI Action Plan &rarr;
              </button>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}
