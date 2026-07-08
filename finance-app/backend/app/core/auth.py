"""Authentication utilities.

JWT-based authentication will be implemented in a future milestone.
All data access should go through get_current_user_id() so user
isolation can be enforced once auth is added.
"""

DEFAULT_USER_ID = 1


def get_current_user_id() -> int:
    """Return the authenticated user's ID.

    Placeholder: returns a fixed user ID until JWT auth is implemented.
    """
    return DEFAULT_USER_ID
