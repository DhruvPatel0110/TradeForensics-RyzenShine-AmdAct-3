import React, { useState, useEffect } from 'react';
import {
  fetchHealth,
  fetchOverview,
  fetchIssues,
  fetchIssueEvidence,
  generateActionPlan
} from './services/api';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardView from './pages/DashboardView';
import IssueExplorer from './pages/IssueExplorer';
import SellersView from './pages/SellersView';
import ProductsView from './pages/ProductsView';
import IssueDetailDrawer from './components/IssueDetailDrawer';
import ActionPlanModal from './components/ActionPlanModal';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  
  // Data state
  const [overview, setOverview] = useState(null);
  const [issues, setIssues] = useState([]);
  const [sellers, setSellers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [health, setHealth] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Detail Drawer state
  const [selectedIssueId, setSelectedIssueId] = useState(null);
  const [selectedEvidence, setSelectedEvidence] = useState(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isLoadingEvidence, setIsLoadingEvidence] = useState(false);

  // Copilot Modal state
  const [actionPlan, setActionPlan] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoadingPlan, setIsLoadingPlan] = useState(false);

  // Initial Data Fetch
  useEffect(() => {
    async function initData() {
      try {
        setIsLoading(true);
        const [healthRes, overviewRes, issuesRes, sellersRes, categoriesRes] = await Promise.all([
          fetchHealth().catch(() => null),
          fetchOverview(),
          fetchIssues({ limit: 50 }),
          fetchIssues({ limit: 50, entityType: 'seller' }).catch(() => ({ issues: [] })),
          fetchIssues({ limit: 50, entityType: 'category' }).catch(() => ({ issues: [] }))
        ]);
        setHealth(healthRes);
        setOverview(overviewRes);
        setIssues(issuesRes?.issues || []);
        setSellers(sellersRes?.issues || []);
        setCategories(categoriesRes?.issues || []);
      } catch (err) {
        console.error('Initialization error:', err);
        setError(err.message || 'Failed to connect to backend server');
      } finally {
        setIsLoading(false);
      }
    }
    initData();
  }, []);

  // Handle Issue Inspection (Opens Drawer)
  const handleSelectIssue = async (issueId) => {
    if (!issueId) return;
    setSelectedIssueId(issueId);
    setIsDrawerOpen(true);
    setIsLoadingEvidence(true);
    try {
      const ev = await fetchIssueEvidence(issueId);
      setSelectedEvidence(ev);
    } catch (err) {
      console.error('Failed to fetch evidence:', err);
    } finally {
      setIsLoadingEvidence(false);
    }
  };

  // Handle Copilot Plan Generation (Opens Modal)
  const handleOpenActionPlan = async (issueId) => {
    if (!issueId) return;
    setSelectedIssueId(issueId);
    setIsModalOpen(true);
    setIsLoadingPlan(true);
    setActionPlan(null);
    try {
      const plan = await generateActionPlan(issueId);
      setActionPlan(plan);
    } catch (err) {
      console.error('Action plan error:', err);
    } finally {
      setIsLoadingPlan(false);
    }
  };

  // Handle Search Submission
  const handleSearchSubmit = (term) => {
    if (!term.trim()) return;
    setActiveTab('issues');
  };

  // Active LLM Display string
  const llmDisplay = health?.llm_provider
    ? health.llm_provider.toLowerCase() === 'fireworks'
      ? 'AMD Instinct'
      : `${health.llm_provider.toUpperCase()} LLM`
    : 'Groq LLM';

  if (isLoading) {
    return (
      <div className="app-loading-screen">
        <div className="app-loading-brand">
          <div className="loading-logo-box">TF</div>
          <span className="loading-title">TradeForensics</span>
          <span className="header-team-pill">RyzenShine</span>
        </div>
        <div className="copilot-spinner" style={{ width: '32px', height: '32px' }} />
        <p className="loading-subtext">
          Loading 98k+ Olist Records, LightGBM Models &amp; ChromaDB Vectors...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-error-screen">
        <div className="error-card">
          <h2 className="error-title">Backend Connection Offline</h2>
          <p className="error-msg">{error}</p>
          <div className="error-hint">
            Make sure the FastAPI backend is running on <code>http://localhost:8000</code>.
          </div>
          <button
            className="hero-cta-btn"
            style={{ marginTop: '20px', alignSelf: 'center' }}
            onClick={() => window.location.reload()}
            type="button"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-layout">
      {/* 1. Left Fixed Navigation Sidebar (i1.png background) */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          setActiveTab(tab);
          if (tab === 'copilot') {
            const issueId = issues[0]?.issue_id || 'seller_1ca7077d890b907f89be8c954a02686a';
            handleOpenActionPlan(issueId);
          }
        }}
        issueCount={issues.length}
      />

      {/* 2. Main Workspace Layout */}
      <div className="app-main-workspace">
        {/* Top Header */}
        <Header
          searchTerm={searchTerm}
          onSearchChange={setSearchTerm}
          onSearchSubmit={handleSearchSubmit}
        />

        {/* Tab Views */}
        <main className="app-page-content">
          {activeTab === 'dashboard' && (
            <DashboardView
              overview={overview}
              issues={issues}
              llmProvider={llmDisplay}
              onSelectIssue={handleSelectIssue}
              onOpenActionPlan={handleOpenActionPlan}
              onNavigateToIssues={() => setActiveTab('issues')}
            />
          )}

          {activeTab === 'issues' && (
            <IssueExplorer
              issues={issues}
              searchTerm={searchTerm}
              onSelectIssue={handleSelectIssue}
              onOpenActionPlan={handleOpenActionPlan}
            />
          )}

          {activeTab === 'sellers' && (
            <SellersView
              sellers={sellers}
              onSelectIssue={handleSelectIssue}
              onOpenActionPlan={handleOpenActionPlan}
            />
          )}

          {activeTab === 'products' && (
            <ProductsView
              categories={categories}
              topCategories={overview?.top_categories || []}
              onSelectIssue={handleSelectIssue}
              onOpenActionPlan={handleOpenActionPlan}
            />
          )}

          {activeTab === 'reviews' && (
            <div className="issues-table-card" style={{ padding: '32px' }}>
              <div className="table-card-header">
                <div>
                  <h3 className="analytics-card-title">Portuguese Customer Reviews Intelligence</h3>
                  <p className="analytics-card-subtitle">
                    40,162 customer text comments processed via TF-IDF + Logistic Regression (97.00% accuracy) &amp; ChromaDB
                  </p>
                </div>
                <span className="badge-model-red">ChromaDB RAG Online</span>
              </div>
              <div style={{ marginTop: '20px' }}>
                <p style={{ color: '#9ca3af', fontSize: '13px', lineHeight: '1.6' }}>
                  Customer comments are categorized into 4 operational root-cause topics: 
                  <strong style={{ color: '#ef4444' }}> DELIVERY_DELAY</strong> (29.6%), 
                  <strong style={{ color: '#f59e0b' }}> SERVICE_REFUND</strong> (8.8%), 
                  <strong style={{ color: '#e5e7eb' }}> DAMAGED_DEFECTIVE</strong> (5.6%), and 
                  <strong style={{ color: '#e5e7eb' }}> CATALOG_MISMATCH</strong> (3.3%).
                </p>
                <div style={{ marginTop: '20px' }}>
                  <button
                    className="hero-cta-btn"
                    onClick={() => setActiveTab('issues')}
                    type="button"
                  >
                    Browse Reviews in Issue Explorer →
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'settings' && (
            <div className="issues-table-card" style={{ padding: '32px', maxWidth: '780px' }}>
              <div className="table-card-header">
                <div>
                  <h3 className="analytics-card-title">System &amp; Environment Diagnostics</h3>
                  <p className="analytics-card-subtitle">TradeForensics runtime configuration</p>
                </div>
                <span className="badge-severity badge-sev-low">System Healthy</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '24px' }}>
                <div className="driver-row" style={{ padding: '12px 16px', background: '#121319', borderRadius: '8px' }}>
                  <div className="driver-row-top">
                    <span className="driver-label">Active LLM Provider</span>
                    <span className="font-mono" style={{ color: '#ef4444', fontWeight: 600 }}>{llmDisplay}</span>
                  </div>
                  <div className="driver-subtext">Toggle via LLM_PROVIDER in .env (Groq API or AMD Instinct Fireworks)</div>
                </div>

                <div className="driver-row" style={{ padding: '12px 16px', background: '#121319', borderRadius: '8px' }}>
                  <div className="driver-row-top">
                    <span className="driver-label">Analytical Dataset Scope</span>
                    <span className="font-mono" style={{ color: '#f3f4f6' }}>98,666 unique orders</span>
                  </div>
                  <div className="driver-subtext">Kaggle Brazilian E-Commerce Public Dataset by Olist (2016–2018)</div>
                </div>

                <div className="driver-row" style={{ padding: '12px 16px', background: '#121319', borderRadius: '8px' }}>
                  <div className="driver-row-top">
                    <span className="driver-label">Vector Store (ChromaDB)</span>
                    <span className="font-mono" style={{ color: '#2dd4bf' }}>3,000 stratified customer reviews</span>
                  </div>
                  <div className="driver-subtext">Embedded using all-MiniLM-L6-v2 384-dimensional dense vectors (Stratified across sellers &amp; categories)</div>
                </div>

                <div className="driver-row" style={{ padding: '12px 16px', background: '#121319', borderRadius: '8px' }}>
                  <div className="driver-row-top">
                    <span className="driver-label">Tabular ML Model</span>
                    <span className="font-mono" style={{ color: '#ef4444' }}>LightGBM (ROC-AUC: 0.9071)</span>
                  </div>
                  <div className="driver-subtext">Trained on 16 logistics and operational features</div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>

      {/* 3. Slide-in Issue Detail Drawer */}
      <IssueDetailDrawer
        isOpen={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        evidence={selectedEvidence}
        isLoadingEvidence={isLoadingEvidence}
        onOpenActionPlan={handleOpenActionPlan}
      />

      {/* 4. AI Action Plan Modal Dialog */}
      <ActionPlanModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        plan={actionPlan}
        isLoadingPlan={isLoadingPlan}
        issueId={selectedIssueId}
      />
    </div>
  );
}
