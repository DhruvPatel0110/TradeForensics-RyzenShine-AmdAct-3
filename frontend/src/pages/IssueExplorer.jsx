import React, { useState } from 'react';

export default function IssueExplorer({
  issues,
  onSelectIssue,
  onOpenActionPlan
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [entityFilter, setEntityFilter] = useState('ALL');
  const [issueTypeFilter, setIssueTypeFilter] = useState('ALL');

  const filteredIssues = issues.filter((iss) => {
    // Entity filter
    if (entityFilter !== 'ALL' && iss.entity_type !== entityFilter) {
      return false;
    }
    // Issue type filter
    if (issueTypeFilter !== 'ALL' && !iss.issue_type.includes(issueTypeFilter)) {
      return false;
    }
    // Search filter
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      const nameMatch = iss.entity_name.toLowerCase().includes(term);
      const idMatch = iss.issue_id.toLowerCase().includes(term);
      const driverMatch = iss.primary_driver.toLowerCase().includes(term);
      if (!nameMatch && !idMatch && !driverMatch) return false;
    }
    return true;
  });

  return (
    <div>
      {/* Search & Filters Row */}
      <div className="card" style={{ marginBottom: '20px', padding: '16px 20px' }}>
        <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: '12px', flex: 1, minWidth: '280px' }}>
            <input
              type="text"
              className="input-field"
              style={{ width: '100%' }}
              placeholder="Search category, seller, location, or symptom..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <select
              className="select-field"
              value={entityFilter}
              onChange={(e) => setEntityFilter(e.target.value)}
            >
              <option value="ALL">All Entity Types</option>
              <option value="category">Categories Only</option>
              <option value="seller">Sellers Only</option>
            </select>

            <select
              className="select-field"
              value={issueTypeFilter}
              onChange={(e) => setIssueTypeFilter(e.target.value)}
            >
              <option value="ALL">All Issue Types</option>
              <option value="LOGISTICS">Logistics Bottlenecks</option>
              <option value="SATISFACTION">Satisfaction Drops</option>
            </select>
          </div>
        </div>
      </div>

      {/* Issues Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ width: '90px' }}>Severity</th>
              <th>Entity</th>
              <th>Issue Type</th>
              <th>Primary Symptom</th>
              <th>Negative Delta</th>
              <th>Late Delta</th>
              <th>Orders (N)</th>
              <th style={{ textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredIssues.length > 0 ? (
              filteredIssues.map((iss) => {
                const isCritical = iss.severity_score >= 40.0;
                const isHigh = iss.severity_score >= 20.0 && iss.severity_score < 40.0;
                const badgeClass = isCritical ? 'badge-red' : isHigh ? 'badge-amber' : 'badge-neutral';

                return (
                  <tr key={iss.issue_id}>
                    <td>
                      <span className={`badge ${badgeClass}`} style={{ fontSize: '12px' }}>
                        {iss.severity_score}
                      </span>
                    </td>
                    <td>
                      <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                        {iss.entity_name}
                      </div>
                      <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {iss.issue_id}
                      </div>
                    </td>
                    <td>
                      <span className="badge badge-neutral" style={{ fontSize: '11px' }}>
                        {iss.issue_type.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td style={{ fontSize: '12px', maxWidth: '300px' }}>
                      {iss.primary_driver}
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#f87171' }}>
                        +{iss.metrics.low_score_delta}%
                      </span>
                    </td>
                    <td>
                      <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: iss.metrics.late_rate_delta > 0 ? '#fbbf24' : 'var(--text-muted)' }}>
                        +{iss.metrics.late_rate_delta}%
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                      {iss.metrics.total_orders.toLocaleString()} ({iss.metrics.sample_size})
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', gap: '8px' }}>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => onSelectIssue(iss.issue_id)}
                        >
                          Evidence
                        </button>
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => onOpenActionPlan(iss.issue_id)}
                        >
                          AI Plan
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                  No operational issues match the selected filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '12px', textAlign: 'right' }}>
        Showing {filteredIssues.length} of {issues.length} detected friction points ranked by mathematical severity score
      </div>
    </div>
  );
}
