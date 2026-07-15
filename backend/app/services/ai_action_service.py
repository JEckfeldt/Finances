"""
Natural language financial actions service.

Architecture and security:
- Receives only the authenticated user's ID from routes (same pattern as insights).
- Future iterations will parse messages and create transactions or budgets.
- Gemini integration and database writes are not implemented yet.
"""

from sqlalchemy.orm import Session

from app.schemas.ai import AIActionResponse

NOT_IMPLEMENTED_MESSAGE = "Natural language actions are not yet implemented."


def process_natural_language_action(
    db: Session,
    user_id: int,
    message: str,
) -> AIActionResponse:
    """Process a natural language financial action request.

    Placeholder for M19 iteration 1 — validates the request path and auth
    wiring without calling Gemini or mutating data.
    """
    return AIActionResponse(
        status="not_implemented",
        message=NOT_IMPLEMENTED_MESSAGE,
    )
