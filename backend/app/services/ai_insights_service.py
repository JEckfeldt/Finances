"""
Financial insights service for AI-powered summaries.

Architecture and security:
- Queries only the authenticated user's data via user_id passed from routes.
- Builds a sanitized text summary before calling ai_service.generate_text().
- Never sends email, account IDs, or raw transaction descriptions to Gemini.
- Gemini has no database access; all context is assembled in this module.
"""

from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.transaction import Transaction, TransactionType
from app.schemas.ai import AIInsightsResponse
from app.services.ai_service import AIServiceError, generate_text
from app.services.dashboard import (
    _apply_transaction_date_filters,
    _month_date_bounds,
    _recent_months,
    _sum_by_type,
    _totals_by_month_and_type,
)

RECENT_TREND_MONTH_COUNT = 3


@dataclass(frozen=True)
class FinancialInsightContext:
    month_label: str
    current_month_income: Decimal
    current_month_expenses: Decimal
    spending_by_category: list[tuple[str, Decimal]]
    budget_utilization: list[tuple[str, Decimal, Decimal, float]]
    recent_monthly_trends: list[tuple[str, Decimal, Decimal]]


def _current_month_range() -> tuple[date, date]:
    today = datetime.now(UTC).date()
    return _month_date_bounds(today.year, today.month)


def _spending_by_category_for_period(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
) -> list[tuple[str, Decimal]]:
    stmt = (
        select(
            Transaction.category,
            func.coalesce(func.sum(Transaction.amount), 0),
        )
        .where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
        )
        .group_by(Transaction.category)
        .order_by(func.sum(Transaction.amount).desc())
    )
    stmt = _apply_transaction_date_filters(stmt, start_date, end_date)
    rows = db.execute(stmt).all()
    return [(category, Decimal(str(total))) for category, total in rows]


def _budget_utilization_for_period(
    db: Session,
    user_id: int,
    start_date: date,
    end_date: date,
) -> list[tuple[str, Decimal, Decimal, float]]:
    budgets = list(
        db.scalars(
            select(Budget)
            .where(Budget.user_id == user_id)
            .order_by(Budget.category)
        ).all()
    )
    spending_by_category = {
        category.lower(): amount
        for category, amount in _spending_by_category_for_period(
            db, user_id, start_date, end_date
        )
    }

    utilization: list[tuple[str, Decimal, Decimal, float]] = []
    for budget in budgets:
        spent = spending_by_category.get(budget.category.lower(), Decimal("0"))
        percentage = (
            float(spent / budget.limit_amount * 100)
            if budget.limit_amount > 0
            else 0.0
        )
        utilization.append((budget.category, spent, budget.limit_amount, percentage))

    return sorted(utilization, key=lambda item: item[3], reverse=True)


def build_financial_insight_context(db: Session, user_id: int) -> FinancialInsightContext:
    month_start, month_end = _current_month_range()
    month_label = datetime(month_start.year, month_start.month, 1, tzinfo=UTC).strftime(
        "%B %Y"
    )

    current_month_income = _sum_by_type(
        db, user_id, TransactionType.INCOME, month_start, month_end
    )
    current_month_expenses = _sum_by_type(
        db, user_id, TransactionType.EXPENSE, month_start, month_end
    )

    income_by_month = _totals_by_month_and_type(
        db, user_id, TransactionType.INCOME, None, None
    )
    expense_by_month = _totals_by_month_and_type(
        db, user_id, TransactionType.EXPENSE, None, None
    )

    recent_monthly_trends: list[tuple[str, Decimal, Decimal]] = []
    for year, month in _recent_months(RECENT_TREND_MONTH_COUNT):
        label = datetime(year, month, 1, tzinfo=UTC).strftime("%b %Y")
        key = (year, month)
        recent_monthly_trends.append(
            (
                label,
                income_by_month.get(key, Decimal("0")),
                expense_by_month.get(key, Decimal("0")),
            )
        )

    return FinancialInsightContext(
        month_label=month_label,
        current_month_income=current_month_income,
        current_month_expenses=current_month_expenses,
        spending_by_category=_spending_by_category_for_period(
            db, user_id, month_start, month_end
        ),
        budget_utilization=_budget_utilization_for_period(
            db, user_id, month_start, month_end
        ),
        recent_monthly_trends=recent_monthly_trends,
    )


def build_insights_prompt(context: FinancialInsightContext) -> str:
    net = context.current_month_income - context.current_month_expenses

    category_lines = "\n".join(
        f"- {category}: ${amount:.2f}"
        for category, amount in context.spending_by_category
    ) or "- No expense categories recorded this month"

    budget_lines = "\n".join(
        f"- {category}: spent ${spent:.2f} of ${limit:.2f} ({percentage:.1f}% used)"
        for category, spent, limit, percentage in context.budget_utilization
    ) or "- No budgets configured"

    trend_lines = "\n".join(
        f"- {month}: income ${income:.2f}, expenses ${expenses:.2f}"
        for month, income, expenses in context.recent_monthly_trends
    )

    return f"""You are a helpful personal finance assistant. Review the user's financial summary and provide concise, actionable insights.

Rules:
- Use only the data provided below.
- Do not invent transactions, balances, or categories.
- Keep the response practical and easy to understand.
- Provide 3 to 5 short bullet points.
- Do not include sensitive identifiers.

Financial summary for {context.month_label}:
- Income: ${context.current_month_income:.2f}
- Expenses: ${context.current_month_expenses:.2f}
- Net: ${net:.2f}

Spending by category:
{category_lines}

Budget utilization:
{budget_lines}

Recent monthly trends:
{trend_lines}
"""


def generate_financial_insights(db: Session, user_id: int) -> AIInsightsResponse:
    context = build_financial_insight_context(db, user_id)
    prompt = build_insights_prompt(context)
    ai_response = generate_text(prompt)

    if not ai_response.enabled:
        return AIInsightsResponse(
            enabled=False,
            message=ai_response.message,
        )

    if not ai_response.text:
        raise AIServiceError("AI provider returned no insight text")

    return AIInsightsResponse(
        enabled=True,
        insights=ai_response.text,
    )
