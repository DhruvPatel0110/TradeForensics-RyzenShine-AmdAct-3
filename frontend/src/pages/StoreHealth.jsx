import React from 'react';

export default function StoreHealth({ overview, onSelectIssue, onNavigateToIssues }) {
  if (!overview) return null;

  const { kpis, delay_distribution, top_categories, global_drivers } = overview;
  const impact = kpis.correlation_impact;

  return (
    <div>
      {/* Alert Banner */}
      <div style={{
        background: 'linear-gradient(90deg, rgba(239,68,68,0.12) 0%, rgba(20,20,24,0.6) 100%)',
        border: '1px solid rgba(239,68,68,0.25)',
        borderRadius: 'var(--radius-md)',
        padding: '16px 20px',
        marginBottom: '24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: 'var(--accent-red)',
            boxShadow: '0 0 10px rgba(239,68,68,0.8)'
          }} />
          <div>
            <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-primary)' }}>
              Operational Ground Truth: Late Shipments Carry a {impact.risk_multiplier}x Dissatisfaction Multiplier
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              On-time shipments have a <span style={{ color: '#34d399', fontWeight: 500 }}>{impact.on_time_low_score_pct}%</span> negative review rate, jumping to <span style={{ color: '#f87171', fontWeight: 600 }}>{impact.late_low_score_pct}%</span> when delivery deadline is missed.
            </div>
          </div>
        </div>
        <button
          className="btn btn-primary btn-sm"
          onClick={onNavigateToIssues}
        >
          Explore Top Friction Points &rarr;
        </button>
      </div>

      {/* KPI Cards Row */}
      <div className="grid-4">
        <div className="card">
          <div className="card-title">Total Store Volume</div>
          <div className="card-value">{kpis.total_orders.toLocaleString()}</div>
          <div className="card-subtitle">
            {kpis.delivered_orders.toLocaleString()} delivered · {kpis.cancelled_orders} cancelled
          </div>
        </div>

        <div className="card">
          <div className="card-title">Late Delivery Rate</div>
          <div className="card-value" style={{ color: kpis.global_late_rate_pct > 8 ? '#f87171' : 'var(--text-primary)' }}>
            {kpis.global_late_rate_pct}%
          </div>
          <div className="card-subtitle">
            Avg {kpis.global_avg_delay_days} days delay on late orders
          </div>
        </div>

        <div className="card">
          <div className="card-title">Low Rating Share (≤ 2★)</div>
          <div className="card-value" style={{ color: kpis.global_low_score_rate_pct > 14 ? '#f87171' : 'var(--text-primary)' }}>
            {kpis.global_low_score_rate_pct}%
          </div>
          <div className="card-subtitle">
            Avg customer rating: {kpis.global_avg_review_score} / 5.0
          </div>
        </div>

        <div className="card">
          <div className="card-title">Store Health Score</div>
          <div className="card-value" style={{ color: '#34d399' }}>
            {kpis.store_health_score} <span style={{ fontSize: '14px', color: 'var(--text-muted)' }}>/ 100</span>
          </div>
          <div className="card-subtitle">
            Composite SLA & fulfillment rating
          </div>
        </div>
      </div>

      {/* Charts Grid: Delay Distribution & ML Feature Drivers */}
      <div className="grid-2">
        {/* Delay Distribution & Penalty Curve */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Fulfillment Delay Distribution & Dissatisfaction Escalation
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                Order volume vs negative rating rate across delay buckets
              </div>
            </div>
            <span className="badge badge-neutral">Deterministic SQL</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '12px' }}>
            {delay_distribution.map((item, idx) => {
              const penaltyColor = item.low_score_rate_pct > 50 ? '#ef4444' : item.low_score_rate_pct > 20 ? '#f59e0b' : '#10b981';

              return (
                <div key={idx} style={{ fontSize: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{item.bucket}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                      {item.order_count.toLocaleString()} orders ({item.pct_of_orders}%)
                      <span style={{ marginLeft: '10px', color: penaltyColor, fontWeight: 600 }}>
                        {item.low_score_rate_pct}% negative
                      </span>
                    </span>
                  </div>

                  {/* Dual Bar: Orders volume and Negative Review rate */}
                  <div style={{ height: '8px', background: '#1c1c22', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                    <div style={{
                      width: `${item.low_score_rate_pct}%`,
                      background: penaltyColor,
                      transition: 'width 0.4s ease'
                    }} />
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '16px', display: 'flex', gap: '16px' }}>
            <span><strong style={{ color: '#10b981' }}>■</strong> 10.8% baseline on-time</span>
            <span><strong style={{ color: '#f59e0b' }}>■</strong> 19.0% 1-3d delay</span>
            <span><strong style={{ color: '#ef4444' }}>■</strong> 76.4% 8+ days delay</span>
          </div>
        </div>

        {/* Global ML Feature Drivers (LightGBM) */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Global Dissatisfaction Root-Cause Drivers
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                Normalized LightGBM feature attribution (ROC-AUC: 0.9071)
              </div>
            </div>
            <span className="badge badge-red">LightGBM Model</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginTop: '12px' }}>
            {global_drivers.map((driver, idx) => (
              <div key={idx} style={{ fontSize: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{driver.display_name}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--accent-red)' }}>
                    {driver.importance_pct}%
                  </span>
                </div>
                <div style={{ height: '8px', background: '#1c1c22', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${driver.importance_pct}%`,
                    background: 'linear-gradient(90deg, #dc2626 0%, #ef4444 100%)',
                    height: '100%',
                    borderRadius: '4px',
                    transition: 'width 0.4s ease'
                  }} />
                </div>
              </div>
            ))}
          </div>

          <div style={{
            fontSize: '11px',
            color: 'var(--text-secondary)',
            marginTop: '20px',
            background: 'var(--bg-base)',
            padding: '10px 12px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)'
          }}>
            <strong style={{ color: 'var(--text-primary)' }}>Key Diagnostic:</strong> Logistics friction (delay days + transit duration) explains over <strong>71.9%</strong> of customer dissatisfaction across the platform.
          </div>
        </div>
      </div>

      {/* Top Categories Benchmark Table */}
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)' }}>
              Major Product Categories Fulfillment & Quality Benchmark
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
              Comparison of high-volume categories against store baseline (8.1% late, 14.2% low ratings)
            </div>
          </div>
          <span className="badge badge-neutral">Top Categories</span>
        </div>

        <div className="table-container">
          <table className="data-table">
            <thead>
              <tr>
                <th>Product Category</th>
                <th>Total Orders</th>
                <th>Late Delivery Rate</th>
                <th>Low Rating Share</th>
                <th>Delta vs Baseline</th>
                <th>Avg Delay</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {top_categories.map((cat, idx) => {
                const isLateElevated = cat.late_delivery_rate_pct > 8.1;
                const isLowScoreElevated = cat.low_score_delta > 0;
                const issueId = `cat_${cat.category}`;

                return (
                  <tr key={idx}>
                    <td style={{ fontWeight: 500, color: 'var(--text-primary)' }}>
                      {cat.category.replace(/_/g, ' ')}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{cat.total_orders.toLocaleString()}</td>
                    <td>
                      <span className={`badge ${isLateElevated ? 'badge-amber' : 'badge-green'}`}>
                        {cat.late_delivery_rate_pct}%
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${isLowScoreElevated ? 'badge-red' : 'badge-green'}`}>
                        {cat.low_score_rate_pct}%
                      </span>
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)', color: isLowScoreElevated ? '#f87171' : '#34d399' }}>
                      {isLowScoreElevated ? `+${cat.low_score_delta}%` : `${cat.low_score_delta}%`}
                    </td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{cat.avg_delay_days}d</td>
                    <td>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => onSelectIssue(issueId)}
                      >
                        Inspect Issue
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
