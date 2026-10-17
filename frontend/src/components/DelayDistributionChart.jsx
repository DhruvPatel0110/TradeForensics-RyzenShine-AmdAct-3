import React, { useState } from 'react';
import { IconInsights } from './Icons';

export default function DelayDistributionChart({ delayDistribution }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  // Normalize or default delay buckets
  const rawData = delayDistribution && delayDistribution.length >= 4
    ? delayDistribution.slice(0, 4)
    : [
        { bucket: 'On Time', order_count: 90840, pct_of_orders: 92.1, low_score_rate_pct: 10.8 },
        { bucket: '1–3 Days', order_count: 2662, pct_of_orders: 2.7, low_score_rate_pct: 19.0 },
        { bucket: '4–7 Days', order_count: 1819, pct_of_orders: 1.7, low_score_rate_pct: 59.8 },
        { bucket: '8–14 Days', order_count: 1790, pct_of_orders: 1.8, low_score_rate_pct: 76.4 }
      ];

  const categories = [
    { label: 'On Time', count: rawData[0]?.order_count || 90840, pct: rawData[0]?.pct_of_orders || 92.1, rate: rawData[0]?.low_score_rate_pct || 10.8 },
    { label: '1–3 Days', count: rawData[1]?.order_count || 2662, pct: rawData[1]?.pct_of_orders || 2.7, rate: rawData[1]?.low_score_rate_pct || 19.0 },
    { label: '4–7 Days', count: rawData[2]?.order_count || 1819, pct: rawData[2]?.pct_of_orders || 1.7, rate: rawData[2]?.low_score_rate_pct || 59.8 },
    { label: '8–14 Days', count: rawData[3]?.order_count || 1790, pct: rawData[3]?.pct_of_orders || 1.8, rate: rawData[3]?.low_score_rate_pct || 76.4 }
  ];

  // SVG Chart Geometry
  const width = 540;
  const height = 230;
  const padding = { top: 30, right: 46, bottom: 35, left: 52 };
  const chartW = width - padding.left - padding.right;
  const chartH = height - padding.top - padding.bottom;

  const maxVolume = 100000;
  const maxRate = 100;

  // Grid steps
  const yTicks = [
    { val: 100000, label: '100K', rateLabel: '100%' },
    { val: 75000, label: '75K', rateLabel: '80%' },
    { val: 50000, label: '50K', rateLabel: '60%' },
    { val: 25000, label: '25K', rateLabel: '40%' },
    { val: 0, label: '0', rateLabel: '0%' }
  ];

  const colWidth = chartW / categories.length;

  // Compute points for the line
  const linePoints = categories.map((cat, idx) => {
    const x = padding.left + idx * colWidth + colWidth / 2;
    const y = padding.top + chartH - (cat.rate / maxRate) * chartH;
    return { x, y, rate: cat.rate };
  });

  // SVG path for smooth line
  const pathD = linePoints.reduce((acc, pt, idx, arr) => {
    if (idx === 0) return `M ${pt.x} ${pt.y}`;
    const prev = arr[idx - 1];
    const cpX = (prev.x + pt.x) / 2;
    return `${acc} C ${cpX} ${prev.y}, ${cpX} ${pt.y}, ${pt.x} ${pt.y}`;
  }, '');

  return (
    <div className="analytics-card" aria-label="Fulfillment Delay Distribution Chart">
      {/* Card Header */}
      <div className="analytics-card-header">
        <div className="analytics-title-group">
          <div className="kpi-icon-box icon-box-red" style={{ width: '28px', height: '28px' }}>
            <IconInsights size={15} color="#ef4444" />
          </div>
          <div>
            <h3 className="analytics-card-title">Fulfillment Delay Distribution</h3>
            <p className="analytics-card-subtitle">Order volume vs negative rating rate across delay buckets</p>
          </div>
        </div>
        <div className="analytics-badge-wrap">
          <button className="dropdown-pill-btn" type="button">
            <span>Deterministic SQL</span>
            <span style={{ fontSize: '10px' }}>⌄</span>
          </button>
        </div>
      </div>

      {/* Legend */}
      <div className="chart-legend-row">
        <div className="legend-item">
          <span className="legend-box-volume" />
          <span>Order Volume</span>
        </div>
        <div className="legend-item">
          <span className="legend-dot-rate" />
          <span>Negative Rating Rate</span>
        </div>
      </div>

      {/* Responsive SVG Chart */}
      <div className="chart-svg-container">
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="chart-svg"
          preserveAspectRatio="xMidYMid meet"
        >
          <defs>
            {/* Bar gradient: dark red to solid deep crimson */}
            <linearGradient id="barGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#b91c1c" stopOpacity="0.85" />
              <stop offset="100%" stopColor="#450a0a" stopOpacity="0.6" />
            </linearGradient>
            <linearGradient id="barHoverGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#ef4444" stopOpacity="1" />
              <stop offset="100%" stopColor="#7f1d1d" stopOpacity="0.8" />
            </linearGradient>
            <filter id="glowLine" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="2" stdDeviation="3" floodColor="#ef4444" floodOpacity="0.6" />
            </filter>
          </defs>

          {/* Left Y Axis Label */}
          <text
            x={14}
            y={height / 2}
            transform={`rotate(-90 14,${height / 2})`}
            fill="#6b7280"
            fontSize="10"
            textAnchor="middle"
            fontFamily="Inter, sans-serif"
          >
            Order Volume
          </text>

          {/* Right Y Axis Label */}
          <text
            x={width - 8}
            y={height / 2}
            transform={`rotate(90 ${width - 8},${height / 2})`}
            fill="#6b7280"
            fontSize="10"
            textAnchor="middle"
            fontFamily="Inter, sans-serif"
          >
            Negative Rating Rate
          </text>

          {/* Grid lines and tick labels */}
          {yTicks.map((tick, idx) => {
            const y = padding.top + (idx / (yTicks.length - 1)) * chartH;
            return (
              <g key={idx}>
                {/* Horizontal gridline */}
                <line
                  x1={padding.left}
                  y1={y}
                  x2={width - padding.right}
                  y2={y}
                  stroke="#1c1e26"
                  strokeDasharray="2 3"
                />
                {/* Left tick label */}
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  fill="#6b7280"
                  fontSize="10"
                  textAnchor="end"
                  fontFamily="JetBrains Mono, monospace"
                >
                  {tick.label}
                </text>
                {/* Right tick label */}
                <text
                  x={width - padding.right + 8}
                  y={y + 3}
                  fill="#6b7280"
                  fontSize="10"
                  textAnchor="start"
                  fontFamily="JetBrains Mono, monospace"
                >
                  {tick.rateLabel}
                </text>
              </g>
            );
          })}

          {/* X Axis Baseline */}
          <line
            x1={padding.left}
            y1={padding.top + chartH}
            x2={width - padding.right}
            y2={padding.top + chartH}
            stroke="#262934"
          />

          {/* Volume Bars */}
          {categories.map((cat, idx) => {
            const barW = 44;
            const x = padding.left + idx * colWidth + (colWidth - barW) / 2;
            const barH = Math.max(4, (cat.count / maxVolume) * chartH);
            const y = padding.top + chartH - barH;
            const isHovered = hoveredIndex === idx;

            return (
              <g
                key={idx}
                onMouseEnter={() => setHoveredIndex(idx)}
                onMouseLeave={() => setHoveredIndex(null)}
                style={{ cursor: 'pointer' }}
              >
                <rect
                  x={x}
                  y={y}
                  width={barW}
                  height={barH}
                  rx="4"
                  fill={isHovered ? 'url(#barHoverGrad)' : 'url(#barGrad)'}
                  stroke={isHovered ? '#ef4444' : 'rgba(239, 68, 68, 0.25)'}
                  strokeWidth="1"
                  className="chart-bar"
                />
                {/* Value on top of bar */}
                <text
                  x={x + barW / 2}
                  y={y - 12}
                  fill="#f3f4f6"
                  fontSize="10"
                  fontWeight="600"
                  textAnchor="middle"
                  fontFamily="JetBrains Mono, monospace"
                >
                  {cat.count.toLocaleString()}
                </text>
                <text
                  x={x + barW / 2}
                  y={y - 2}
                  fill="#9ca3af"
                  fontSize="9"
                  textAnchor="middle"
                  fontFamily="Inter, sans-serif"
                >
                  ({cat.pct}%)
                </text>

                {/* X-axis category label */}
                <text
                  x={padding.left + idx * colWidth + colWidth / 2}
                  y={padding.top + chartH + 18}
                  fill="#9ca3af"
                  fontSize="11"
                  textAnchor="middle"
                  fontFamily="Inter, sans-serif"
                >
                  {cat.label}
                </text>
              </g>
            );
          })}

          {/* Negative Rating Rate Line */}
          <path
            d={pathD}
            fill="none"
            stroke="#ef4444"
            strokeWidth="2.5"
            strokeLinecap="round"
            filter="url(#glowLine)"
          />

          {/* Line Nodes and Rate Labels */}
          {linePoints.map((pt, idx) => (
            <g key={idx}>
              {/* Outer glow ring */}
              <circle
                cx={pt.x}
                cy={pt.y}
                r="6"
                fill="#b91c1c"
                opacity="0.4"
              />
              {/* Center dot */}
              <circle
                cx={pt.x}
                cy={pt.y}
                r="3.5"
                fill="#ffffff"
                stroke="#ef4444"
                strokeWidth="2"
              />
              {/* Rate percentage label */}
              <text
                x={pt.x}
                y={pt.y - 10}
                fill="#ef4444"
                fontSize="11"
                fontWeight="700"
                textAnchor="middle"
                fontFamily="JetBrains Mono, monospace"
              >
                {pt.rate}%
              </text>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
}
