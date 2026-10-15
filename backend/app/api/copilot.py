import logging
from typing import Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from backend.app.services.copilot_service import copilot_service
from backend.app.llm.schemas import ActionPlanResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Action Copilot"])

class ActionPlanRequest(BaseModel):
    issue_id: str = Field(description="Issue ID, e.g., 'cat_office_furniture' or 'seller_1ca7077d890b907f89be8c954a02686a'")

class AskCopilotRequest(BaseModel):
    issue_id: str = Field(description="Target issue identifier")
    question: str = Field(min_length=3, description="Merchant operational question")

class AskCopilotResponse(BaseModel):
    issue_id: str
    question: str
    answer: str
    cited_metrics: Dict[str, Any]
    recommended_next_step: str

@router.post("/action-plan", response_model=ActionPlanResponse)
def create_action_plan(payload: ActionPlanRequest):
    """
    Generates a structured, evidence-grounded remediation action plan
    synthesizing SQL KPIs, LightGBM feature attribution, and authentic customer quotes.
    Strictly forbids hallucinated metrics.
    """
    try:
        plan = copilot_service.generate_action_plan(payload.issue_id)
        return plan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Action plan generation failed for {payload.issue_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate action plan: {str(e)}")

@router.post("/ask", response_model=AskCopilotResponse)
def ask_question(payload: AskCopilotRequest):
    """
    Handles custom natural language merchant questions grounded in the Evidence Packet.
    """
    try:
        result = copilot_service.ask_copilot(payload.issue_id, payload.question)
        return AskCopilotResponse(
            issue_id=payload.issue_id,
            question=payload.question,
            answer=result.get("answer", ""),
            cited_metrics=result.get("cited_metrics", {}),
            recommended_next_step=result.get("recommended_next_step", "")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Ask copilot failed for {payload.issue_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to answer question: {str(e)}")
