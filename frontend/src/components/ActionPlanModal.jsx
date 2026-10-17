import React, { useState } from 'react';
import { askCopilot } from '../services/api';

export default function ActionPlanModal({
  isOpen,
  onClose,
  plan,
  isLoadingPlan,
  issueId
}) {
  const [customQuestion, setCustomQuestion] = useState('');
  const [copilotAnswer, setCopilotAnswer] = useState(null);
  const [isAsking, setIsAsking] = useState(false);

  if (!isOpen) return null;

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!customQuestion.trim() || isAsking) return;

    setIsAsking(true);
    try {
      const resp = await askCopilot(issueId, customQuestion);
      setCopilotAnswer(resp);
    } catch (err) {
      console.error('Ask copilot error:', err);
    } finally {
      setIsAsking(false);
    }
  };

  const getSeverityBadge = (level) => {
    switch (level) {
      case 'CRITICAL': return 'badge-red';
      case 'HIGH': return 'badge-red';
      case 'MEDIUM': return 'badge-amber';
      case 'LOW': return 'badge-green';
      default: return 'badge-neutral';
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '16px', marginBottom: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span className="brand-icon" style={{ width: '20px', height: '20px', fontSize: '11px' }}>AI</span>
              <span className="font-baskerville" style={{ fontSize: '14px', fontWeight: 700, color: 'var(--accent-red)', letterSpacing: '0.5px' }}>
                TRADEFORENSICS COPILOT
              </span>
              {plan && (
                <span className={`badge ${getSeverityBadge(plan.severity_level)}`}>
                  {plan.severity_level} SEVERITY
                </span>
              )}
            </div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text-primary)' }}>
              Operational Remediation Plan
            </div>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              {plan ? plan.entity_name : `Analyzing ${issueId}...`}
            </div>
          </div>
          <button
            className="btn btn-secondary btn-sm"
            onClick={onClose}
            style={{ padding: '4px 10px' }}
          >
            ✕
          </button>
        </div>

        {isLoadingPlan ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '350px', gap: '14px' }}>
            <div className="spinner" style={{ width: '36px', height: '36px', borderTopColor: 'var(--accent-red)' }} />
            <div style={{ fontSize: '15px', fontWeight: 500, color: 'var(--text-primary)' }}>
              Synthesizing Evidence-Bounded Action Plan...
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              Querying Groq LLM (llama-3.3-70b-versatile) with strict anti-hallucination guardrails
            </div>
          </div>
        ) : plan ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
            {/* Executive Diagnosis */}
            <div style={{
              background: 'var(--bg-base)',
              border: '1px solid var(--border-card)',
              borderRadius: 'var(--radius-md)',
              padding: '16px 20px',
              borderLeft: '4px solid var(--accent-red)'
            }}>
              <div style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600, letterSpacing: '0.5px', marginBottom: '6px' }}>
                Executive Diagnosis
              </div>
              <div style={{ fontSize: '14px', color: 'var(--text-primary)', lineHeight: 1.6 }}>
                {plan.executive_summary}
              </div>
            </div>

            {/* Key Findings */}
            <div>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                Key Empirical Findings
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {plan.key_findings.map((kf, i) => (
                  <div key={i} style={{ display: 'flex', gap: '8px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                    <span style={{ color: 'var(--accent-red)' }}>•</span>
                    <span>{kf}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Prioritized Action Items */}
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Prioritized Operational Actions
                </div>
                <span className="badge badge-neutral">{plan.recommended_actions.length} Recommended Actions</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {plan.recommended_actions.map((act, i) => (
                  <div
                    key={i}
                    style={{
                      background: 'var(--bg-card)',
                      border: '1px solid var(--border-card)',
                      borderRadius: 'var(--radius-md)',
                      padding: '16px',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '8px'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{
                          width: '22px',
                          height: '22px',
                          borderRadius: '50%',
                          background: '#1f1f24',
                          color: 'var(--accent-red)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '11px',
                          fontWeight: 700,
                          fontFamily: 'var(--font-mono)'
                        }}>
                          #{act.priority}
                        </span>
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '14px' }}>
                          {act.title}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: '6px' }}>
                        <span className="badge badge-neutral" style={{ fontSize: '10px' }}>{act.category}</span>
                        <span className={`badge ${act.effort === 'LOW' ? 'badge-green' : act.effort === 'MEDIUM' ? 'badge-amber' : 'badge-red'}`} style={{ fontSize: '10px' }}>
                          {act.effort} EFFORT
                        </span>
                      </div>
                    </div>

                    <div style={{ fontSize: '13px', color: 'var(--text-primary)', lineHeight: 1.5 }}>
                      <strong>Action:</strong> {act.action}
                    </div>

                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)', background: 'var(--bg-base)', padding: '8px 10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                      <strong>Rationale:</strong> {act.rationale}
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', marginTop: '4px' }}>
                      <span><strong>Expected Effect:</strong> {act.expected_effect}</span>
                      <span><strong>Responsible:</strong> {act.responsible_team}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Interactive Ask Copilot Inquiry Section */}
            <div style={{
              background: 'var(--bg-base)',
              border: '1px solid var(--border-card)',
              borderRadius: 'var(--radius-md)',
              padding: '16px'
            }}>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '8px' }}>
                Ask Action Copilot
              </div>
              <form onSubmit={handleAsk} style={{ display: 'flex', gap: '8px' }}>
                <input
                  type="text"
                  className="input-field"
                  style={{ flex: 1 }}
                  placeholder="e.g., How can we reduce packaging transit damage for this seller?"
                  value={customQuestion}
                  onChange={(e) => setCustomQuestion(e.target.value)}
                  disabled={isAsking}
                />
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={!customQuestion.trim() || isAsking}
                >
                  {isAsking ? <span className="spinner" /> : 'Ask'}
                </button>
              </form>

              {copilotAnswer && (
                <div style={{ marginTop: '12px', padding: '12px', background: 'var(--bg-card)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)', fontSize: '13px' }}>
                  <div style={{ color: 'var(--text-primary)', lineHeight: 1.5, marginBottom: '8px' }}>
                    {copilotAnswer.answer}
                  </div>
                  {copilotAnswer.recommended_next_step && (
                    <div style={{ fontSize: '11px', color: '#34d399', fontWeight: 500 }}>
                      Next Step: {copilotAnswer.recommended_next_step}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Limitations Notice */}
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', textAlign: 'center', borderTop: '1px solid var(--border-subtle)', paddingTop: '12px' }}>
              {plan.data_limitations}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
