def normalize_category(category: str) -> str:
    """Trim whitespace and apply consistent casing for storage and comparison."""
    return category.strip().title()
