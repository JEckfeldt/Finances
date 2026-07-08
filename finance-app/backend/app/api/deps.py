from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.db.session import get_db

__all__ = ["get_db", "get_current_user_id", "DbDep", "UserIdDep"]

DbDep = Session
UserIdDep = int
