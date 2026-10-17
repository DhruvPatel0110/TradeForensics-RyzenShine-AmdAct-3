import React from 'react';
import {
  IconBox,
  IconClock,
  IconStar,
  IconPulse
} from './Icons';

export default function KpiCards({ kpis }) {
  const totalOrders = kpis?.total_orders || 98666;
  const delivered = kpis?.delivered_orders || 96470;
  const cancelled = kpis?.cancelled_orders || 461;
  const lateRate = kpis?.global_late_rate_pct || 8.11;
  const avgDelay = kpis?.global_avg_delay_days || 8.6;
  const lowRatingShare = kpis?.global_low_score_rate_pct || 14.23;
  const avgRating = kpis?.global_avg_review_score || 4.1;
  const healthScore = kpis?.store_health_score || 62.4;

  return (
    <div className="kpi-cards-grid">
      {/* 1. Total Store Volume */}
      <div className="kpi-card">
        <div className="kpi-card-header">
          <div className="kpi-icon-box icon-box-red">
            <IconBox size={16} color="#ef4444" />
          </div>
          <span className="kpi-label">Total Store Volume</span>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value">{totalOrders.toLocaleString()}</span>
          {/* Mini Sparkline Bars */}
          <div className="kpi-mini-graphic" aria-hidden="true">
            <svg width="44" height="24" viewBox="0 0 44 24" fill="none">
              <rect x="2" y="14" width="4" height="10" rx="1" fill="#ef4444" opacity="0.3" />
              <rect x="8" y="10" width="4" height="14" rx="1" fill="#ef4444" opacity="0.4" />
              <rect x="14" y="6" width="4" height="18" rx="1" fill="#ef4444" opacity="0.5" />
              <rect x="20" y="12" width="4" height="12" rx="1" fill="#ef4444" opacity="0.4" />
              <rect x="26" y="8" width="4" height="16" rx="1" fill="#ef4444" opacity="0.6" />
              <rect x="32" y="4" width="4" height="20" rx="1" fill="#ef4444" opacity="0.8" />
              <rect x="38" y="2" width="4" height="22" rx="1" fill="#ef4444" />
            </svg>
          </div>
        </div>
        <div className="kpi-subtitle">
          {delivered.toLocaleString()} delivered • {cancelled} cancelled
        </div>
      </div>

      {/* 2. Late Delivery Rate */}
      <div className="kpi-card">
        <div className="kpi-card-header">
          <div className="kpi-icon-box icon-box-red">
            <IconClock size={16} color="#ef4444" />
          </div>
          <span className="kpi-label">Late Delivery Rate</span>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value">{lateRate}%</span>
          {/* Mini Wave Graphic */}
          <div className="kpi-mini-graphic" aria-hidden="true">
            <svg width="44" height="24" viewBox="0 0 44 24" fill="none">
              <path d="M2 18 C10 18, 16 22, 22 14 C28 6, 36 8, 42 4" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" />
              <path d="M2 18 C10 18, 16 22, 22 14 C28 6, 36 8, 42 4 L42 24 L2 24 Z" fill="url(#lateRateGrad)" opacity="0.15" />
              <defs>
                <linearGradient id="lateRateGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity="0" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
        <div className="kpi-subtitle">
          Avg {avgDelay} days delay on late orders
        </div>
      </div>

      {/* 3. Low Rating Share (<= 2 Stars) */}
      <div className="kpi-card">
        <div className="kpi-card-header">
          <div className="kpi-icon-box icon-box-red">
            <IconStar size={16} color="#ef4444" />
          </div>
          <span className="kpi-label">Low Rating Share (≤ 2★)</span>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value">{lowRatingShare}%</span>
          {/* Mini Bars */}
          <div className="kpi-mini-graphic" aria-hidden="true">
            <svg width="44" height="24" viewBox="0 0 44 24" fill="none">
              <rect x="2" y="16" width="4" height="8" rx="1" fill="#ef4444" opacity="0.3" />
              <rect x="9" y="14" width="4" height="10" rx="1" fill="#ef4444" opacity="0.4" />
              <rect x="16" y="12" width="4" height="12" rx="1" fill="#ef4444" opacity="0.5" />
              <rect x="23" y="10" width="4" height="14" rx="1" fill="#ef4444" opacity="0.6" />
              <rect x="30" y="6" width="4" height="18" rx="1" fill="#ef4444" opacity="0.75" />
              <rect x="37" y="4" width="4" height="20" rx="1" fill="#ef4444" />
            </svg>
          </div>
        </div>
        <div className="kpi-subtitle">
          Avg customer rating: {avgRating} / 5.0
        </div>
      </div>

      {/* 4. Store Health Score */}
      <div className="kpi-card">
        <div className="kpi-card-header">
          <div className="kpi-icon-box icon-box-teal">
            <IconPulse size={16} color="#2dd4bf" />
          </div>
          <span className="kpi-label">Store Health Score</span>
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value val-teal">
            {healthScore} <span className="val-sub">/ 100</span>
          </span>
          {/* Mini Pulse Graphic */}
          <div className="kpi-mini-graphic" aria-hidden="true">
            <svg width="44" height="24" viewBox="0 0 44 24" fill="none">
              <path d="M2 13 L12 13 L15 19 L21 4 L26 21 L29 11 L33 14 L42 13" stroke="#2dd4bf" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </div>
        </div>
        <div className="kpi-subtitle">
          Composite SLA &amp; fulfillment rating
        </div>
      </div>
    </div>
  );
}
