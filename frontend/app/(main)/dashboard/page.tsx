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
import { IncomeExpenseChart } from "@/components/dashboard/income-expense-chart";
import { SpendingTrendsChart } from "@/components/dashboard/spending-trends-chart";
import { ErrorState } from "@/components/ui/error-state";
import { getDashboard } from "@/lib/api";
import type { DashboardData } from "@/lib/types";

function getCurrentMonthLabel(): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    year: "numeric",
  }).format(new Date());
}

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);
      const data = await getDashboard();
      setDashboard(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load dashboard"
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const pageSections = "space-y-5 sm:space-y-6 lg:space-y-8";
  const widgetGrid = "grid grid-cols-1 gap-3 sm:gap-4 lg:grid-cols-2 [&>*]:min-w-0";

  if (isLoading && !dashboard) {
    return (
      <div className={pageSections}>
        <div>
          <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">Dashboard</h1>
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
      <div className={pageSections}>
        <div>
          <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">Dashboard</h1>
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
    <div className={pageSections}>
      <div>
        <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Overview of your financial health
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3 [&>*]:min-w-0">
        <BalanceCard balance={dashboard.current_balance} />
        <IncomeSummaryCard
          income={dashboard.monthly_summary.income}
          periodLabel={`Income for ${getCurrentMonthLabel()}`}
        />
        <ExpenseSummaryCard
          expenses={dashboard.monthly_summary.expenses}
          periodLabel={`Expenses for ${getCurrentMonthLabel()}`}
        />
      </div>

      <div className={widgetGrid}>
        <BudgetProgressCard budgets={dashboard.budget_overview} />
        <RecentTransactionsCard transactions={dashboard.recent_transactions} />
      </div>

      <div className={widgetGrid}>
        <IncomeExpenseChart data={dashboard.monthly_comparison_trend} />
        <SpendingTrendsChart data={dashboard.monthly_spending_trend} />
      </div>
    </div>
  );
}
