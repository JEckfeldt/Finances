from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User

__all__ = ["get_db", "get_current_user", "DbDep", "CurrentUserDep"]

DbDep = Session
CurrentUserDep = User
