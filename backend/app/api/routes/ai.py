from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import AIActionRequest, AIActionResponse, AIInsightsResponse
from app.services.ai_action_service import process_natural_language_action
from app.services.ai_insights_service import generate_financial_insights
from app.services.ai_service import AIServiceError

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/insights", response_model=AIInsightsResponse)
def create_financial_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIInsightsResponse:
    try:
        return generate_financial_insights(db, current_user.id)
    except AIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


@router.post("/action", response_model=AIActionResponse)
def create_natural_language_action(
    body: AIActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AIActionResponse:
    return process_natural_language_action(db, current_user.id, body.message)
