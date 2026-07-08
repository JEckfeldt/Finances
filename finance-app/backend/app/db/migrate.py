from sqlalchemy import inspect, text

from app.db.session import engine


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
