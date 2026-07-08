"use client";

import { useCallback, useEffect, useState } from "react";

import {
  BalanceCard,
  BudgetProgressCard,
  ExpenseSummaryCard,
  IncomeSummaryCard,
  RecentTransactionsCard,
} from "@/components/dashboard/dashboard-widgets";
import { DashboardSkeleton } from "@/components/dashboard/dashboard-skeleton";
import { DateRangeSelector } from "@/components/dashboard/date-range-selector";
import { IncomeExpenseChart } from "@/components/dashboard/income-expense-chart";
import { SpendingTrendsChart } from "@/components/dashboard/spending-trends-chart";
import { ErrorState } from "@/components/ui/error-state";
import { getDashboard } from "@/lib/api";
import {
  getDateRangeForPreset,
  getPeriodLabel,
  type DateRangePreset,
} from "@/lib/date-range";
import type { DashboardData } from "@/lib/types";

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [datePreset, setDatePreset] = useState<DateRangePreset>("default");

  const loadDashboard = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);
      const range = getDateRangeForPreset(datePreset);
      const data = await getDashboard(range);
      setDashboard(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load dashboard"
      );
    } finally {
      setIsLoading(false);
    }
  }, [datePreset]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const periodLabel =
    datePreset === "default"
      ? "All-time balance · This month's summary"
      : getPeriodLabel(datePreset);

  if (isLoading && !dashboard) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Overview of your financial health
          </p>
        </div>
        <DashboardSkeleton />
      </div>
    );
  }

  if (error || !dashboard) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Overview of your financial health
          </p>
        </div>
        <ErrorState
          message={error ?? "Failed to load dashboard"}
          onRetry={loadDashboard}
        />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Overview of your financial health
          </p>
        </div>
        <DateRangeSelector value={datePreset} onChange={setDatePreset} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <BalanceCard balance={dashboard.current_balance} periodLabel={periodLabel} />
        <IncomeSummaryCard
          income={dashboard.monthly_summary.income}
          periodLabel={periodLabel}
        />
        <ExpenseSummaryCard
          expenses={dashboard.monthly_summary.expenses}
          periodLabel={periodLabel}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <BudgetProgressCard budgets={dashboard.budget_overview} />
        <RecentTransactionsCard transactions={dashboard.recent_transactions} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <IncomeExpenseChart data={dashboard.monthly_comparison_trend} />
        <SpendingTrendsChart data={dashboard.monthly_spending_trend} />
      </div>
    </div>
  );
}
