import React, { useState, useMemo } from 'react';
import { IconSeller, IconAlert, IconTruck, IconClock, IconStar } from '../components/Icons';

export default function SellersView({
  sellers = [],
  onSelectIssue,
  onOpenActionPlan
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [stateFilter, setStateFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [issueTypeFilter, setIssueTypeFilter] = useState('ALL');

  // Compute unique states from sellers list
  const availableStates = useMemo(() => {
    const states = new Set();
    sellers.forEach((s) => {
      const match = s.entity_name?.match(/\/([A-Z]{2})\)/);
      if (match) states.add(match[1]);
    });
    return Array.from(states).sort();
  }, [sellers]);

  // Filtered sellers
  const filteredSellers = useMemo(() => {
    return sellers.filter((s) => {
      // Severity filter
      if (severityFilter !== 'ALL') {
        const sev = s.severity_score >= 40 ? 'HIGH' : s.severity_score >= 20 ? 'MEDIUM' : 'LOW';
        if (sev !== severityFilter) return false;
      }
      // State filter
      if (stateFilter !== 'ALL') {
        if (!s.entity_name?.includes(`/${stateFilter})`)) return false;
      }
      // Issue type filter
      if (issueTypeFilter !== 'ALL' && !s.issue_type.includes(issueTypeFilter)) {
        return false;
      }
      // Search term
      if (searchTerm.trim()) {
        const term = searchTerm.toLowerCase();
        const nameMatch = s.entity_name?.toLowerCase().includes(term);
        const idMatch = s.issue_id?.toLowerCase().includes(term);
        const driverMatch = s.primary_driver?.toLowerCase().includes(term);
        if (!nameMatch && !idMatch && !driverMatch) return false;
      }
      return true;
    });
  }, [sellers, severityFilter, stateFilter, issueTypeFilter, searchTerm]);

  // Compute summary stats
  const totalSellers = sellers.length;
  const avgLateRate = totalSellers > 0
    ? (sellers.reduce((acc, s) => acc + (s.metrics?.late_delivery_rate_pct || 0), 0) / totalSellers).toFixed(1)
    : '26.8';
  const peakDelta = totalSellers > 0
    ? Math.max(...sellers.map(s => s.metrics?.low_score_delta || 0)).toFixed(1)
    : '47.2';

  return (
    <div className="sellers-page-view" aria-label="Seller Forensics Dashboard">
      {/* Top Header & Context */}
      <div className="section-intro-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="kpi-icon-box icon-box-red" style={{ width: '32px', height: '32px' }}>
            <IconSeller size={17} color="#ef4444" />
          </div>
          <div>
            <h2 className="view-page-title">Marketplace Seller Forensics</h2>
            <p className="view-page-subtitle">
              Operational diagnostics and SLA breach analysis for merchant accounts across Brazilian distribution corridors
            </p>
          </div>
        </div>
        <span className="badge-model-red">Seller Entity Vector Store</span>
      </div>

      {/* 4 Quick Stat Cards */}
      <div className="kpi-cards-grid" style={{ marginBottom: '20px' }}>
        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box icon-box-red">
              <IconSeller size={15} color="#ef4444" />
            </div>
            <span className="kpi-label">Problem Sellers Monitored</span>
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value">{totalSellers}</span>
          </div>
          <div className="kpi-subtitle">Fulfillment accounts with high delta signals</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box icon-box-red">
              <IconTruck size={15} color="#ef4444" />
            </div>
            <span className="kpi-label">Average Seller Late Rate</span>
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value" style={{ color: '#f87171' }}>{avgLateRate}%</span>
          </div>
          <div className="kpi-subtitle">Global store baseline is 8.11%</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box icon-box-red">
              <IconStar size={15} color="#ef4444" />
            </div>
            <span className="kpi-label">Peak Dissatisfaction Spike</span>
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value" style={{ color: '#f87171' }}>+{peakDelta}%</span>
          </div>
          <div className="kpi-subtitle">Highest recorded negative review delta</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box icon-box-teal">
              <IconClock size={15} color="#2dd4bf" />
            </div>
            <span className="kpi-label">Primary Bottleneck Corridors</span>
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value val-teal" style={{ fontSize: '18px' }}>SP / PR / RJ</span>
          </div>
          <div className="kpi-subtitle">Southeast &amp; South shipping nodes</div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="issues-table-card" style={{ marginBottom: '16px', padding: '14px 18px' }}>
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: '10px', flex: 1, minWidth: '280px' }}>
            <input
              type="text"
              className="input-field"
              style={{ width: '100%' }}
              placeholder="Filter seller ID, city, state, or operational symptom..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <select
              className="select-field"
              value={stateFilter}
              onChange={(e) => setStateFilter(e.target.value)}
            >
              <option value="ALL">All Hub States</option>
              {availableStates.map(st => (
                <option key={st} value={st}>{st} State Sellers</option>
              ))}
            </select>

            <select
              className="select-field"
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
            >
              <option value="ALL">All Severities</option>
              <option value="HIGH">High Severity (≥ 40)</option>
              <option value="MEDIUM">Medium Severity (20–40)</option>
              <option value="LOW">Low Severity (&lt; 20)</option>
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

      {/* Sellers Data Table */}
      <div className="issues-table-card">
        <div className="table-card-header">
          <div className="table-title-group">
            <div className="kpi-icon-box icon-box-red" style={{ width: '26px', height: '26px' }}>
              <IconAlert size={14} color="#ef4444" />
            </div>
            <div>
              <h3 className="analytics-card-title">Fulfillment Merchants Risk Breakdown</h3>
              <p className="analytics-card-subtitle">
                Ranked by severity score: (Low-Score Δ × 0.6 + Late-Rate Δ × 0.4) × log₁₀(Reviews)
              </p>
            </div>
          </div>
          <span className="badge-neutral" style={{ fontSize: '11px', padding: '3px 8px' }}>
            {filteredSellers.length} Sellers Displayed
          </span>
        </div>

        <div className="priority-table-wrapper">
          <table className="priority-table">
            <thead>
              <tr>
                <th style={{ width: '36px' }}>#</th>
                <th style={{ width: '80px' }}>SEVERITY</th>
                <th>SELLER ACCOUNT &amp; LOCATION</th>
                <th>HUB</th>
                <th>FAILURE MODE</th>
                <th style={{ textAlign: 'right' }}>LATE SLA</th>
                <th style={{ textAlign: 'right' }}>LOW SCORE</th>
                <th style={{ textAlign: 'right' }}>AVG DELAY</th>
                <th style={{ textAlign: 'right' }}>ORDERS (N)</th>
                <th style={{ textAlign: 'center', width: '160px' }}>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {filteredSellers.length > 0 ? (
                filteredSellers.map((seller, idx) => {
                  const isHigh = seller.severity_score >= 40;
                  const isMed = seller.severity_score >= 20 && seller.severity_score < 40;
                  const sevClass = isHigh ? 'badge-sev-high' : isMed ? 'badge-sev-med' : 'badge-sev-low';
                  const sevLabel = isHigh ? 'High' : isMed ? 'Medium' : 'Low';
                  
                  // Extract state
                  const stateMatch = seller.entity_name?.match(/\/([A-Z]{2})\)/);
                  const stateHub = stateMatch ? stateMatch[1] : 'SP';

                  return (
                    <tr key={seller.issue_id}>
                      <td className="cell-num">{idx + 1}</td>
                      <td>
                        <span className={`badge-severity ${sevClass}`}>
                          {sevLabel} ({seller.severity_score})
                        </span>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-white)' }}>
                          {seller.entity_name}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                          {seller.issue_id}
                        </div>
                      </td>
                      <td>
                        <span className="badge-neutral" style={{ fontWeight: 600, color: '#fca5a5' }}>
                          {stateHub}
                        </span>
                      </td>
                      <td className="cell-issue-type">
                        {seller.issue_type.replace('SELLER_', '').replace(/_/g, ' ')}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#fbbf24' }}>
                          {seller.metrics?.late_delivery_rate_pct}%
                        </div>
                        <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                          +{seller.metrics?.late_rate_delta}% vs base
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#f87171' }}>
                          {seller.metrics?.low_score_rate_pct}%
                        </div>
                        <div style={{ fontSize: '10px', color: '#f87171' }}>
                          +{seller.metrics?.low_score_delta}% vs base
                        </div>
                      </td>
                      <td className="cell-orders font-mono" style={{ textAlign: 'right' }}>
                        {seller.metrics?.avg_delay_days}d
                      </td>
                      <td className="cell-orders font-mono" style={{ textAlign: 'right' }}>
                        {seller.metrics?.total_orders} <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>({seller.metrics?.sample_size})</span>
                      </td>
                      <td className="cell-actions">
                        <div className="table-actions-group">
                          <button
                            className="btn-action-view"
                            onClick={() => onSelectIssue(seller.issue_id)}
                            title="Inspect Seller Evidence & Portuguese Reviews"
                            type="button"
                          >
                            Evidence
                          </button>
                          <button
                            className="btn-action-fix"
                            onClick={() => onOpenActionPlan(seller.issue_id)}
                            title="Generate Seller Action Plan via Groq/AMD Instinct"
                            type="button"
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
                  <td colSpan="10" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                    No marketplace sellers match the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
