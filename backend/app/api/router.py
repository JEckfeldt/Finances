from fastapi import APIRouter

from app.api.routes import auth, budgets, dashboard, transactions

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(budgets.router)
api_router.include_router(dashboard.router)
api_router.include_router(transactions.router)
