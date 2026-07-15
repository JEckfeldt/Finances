from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.ai import AIInsightsResponse
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
