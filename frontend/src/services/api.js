/**
 * TradeForensics API Service
 * Handles all communication with FastAPI backend endpoints.
 */

const API_BASE = '/api';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
  return res.json();
}

export async function fetchOverview() {
  const res = await fetch(`${API_BASE}/overview`);
  if (!res.ok) throw new Error(`Failed to load store overview: ${res.statusText}`);
  return res.json();
}

export async function fetchIssues({ limit = 20, entityType = null, issueType = null } = {}) {
  const params = new URLSearchParams();
  if (limit) params.set('limit', limit);
  if (entityType) params.set('entity_type', entityType);
  if (issueType) params.set('issue_type', issueType);

  const res = await fetch(`${API_BASE}/issues?${params.toString()}`);
  if (!res.ok) throw new Error(`Failed to load issues: ${res.statusText}`);
  return res.json();
}

export async function fetchIssueEvidence(issueId) {
  const res = await fetch(`${API_BASE}/issues/${encodeURIComponent(issueId)}/evidence`);
  if (!res.ok) throw new Error(`Failed to fetch evidence for ${issueId}: ${res.statusText}`);
  return res.json();
}

export async function generateActionPlan(issueId) {
  const res = await fetch(`${API_BASE}/action-plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ issue_id: issueId })
  });
  if (!res.ok) throw new Error(`Failed to generate action plan: ${res.statusText}`);
  return res.json();
}

export async function askCopilot(issueId, question) {
  const res = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ issue_id: issueId, question })
  });
  if (!res.ok) throw new Error(`Copilot query failed: ${res.statusText}`);
  return res.json();
}
