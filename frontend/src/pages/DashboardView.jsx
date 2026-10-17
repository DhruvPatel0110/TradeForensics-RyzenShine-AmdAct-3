import React from 'react';
import HeroBanner from '../components/HeroBanner';
import KpiCards from '../components/KpiCards';
import DelayDistributionChart from '../components/DelayDistributionChart';
import DissatisfactionDrivers from '../components/DissatisfactionDrivers';
import PriorityIssuesTable from '../components/PriorityIssuesTable';
import CopilotPanel from '../components/CopilotPanel';

export default function DashboardView({
  overview,
  issues = [],
  llmProvider = 'Groq LLM',
  onSelectIssue,
  onOpenActionPlan,
  onNavigateToIssues
}) {
  if (!overview) return null;

  const { kpis, delay_distribution, global_drivers } = overview;
  const defaultIssueId = issues[0]?.issue_id || 'seller_1ca7077d890b907f89be8c954a02686a';

  return (
    <div className="dashboard-grid-layout">
      {/* Left Main Workspace Column */}
      <div className="dashboard-main-col">
        {/* 1. Hero / Operational Ground Truth Banner */}
        <HeroBanner
          kpis={kpis}
          onExploreFriction={onNavigateToIssues}
        />

        {/* 2. 4 Horizontal KPI Metric Cards */}
        <KpiCards kpis={kpis} />

        {/* 3. Analytics Section: Delay Distribution Chart & Dissatisfaction Drivers */}
        <div className="analytics-grid-two-col">
          <DelayDistributionChart delayDistribution={delay_distribution} />
          <DissatisfactionDrivers globalDrivers={global_drivers} />
        </div>

        {/* 4. High Priority Issues Table */}
        <PriorityIssuesTable
          issues={issues}
          onSelectIssue={onSelectIssue}
          onOpenActionPlan={onOpenActionPlan}
          onViewAllIssues={onNavigateToIssues}
        />
      </div>

      {/* Right Column: AI Operations Copilot */}
      <div className="dashboard-copilot-col">
        <CopilotPanel
          llmProvider={llmProvider}
          defaultIssueId={defaultIssueId}
          onTriggerActionPlan={onOpenActionPlan}
        />
      </div>
    </div>
  );
}
