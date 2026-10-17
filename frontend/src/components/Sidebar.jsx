import React from 'react';
import {
  IconTFLogo,
  IconDashboard,
  IconTarget,
  IconSeller,
  IconProduct,
  IconReview,
  IconCopilot,
  IconSettings
} from './Icons';

export default function Sidebar({ activeTab, onSelectTab, issueCount = 0 }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: IconDashboard },
    { id: 'issues', label: 'Issue Explorer', icon: IconTarget, badge: issueCount > 0 ? issueCount : null },
    { id: 'sellers', label: 'Sellers', icon: IconSeller },
    { id: 'products', label: 'Products', icon: IconProduct },
    { id: 'reviews', label: 'Reviews', icon: IconReview },
    { id: 'copilot', label: 'AI Copilot', icon: IconCopilot }
  ];

  return (
    <aside className="app-sidebar" aria-label="Main Navigation">
      <div className="sidebar-background" />
      <div className="sidebar-overlay" />
      
      <div className="sidebar-content">
        {/* Top Logo */}
        <div className="sidebar-logo">
          <IconTFLogo size={36} />
        </div>

        {/* Navigation Items */}
        <nav className="sidebar-nav">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                className={`sidebar-nav-item ${isActive ? 'active' : ''}`}
                onClick={() => onSelectTab(item.id)}
                type="button"
                aria-current={isActive ? 'page' : undefined}
              >
                <span className="sidebar-nav-icon">
                  <Icon size={18} color={isActive ? '#ef4444' : 'currentColor'} />
                </span>
                <span className="sidebar-nav-label">{item.label}</span>
                {item.badge && (
                  <span className="sidebar-nav-badge">{item.badge}</span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Bottom Settings Item */}
        <div className="sidebar-footer">
          <button
            className={`sidebar-nav-item ${activeTab === 'settings' ? 'active' : ''}`}
            onClick={() => onSelectTab('settings')}
            type="button"
          >
            <span className="sidebar-nav-icon">
              <IconSettings size={18} color={activeTab === 'settings' ? '#ef4444' : 'currentColor'} />
            </span>
            <span className="sidebar-nav-label">Settings</span>
          </button>
        </div>
      </div>
    </aside>
  );
}
