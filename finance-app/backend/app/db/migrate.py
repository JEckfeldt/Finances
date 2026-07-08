from sqlalchemy import inspect, text

from app.db.session import engine


def _has_foreign_key(table_name: str, referred_table: str) -> bool:
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return False
    foreign_keys = inspector.get_foreign_keys(table_name)
    return any(fk.get("referred_table") == referred_table for fk in foreign_keys)


def migrate_users_table() -> None:
    """Add auth columns to legacy placeholder users table when needed."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("users")}

    with engine.begin() as connection:
        if "hashed_password" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255) NOT NULL DEFAULT ''"
                )
            )
            connection.execute(
                text("ALTER TABLE users ALTER COLUMN hashed_password DROP DEFAULT")
            )

        if "created_at" not in columns:
            connection.execute(
                text(
                    "ALTER TABLE users ADD COLUMN created_at TIMESTAMPTZ NOT NULL DEFAULT now()"
                )
            )


def migrate_foreign_keys() -> None:
    """Add user foreign keys to existing tables when missing."""
    with engine.begin() as connection:
        if not _has_foreign_key("transactions", "users"):
            connection.execute(
                text(
                    "ALTER TABLE transactions "
                    "ADD CONSTRAINT transactions_user_id_fkey "
                    "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
                )
            )

        if not _has_foreign_key("budgets", "users"):
            connection.execute(
                text(
                    "ALTER TABLE budgets "
                    "ADD CONSTRAINT budgets_user_id_fkey "
                    "FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE"
                )
            )
