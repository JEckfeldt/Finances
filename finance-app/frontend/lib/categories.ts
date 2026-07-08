export const COMMON_CATEGORIES = [
  "Groceries",
  "Food",
  "Transportation",
  "Entertainment",
  "Utilities",
  "Healthcare",
  "Salary",
  "Rent",
  "Shopping",
  "Savings",
];

export function mergeCategorySuggestions(
  userCategories: string[],
  query = ""
): string[] {
  const normalizedQuery = query.trim().toLowerCase();
  const combined = [...new Set([...userCategories, ...COMMON_CATEGORIES])].sort(
    (a, b) => a.localeCompare(b)
  );

  if (!normalizedQuery) {
    return combined;
  }

  return combined.filter((category) =>
    category.toLowerCase().includes(normalizedQuery)
  );
}
