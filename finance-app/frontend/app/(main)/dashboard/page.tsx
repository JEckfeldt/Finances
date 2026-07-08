"use client";

import { useCallback, useEffect, useState } from "react";

import {
  BalanceCard,
  BudgetProgressCard,
  ExpenseSummaryCard,
  IncomeSummaryCard,
  RecentTransactionsCard,
} from "@/components/dashboard/dashboard-widgets";
import { SpendingTrendsChart } from "@/components/dashboard/spending-trends-chart";
import { getDashboard } from "@/lib/api";
import type { DashboardData } from "@/lib/types";

export default function DashboardPage() {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    try {
      setError(null);
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

  if (isLoading) {
    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Overview of your financial health
          </p>
        </div>
        <p className="py-8 text-center text-sm text-muted-foreground">
          Loading dashboard...
        </p>
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
        <p className="py-8 text-center text-sm text-destructive">
          {error ?? "Failed to load dashboard"}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Overview of your financial health
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <BalanceCard balance={dashboard.current_balance} />
        <IncomeSummaryCard income={dashboard.monthly_summary.income} />
        <ExpenseSummaryCard expenses={dashboard.monthly_summary.expenses} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <BudgetProgressCard budgets={dashboard.budget_overview} />
        <RecentTransactionsCard transactions={dashboard.recent_transactions} />
      </div>

      <SpendingTrendsChart data={dashboard.monthly_spending_trend} />
    </div>
  );
}
