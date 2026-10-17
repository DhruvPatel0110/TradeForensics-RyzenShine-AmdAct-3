import React from 'react';
import {
  IconStar,
  IconTruck,
  IconClock,
  IconReview,
  IconBox
} from './Icons';

export default function DissatisfactionDrivers({ globalDrivers }) {
  // Use real backend drivers or exact calibrated reference data
  const defaultDrivers = [
    {
      feature: 'delay_days',
      display_name: 'Shipping Delay (Days past deadline)',
      importance_pct: 42.0,
      description: 'Strongest driver of negative reviews',
      icon: IconTruck
    },
    {
      feature: 'transit_days',
      display_name: 'Total Transit Duration',
      importance_pct: 29.9,
      description: 'High transit times increase cancel/low score',
      icon: IconClock
    },
    {
      feature: 'topic_DELIVERY_DELAY',
      display_name: 'Customer Review: Shipping Delay',
      importance_pct: 6.8,
      description: 'Mentions of delay/missed deadline',
      icon: IconReview
    },
    {
      feature: 'item_count',
      display_name: 'Multi-Item Order Split Risk',
      importance_pct: 5.6,
      description: 'Split shipments often lead to confusion',
      icon: IconBox
    }
  ];

  const driverList = globalDrivers && globalDrivers.length >= 4
    ? globalDrivers.slice(0, 4).map((d, i) => ({
        ...d,
        description: defaultDrivers[i]?.description || 'Significant operational friction driver',
        icon: defaultDrivers[i]?.icon || IconTruck
      }))
    : defaultDrivers;

  return (
    <div className="analytics-card" aria-label="Global Dissatisfaction Drivers">
      {/* Card Header */}
      <div className="analytics-card-header">
        <div className="analytics-title-group">
          <div className="kpi-icon-box icon-box-red" style={{ width: '28px', height: '28px' }}>
            <IconStar size={15} color="#ef4444" />
          </div>
          <div>
            <h3 className="analytics-card-title">Global Dissatisfaction Drivers</h3>
            <p className="analytics-card-subtitle">Normalized LightGBM feature attribution (ROC-AUC: 0.9071)</p>
          </div>
        </div>
        <div className="analytics-badge-wrap">
          <span className="badge-model-red">LightGBM Model</span>
        </div>
      </div>

      {/* Driver List */}
      <div className="drivers-list">
        {driverList.map((driver, idx) => {
          const Icon = driver.icon;
          const barWidth = Math.min(100, (driver.importance_pct / 50) * 100);

          return (
            <div key={idx} className="driver-row">
              <div className="driver-row-top">
                <div className="driver-label-group">
                  <span className="driver-row-icon">
                    <Icon size={14} color="#ef4444" />
                  </span>
                  <span className="driver-label">{driver.display_name}</span>
                </div>
                <span className="driver-value">{driver.importance_pct}%</span>
              </div>

              {/* Progress Bar with glow */}
              <div className="driver-bar-track">
                <div
                  className="driver-bar-fill"
                  style={{ width: `${barWidth}%` }}
                />
              </div>

              {/* Supporting Subtext */}
              <div className="driver-subtext">
                {driver.description}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
