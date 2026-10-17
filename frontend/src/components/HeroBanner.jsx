import React from 'react';
import {
  IconBox,
  IconClock,
  IconStar,
  IconPulse,
  IconArrowRight
} from './Icons';

export default function HeroBanner({
  kpis,
  onExploreFriction
}) {
  const impact = kpis?.correlation_impact || {
    risk_multiplier: 5.75,
    on_time_low_score_pct: 9.21,
    late_low_score_pct: 52.98
  };

  const totalOrders = kpis?.total_orders || 98666;
  const lateRate = kpis?.global_late_rate_pct || 8.11;
  const lowScoreRate = kpis?.global_low_score_rate_pct || 14.23;
  const healthScore = kpis?.store_health_score || 62.4;

  return (
    <section className="hero-banner" aria-label="Operational Ground Truth Banner">
      {/* Background artwork i2.png & responsive dark gradient */}
      <div className="hero-banner-bg" />
      <div className="hero-banner-overlay" />

      <div className="hero-banner-content">
        {/* Left Side: Headline & Narrative */}
        <div className="hero-left">
          <span className="hero-eyebrow">OPERATIONAL GROUND TRUTH</span>
          <h2 className="hero-headline">
            Late shipments carry a {impact.risk_multiplier}x dissatisfaction multiplier.
          </h2>
          <p className="hero-subtext">
            On-time shipments have a <span className="stat-green">{impact.on_time_low_score_pct}%</span> negative review rate, jumping to <span className="stat-red">{impact.late_low_score_pct}%</span> when delivery deadline is missed.
          </p>
          <div className="hero-cta-wrap">
            <button
              className="hero-cta-btn"
              onClick={onExploreFriction}
              type="button"
            >
              <span>Explore Friction Points</span>
              <IconArrowRight size={14} color="#ffffff" />
            </button>
          </div>
        </div>

        {/* Right Side: Quick Summary Metrics Overlay */}
        <div className="hero-right-metrics">
          {/* 1. Total Orders */}
          <div className="hero-metric-item">
            <div className="hero-metric-icon-wrap icon-red">
              <IconBox size={16} color="#ef4444" />
            </div>
            <div className="hero-metric-text">
              <div className="hero-metric-val">{totalOrders.toLocaleString()}</div>
              <div className="hero-metric-label">Total Orders</div>
            </div>
          </div>

          {/* 2. Late Delivery Rate */}
          <div className="hero-metric-item">
            <div className="hero-metric-icon-wrap icon-red">
              <IconClock size={16} color="#ef4444" />
            </div>
            <div className="hero-metric-text">
              <div className="hero-metric-val">{lateRate}%</div>
              <div className="hero-metric-label">Late Delivery Rate</div>
            </div>
          </div>

          {/* 3. Low Rating Share */}
          <div className="hero-metric-item">
            <div className="hero-metric-icon-wrap icon-red">
              <IconStar size={16} color="#ef4444" />
            </div>
            <div className="hero-metric-text">
              <div className="hero-metric-val val-red">{lowScoreRate}%</div>
              <div className="hero-metric-label">Low Rating Share (≤ 2★)</div>
            </div>
          </div>

          {/* 4. Store Health Score */}
          <div className="hero-metric-item">
            <div className="hero-metric-icon-wrap icon-teal">
              <IconPulse size={16} color="#2dd4bf" />
            </div>
            <div className="hero-metric-text">
              <div className="hero-metric-val val-teal">
                {healthScore} <span className="val-sub">/ 100</span>
              </div>
              <div className="hero-metric-label">Store Health Score</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
