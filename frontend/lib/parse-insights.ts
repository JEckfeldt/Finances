export type AIInsightStatus = "loading" | "success" | "disabled" | "error";

/**
 * Parse Gemini insight text into discrete items for display.
 * Supports bullets (-, *, •), numbered lists, and plain newline-separated lines.
 */
export function parseInsightLines(insights: string): string[] {
  const lines = insights
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);

  const items: string[] = [];

  for (const line of lines) {
    const bulletMatch = line.match(/^[-*•]\s+(.+)$/);
    const numberedMatch = line.match(/^\d+[.)]\s+(.+)$/);

    if (bulletMatch) {
      items.push(bulletMatch[1]);
      continue;
    }

    if (numberedMatch) {
      items.push(numberedMatch[1]);
      continue;
    }

    items.push(line);
  }

  return items;
}
