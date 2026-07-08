export type DateRangePreset =
  | "default"
  | "last_7_days"
  | "last_30_days"
  | "this_month"
  | "last_month"
  | "last_3_months"
  | "this_year";

export interface DateRangeParams {
  start_date?: string;
  end_date?: string;
}

function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function startOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}

function endOfMonth(date: Date): Date {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
}

export function getDateRangeForPreset(
  preset: DateRangePreset
): DateRangeParams {
  if (preset === "default") {
    return {};
  }

  const today = new Date();
  const end = formatDate(today);

  switch (preset) {
    case "last_7_days": {
      const start = new Date(today);
      start.setDate(start.getDate() - 6);
      return { start_date: formatDate(start), end_date: end };
    }
    case "last_30_days": {
      const start = new Date(today);
      start.setDate(start.getDate() - 29);
      return { start_date: formatDate(start), end_date: end };
    }
    case "this_month":
      return {
        start_date: formatDate(startOfMonth(today)),
        end_date: end,
      };
    case "last_month": {
      const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      return {
        start_date: formatDate(startOfMonth(lastMonth)),
        end_date: formatDate(endOfMonth(lastMonth)),
      };
    }
    case "last_3_months": {
      const start = new Date(today.getFullYear(), today.getMonth() - 2, 1);
      return { start_date: formatDate(start), end_date: end };
    }
    case "this_year":
      return {
        start_date: formatDate(new Date(today.getFullYear(), 0, 1)),
        end_date: end,
      };
    default:
      return {};
  }
}

export const DATE_RANGE_OPTIONS: { value: DateRangePreset; label: string }[] = [
  { value: "default", label: "All time / This month" },
  { value: "last_7_days", label: "Last 7 days" },
  { value: "last_30_days", label: "Last 30 days" },
  { value: "this_month", label: "This month" },
  { value: "last_month", label: "Last month" },
  { value: "last_3_months", label: "Last 3 months" },
  { value: "this_year", label: "This year" },
];

export function getPeriodLabel(preset: DateRangePreset): string {
  const option = DATE_RANGE_OPTIONS.find((item) => item.value === preset);
  return option?.label ?? "Selected period";
}
