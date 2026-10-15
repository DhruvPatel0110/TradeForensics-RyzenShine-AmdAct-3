import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query

from backend.app.services.issue_detector import issue_detector
from backend.app.services.evidence_assembler import evidence_assembler
from backend.app.llm.schemas import EvidencePacket

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/issues", tags=["Issues & Diagnosis"])

@router.get("", response_model=Dict[str, Any])
def list_issues(
    limit: int = Query(default=15, ge=1, le=50, description="Max issues to return"),
    entity_type: Optional[str] = Query(default=None, description="Filter by 'category' or 'seller'"),
    issue_type: Optional[str] = Query(default=None, description="Filter by issue type")
):
    """
    Returns ranked operational friction points across categories and sellers
    sorted descending by mathematical severity score.
    """
    all_issues = issue_detector.detect_top_issues(top_n=50)

    filtered = []
    for iss in all_issues:
        if entity_type and iss["entity_type"] != entity_type:
            continue
        if issue_type and iss["issue_type"] != issue_type:
            continue
        filtered.append(iss)

    result = filtered[:limit]
    return {
        "count": len(result),
        "total_available": len(filtered),
        "issues": result
    }

@router.get("/{issue_id}", response_model=Dict[str, Any])
def get_issue(issue_id: str):
    """Returns single issue summary and basic metrics."""
    all_issues = issue_detector.detect_top_issues(top_n=50)
    for iss in all_issues:
        if iss["issue_id"] == issue_id:
            return iss
    raise HTTPException(status_code=404, detail=f"Issue '{issue_id}' not found in detected issues.")

@router.get("/{issue_id}/evidence", response_model=EvidencePacket)
def get_issue_evidence(issue_id: str):
    """
    Returns the complete, assembled EvidencePacket combining:
    1. Deterministic SQL KPIs (volumes, deltas, rates).
    2. LightGBM tabular ML predicted segment risk and root-cause drivers.
    3. ChromaDB vector search authentic Brazilian Portuguese customer quotes.
    """
    try:
        packet = evidence_assembler.assemble_evidence(issue_id)
        return packet
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error assembling evidence for {issue_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to assemble evidence packet: {str(e)}")
