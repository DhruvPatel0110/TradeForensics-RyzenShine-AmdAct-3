import React, { useState, useMemo } from 'react';
import { IconProduct, IconBox, IconTruck, IconStar, IconAlert } from '../components/Icons';

export default function ProductsView({
  categories = [],
  topCategories = [],
  onSelectIssue,
  onOpenActionPlan
}) {
  const [searchTerm, setSearchTerm] = useState('');
  const [sectorFilter, setSectorFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  // Helper to categorize product categories into intuitive sectors
  const getProductSector = (categoryName = '') => {
    const cat = categoryName.toLowerCase();
    if (cat.includes('furniture') || cat.includes('bed') || cat.includes('table') || cat.includes('mattress')) {
      return { sector: 'Heavy / Furniture', badgeClass: 'badge-amber' };
    }
    if (cat.includes('computer') || cat.includes('audio') || cat.includes('telephony') || cat.includes('electronic')) {
      return { sector: 'Electronics & Tech', badgeClass: 'badge-teal' };
    }
    if (cat.includes('fashion') || cat.includes('clothing') || cat.includes('shoes') || cat.includes('bag')) {
      return { sector: 'Apparel & Fashion', badgeClass: 'badge-purple' };
    }
    if (cat.includes('housewares') || cat.includes('home') || cat.includes('garden') || cat.includes('appliances')) {
      return { sector: 'Home & Living', badgeClass: 'badge-blue' };
    }
    if (cat.includes('health') || cat.includes('beauty') || cat.includes('perfumery')) {
      return { sector: 'Health & Beauty', badgeClass: 'badge-green' };
    }
    if (cat.includes('auto') || cat.includes('tools') || cat.includes('industry')) {
      return { sector: 'Industrial & Auto', badgeClass: 'badge-neutral' };
    }
    return { sector: 'General Retail', badgeClass: 'badge-neutral' };
  };

  // Combine categories issues and top categories overview
  const combinedCategories = useMemo(() => {
    // If backend provided category issues, use them
    if (categories && categories.length > 0) {
      return categories.map((cat, idx) => {
        const rawName = cat.entity_name || cat.issue_id.replace('cat_', '');
        const displayName = rawName
          .split('_')
          .map(w => w.charAt(0).toUpperCase() + w.slice(1))
          .join(' ');
        const sectorInfo = getProductSector(rawName);

        return {
          id: idx + 1,
          issue_id: cat.issue_id,
          raw_name: rawName,
          display_name: displayName,
          sector: sectorInfo.sector,
          sector_badge: sectorInfo.badgeClass,
          severity_score: cat.severity_score || 12.0,
          issue_type: cat.issue_type || 'CATEGORY_SATISFACTION_DROP',
          primary_driver: cat.primary_driver || `Low-rating share is elevated above store baseline`,
          total_orders: cat.metrics?.total_orders || 100,
          sample_size: cat.metrics?.sample_size || 95,
          late_delivery_rate_pct: cat.metrics?.late_delivery_rate_pct || 8.1,
          late_rate_delta: cat.metrics?.late_rate_delta || 0.0,
          low_score_rate_pct: cat.metrics?.low_score_rate_pct || 14.2,
          low_score_delta: cat.metrics?.low_score_delta || 0.0,
          avg_delay_days: cat.metrics?.avg_delay_days || 8.0
        };
      });
    }

    // Fallback using top_categories from overview
    return topCategories.map((cat, idx) => {
      const rawName = cat.category;
      const displayName = rawName
        .split('_')
        .map(w => w.charAt(0).toUpperCase() + w.slice(1))
        .join(' ');
      const sectorInfo = getProductSector(rawName);

      return {
        id: idx + 1,
        issue_id: `cat_${rawName}`,
        raw_name: rawName,
        display_name: displayName,
        sector: sectorInfo.sector,
        sector_badge: sectorInfo.badgeClass,
        severity_score: Math.round(Math.abs(cat.low_score_delta || 0) * 3.5),
        issue_type: (cat.late_delivery_rate_pct > 8.1) ? 'LOGISTICS_BOTTLENECK' : 'CATEGORY_SATISFACTION_DROP',
        primary_driver: `Low-rating share is +${cat.low_score_delta}% vs store baseline`,
        total_orders: cat.total_orders,
        sample_size: cat.review_count,
        late_delivery_rate_pct: cat.late_delivery_rate_pct,
        late_rate_delta: (cat.late_delivery_rate_pct - 8.1).toFixed(1),
        low_score_rate_pct: cat.low_score_rate_pct,
        low_score_delta: cat.low_score_delta,
        avg_delay_days: cat.avg_delay_days
      };
    });
  }, [categories, topCategories]);

  // Filtering
  const filteredCategories = useMemo(() => {
    return combinedCategories.filter((cat) => {
      // Sector filter
      if (sectorFilter !== 'ALL' && !cat.sector.includes(sectorFilter)) {
        return false;
      }
      // Status filter
      if (statusFilter === 'CRITICAL' && cat.low_score_delta < 5.0) return false;
      if (statusFilter === 'ELEVATED' && (cat.low_score_delta <= 0 || cat.low_score_delta >= 5.0)) return false;
      if (statusFilter === 'HEALTHY' && cat.low_score_delta > 0) return false;

      // Search term
      if (searchTerm.trim()) {
        const term = searchTerm.toLowerCase();
        const nameMatch = cat.display_name.toLowerCase().includes(term);
        const slugMatch = cat.raw_name.toLowerCase().includes(term);
        const sectorMatch = cat.sector.toLowerCase().includes(term);
        const driverMatch = cat.primary_driver.toLowerCase().includes(term);
        if (!nameMatch && !slugMatch && !sectorMatch && !driverMatch) return false;
      }
      return true;
    });
  }, [combinedCategories, sectorFilter, statusFilter, searchTerm]);

  return (
    <div className="products-page-view" aria-label="Product Category Catalog Forensics">
      {/* Top Header & Context */}
      <div className="section-intro-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div className="kpi-icon-box icon-box-red" style={{ width: '32px', height: '32px' }}>
            <IconProduct size={17} color="#ef4444" />
          </div>
          <div>
            <h2 className="view-page-title">Product Category Quality &amp; Catalog Forensics</h2>
            <p className="view-page-subtitle">
              SLA fulfillment speed, catalog description mismatches, and packaging defects across all 72 Brazilian product categories
            </p>
          </div>
        </div>
        <span className="badge-model-red">Category Vector DB Stratified</span>
      </div>

      {/* 4 Category Metric Cards */}
      <div className="kpi-cards-grid" style={{ marginBottom: '20px' }}>
        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box icon-box-red">
              <IconBox size={15} color="#ef4444" />
            </div>
            <span className="kpi-label">Active Categories Analyzed</span>
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value">68</span>
          </div>
          <div className="kpi-subtitle">Across 98,666 grain-safe customer orders</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box icon-box-red">
              <IconTruck size={15} color="#ef4444" />
            </div>
            <span className="kpi-label">Top Logistics Friction Category</span>
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value" style={{ fontSize: '18px', color: '#f87171' }}>Office Furniture</span>
          </div>
          <div className="kpi-subtitle">22.5% low score • 10.0 days transit delay</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box icon-box-red">
              <IconStar size={15} color="#ef4444" />
            </div>
            <span className="kpi-label">Highest Catalog Mismatch Risk</span>
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value" style={{ fontSize: '18px', color: '#fbbf24' }}>Fashion Male Clothing</span>
          </div>
          <div className="kpi-subtitle">25.9% low score (+11.7% above baseline)</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-card-header">
            <div className="kpi-icon-box icon-box-teal">
              <IconProduct size={15} color="#2dd4bf" />
            </div>
            <span className="kpi-label">Global Baseline Reference</span>
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value val-teal">8.11% / 14.2%</span>
          </div>
          <div className="kpi-subtitle">Late Delivery Rate / Low-Rating Share</div>
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
              placeholder="Filter product category, sector, or defect theme..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <select
              className="select-field"
              value={sectorFilter}
              onChange={(e) => setSectorFilter(e.target.value)}
            >
              <option value="ALL">All Product Sectors</option>
              <option value="Heavy">Heavy / Bulky Furniture</option>
              <option value="Electronics">Electronics &amp; Tech</option>
              <option value="Apparel">Apparel &amp; Fashion</option>
              <option value="Home">Home &amp; Living</option>
              <option value="Health">Health &amp; Beauty</option>
              <option value="Industrial">Industrial &amp; Auto</option>
            </select>

            <select
              className="select-field"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="ALL">All Performance Tiers</option>
              <option value="CRITICAL">Critical Friction (Δ ≥ +5.0%)</option>
              <option value="ELEVATED">Elevated Friction (0 &lt; Δ &lt; +5.0%)</option>
              <option value="HEALTHY">Healthy (Below Baseline)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Products Data Table */}
      <div className="issues-table-card">
        <div className="table-card-header">
          <div className="table-title-group">
            <div className="kpi-icon-box icon-box-red" style={{ width: '26px', height: '26px' }}>
              <IconAlert size={14} color="#ef4444" />
            </div>
            <div>
              <h3 className="analytics-card-title">Category Catalog &amp; Quality Audit</h3>
              <p className="analytics-card-subtitle">
                Cross-referenced with LightGBM feature attribution and stratified Portuguese customer reviews
              </p>
            </div>
          </div>
          <span className="badge-neutral" style={{ fontSize: '11px', padding: '3px 8px' }}>
            {filteredCategories.length} Categories Displayed
          </span>
        </div>

        <div className="priority-table-wrapper">
          <table className="priority-table">
            <thead>
              <tr>
                <th style={{ width: '36px' }}>#</th>
                <th>CATEGORY NAME</th>
                <th>SECTOR</th>
                <th style={{ textAlign: 'right' }}>VOLUME (ORDERS)</th>
                <th style={{ textAlign: 'right' }}>LATE DELIVERY SLA</th>
                <th style={{ textAlign: 'right' }}>LOW SCORE SHARE</th>
                <th style={{ textAlign: 'right' }}>AVG DELAY</th>
                <th>DOMINANT DEFECT / FAILURE MODE</th>
                <th style={{ textAlign: 'center', width: '160px' }}>ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {filteredCategories.length > 0 ? (
                filteredCategories.map((cat, idx) => {
                  const isLowElevated = cat.low_score_delta > 0;
                  const isLateElevated = cat.late_delivery_rate_pct > 8.1;

                  return (
                    <tr key={cat.issue_id}>
                      <td className="cell-num">{idx + 1}</td>
                      <td>
                        <div style={{ fontWeight: 600, color: 'var(--text-white)' }}>
                          {cat.display_name}
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                          {cat.issue_id}
                        </div>
                      </td>
                      <td>
                        <span className="badge-neutral" style={{ fontSize: '10.5px' }}>
                          {cat.sector}
                        </span>
                      </td>
                      <td className="cell-orders font-mono" style={{ textAlign: 'right' }}>
                        {cat.total_orders.toLocaleString()} <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>({cat.sample_size})</span>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: isLateElevated ? '#fbbf24' : '#34d399' }}>
                          {cat.late_delivery_rate_pct}%
                        </div>
                        <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                          {cat.late_rate_delta > 0 ? `+${cat.late_rate_delta}%` : `${cat.late_rate_delta}%`} vs base
                        </div>
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <div style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: isLowElevated ? '#f87171' : '#34d399' }}>
                          {cat.low_score_rate_pct}%
                        </div>
                        <div style={{ fontSize: '10px', color: isLowElevated ? '#f87171' : '#34d399' }}>
                          {isLowElevated ? `+${cat.low_score_delta}%` : `${cat.low_score_delta}%`} vs base
                        </div>
                      </td>
                      <td className="cell-orders font-mono" style={{ textAlign: 'right' }}>
                        {cat.avg_delay_days}d
                      </td>
                      <td className="cell-symptom" style={{ maxWidth: '280px' }}>
                        {cat.primary_driver}
                      </td>
                      <td className="cell-actions">
                        <div className="table-actions-group">
                          <button
                            className="btn-action-view"
                            onClick={() => onSelectIssue(cat.issue_id)}
                            title="Inspect Category Evidence & ChromaDB Quotes"
                            type="button"
                          >
                            Evidence
                          </button>
                          <button
                            className="btn-action-fix"
                            onClick={() => onOpenActionPlan(cat.issue_id)}
                            title="Generate Category Action Plan via Groq/AMD Instinct"
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
                  <td colSpan="9" style={{ textAlign: 'center', padding: '36px', color: 'var(--text-muted)' }}>
                    No product categories match the selected filters.
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
