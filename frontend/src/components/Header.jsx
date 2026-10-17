import React from 'react';
import { IconSearch, IconSun, IconBell } from './Icons';

export default function Header({
  searchTerm = '',
  onSearchChange,
  onSearchSubmit
}) {
  return (
    <header className="top-header" role="banner">
      {/* Left: Branding & Subtitles */}
      <div className="header-left">
        <div className="header-title-row">
          <h1 className="header-brand-title">TradeForensics</h1>
          <span className="header-team-pill">RyzenShine</span>
        </div>
        <div className="header-subtitle-row">
          <span>Operational Diagnostics &amp; Action Copilot</span>
          <span className="subtitle-divider">|</span>
          <span>Brazilian E-commerce Analytics</span>
          <span className="subtitle-divider">|</span>
          <span>AMD Developer Hackathon ACT III</span>
        </div>
      </div>

      {/* Right: Search bar & Utilities */}
      <div className="header-right">
        <div className="search-bar-container">
          <span className="search-icon">
            <IconSearch size={15} color="#6b7280" />
          </span>
          <input
            type="text"
            className="search-input"
            placeholder="Search seller, product, location, or issue..."
            value={searchTerm}
            onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && onSearchSubmit) {
                onSearchSubmit(searchTerm);
              }
            }}
            aria-label="Search dashboard"
          />
          <kbd className="search-kbd">Ctrl K</kbd>
        </div>

        {/* Theme Toggle Button */}
        <button
          className="header-icon-btn"
          title="Toggle display mode"
          aria-label="Toggle display mode"
          type="button"
        >
          <IconSun size={17} color="#9ca3af" />
        </button>

        {/* Notification Bell with Badge */}
        <button
          className="header-icon-btn"
          title="1 operational alert"
          aria-label="1 operational alert"
          type="button"
        >
          <IconBell size={17} color="#9ca3af" />
          <span className="notification-counter-badge">1</span>
        </button>

        {/* User Profile Badge (RyzenShine) */}
        <div className="header-user-avatar" title="RyzenShine Team Lead">
          RS
        </div>
      </div>
    </header>
  );
}
