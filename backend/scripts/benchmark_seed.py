#!/usr/bin/env python3
"""
Benchmark data generator for local performance testing.

Creates a dedicated user with budgets and 10,000 transactions spread across
several years. Does not run automatically — invoke explicitly from the CLI.

Usage:
    python scripts/benchmark_seed.py seed
    python scripts/benchmark_seed.py cleanup

See scripts/README.md for Docker setup and cleanup details.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from random import Random

from dotenv import load_dotenv
from sqlalchemy import func, select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_ROOT.parent

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("APP_ENV", "development")
load_dotenv(REPO_ROOT / ".env")
load_dotenv(BACKEND_ROOT / ".env")

from app.core.auth import hash_password  # noqa: E402
from app.core.categories import normalize_category  # noqa: E402
from app.db.session import SessionLocal  # noqa: E402
from app.models.budget import Budget  # noqa: E402
from app.models.transaction import Transaction, TransactionType  # noqa: E402
from app.models.user import User  # noqa: E402

BENCHMARK_EMAIL = "benchmark@local.dev"
BENCHMARK_PASSWORD = "benchmark123456"
TRANSACTION_COUNT = 10_000
BATCH_SIZE = 500
RNG_SEED = 42

EXPENSE_CATEGORIES: list[tuple[str, tuple[str, ...], tuple[Decimal, Decimal]]] = [
    ("Groceries", ("Costco", "Walmart", "Trader Joe's", "Whole Foods"), (Decimal("8.50"), Decimal("185.00"))),
    ("Dining", ("Lunch", "Dinner", "Coffee Shop", "Restaurant"), (Decimal("6.00"), Decimal("95.00"))),
    ("Gas", ("Shell", "Chevron", "Gas Station"), (Decimal("25.00"), Decimal("75.00"))),
    ("Shopping", ("Amazon", "Target", "Best Buy"), (Decimal("12.00"), Decimal("320.00"))),
    ("Entertainment", ("Netflix", "Spotify", "Movies", "Concert"), (Decimal("9.99"), Decimal("120.00"))),
    ("Utilities", ("Electric Bill", "Water Bill", "Internet"), (Decimal("45.00"), Decimal("210.00"))),
    ("Healthcare", ("Pharmacy", "Copay", "Dental"), (Decimal("15.00"), Decimal("250.00"))),
    ("Travel", ("Hotel", "Flight", "Uber"), (Decimal("18.00"), Decimal("650.00"))),
    ("Subscriptions", ("Gym", "Cloud Storage", "Software"), (Decimal("9.99"), Decimal("49.99"))),
]

INCOME_CATEGORIES: list[tuple[str, tuple[str, ...], tuple[Decimal, Decimal]]] = [
    ("Salary", ("Paycheck", "Direct Deposit"), (Decimal("1200.00"), Decimal("3200.00"))),
    ("Freelance", ("Client Payment", "Consulting"), (Decimal("150.00"), Decimal("1800.00"))),
    ("Investment", ("Dividend", "Interest"), (Decimal("5.00"), Decimal("450.00"))),
    ("Other", ("Refund", "Gift"), (Decimal("10.00"), Decimal("200.00"))),
]

BUDGET_LIMITS: dict[str, Decimal] = {
    "Groceries": Decimal("600.00"),
    "Dining": Decimal("350.00"),
    "Gas": Decimal("200.00"),
    "Shopping": Decimal("400.00"),
    "Entertainment": Decimal("150.00"),
    "Utilities": Decimal("300.00"),
    "Healthcare": Decimal("250.00"),
    "Travel": Decimal("500.00"),
    "Subscriptions": Decimal("120.00"),
}


def _money(rng: Random, low: Decimal, high: Decimal) -> Decimal:
    value = rng.uniform(float(low), float(high))
    return Decimal(str(round(value, 2)))


def _random_date(rng: Random, start: date, end: date) -> date:
    days = (end - start).days
    if days <= 0:
        return start
    return start + timedelta(days=rng.randint(0, days))


def _build_transaction_rows(
    rng: Random,
    user_id: int,
    start: date,
    end: date,
) -> list[dict]:
    rows: list[dict] = []
    income_target = int(TRANSACTION_COUNT * 0.12)

    for index in range(TRANSACTION_COUNT):
        is_income = index < income_target
        if is_income:
            category, descriptions, (low, high) = rng.choice(INCOME_CATEGORIES)
            tx_type = TransactionType.INCOME
        else:
            category, descriptions, (low, high) = rng.choice(EXPENSE_CATEGORIES)
            tx_type = TransactionType.EXPENSE

        rows.append(
            {
                "user_id": user_id,
                "description": rng.choice(descriptions),
                "amount": _money(rng, low, high),
                "type": tx_type,
                "category": normalize_category(category),
                "transaction_date": _random_date(rng, start, end),
            }
        )

    rng.shuffle(rows)
    return rows


def cleanup_benchmark_data() -> None:
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == BENCHMARK_EMAIL))
        if user is None:
            print(f"No benchmark user found ({BENCHMARK_EMAIL}). Nothing to delete.")
            return

        tx_count = session.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.user_id == user.id)
        )
        budget_count = session.scalar(
            select(func.count()).select_from(Budget).where(Budget.user_id == user.id)
        )

        session.delete(user)
        session.commit()

        print(f"Removed benchmark user {BENCHMARK_EMAIL} (id={user.id}).")
        print(f"  Cascaded deletes: {tx_count or 0} transactions, {budget_count or 0} budgets.")


def seed_benchmark_data(*, replace: bool) -> None:
    rng = Random(RNG_SEED)
    today = date.today()
    start = date(today.year - 4, 1, 1)

    with SessionLocal() as session:
        existing = session.scalar(select(User).where(User.email == BENCHMARK_EMAIL))
        if existing is not None:
            if not replace:
                print(
                    f"Benchmark user already exists ({BENCHMARK_EMAIL}). "
                    "Run cleanup first or pass --replace."
                )
                sys.exit(1)
            session.delete(existing)
            session.commit()
            print(f"Removed existing benchmark user before re-seeding.")

        user = User(
            email=BENCHMARK_EMAIL,
            hashed_password=hash_password(BENCHMARK_PASSWORD),
        )
        session.add(user)
        session.flush()

        for category, limit in BUDGET_LIMITS.items():
            session.add(
                Budget(
                    user_id=user.id,
                    category=normalize_category(category),
                    limit_amount=limit,
                )
            )
        session.commit()

        rows = _build_transaction_rows(rng, user.id, start, today)
        for offset in range(0, len(rows), BATCH_SIZE):
            batch = rows[offset : offset + BATCH_SIZE]
            session.bulk_insert_mappings(Transaction, batch)
            session.commit()
            print(f"  Inserted transactions {offset + 1}-{offset + len(batch)} / {len(rows)}")

        tx_count = session.scalar(
            select(func.count())
            .select_from(Transaction)
            .where(Transaction.user_id == user.id)
        )
        budget_count = session.scalar(
            select(func.count()).select_from(Budget).where(Budget.user_id == user.id)
        )

        print()
        print("Benchmark dataset ready.")
        print(f"  Email:        {BENCHMARK_EMAIL}")
        print(f"  Password:     {BENCHMARK_PASSWORD}")
        print(f"  User id:      {user.id}")
        print(f"  Transactions: {tx_count}")
        print(f"  Budgets:      {budget_count}")
        print(f"  Date range:   {start.isoformat()} to {today.isoformat()}")
        print()
        print("Log in via the app or use this account for API performance baselines.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Seed or remove local benchmark data for performance testing."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    seed_parser = subparsers.add_parser("seed", help="Create benchmark user and data")
    seed_parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete existing benchmark user before seeding",
    )

    subparsers.add_parser("cleanup", help="Delete benchmark user and cascaded data")

    args = parser.parse_args()

    if args.command == "cleanup":
        cleanup_benchmark_data()
    elif args.command == "seed":
        seed_benchmark_data(replace=args.replace)


if __name__ == "__main__":
    main()
