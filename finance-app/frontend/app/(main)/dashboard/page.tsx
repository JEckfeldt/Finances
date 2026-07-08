import {
  BalanceCard,
  BudgetProgressCard,
  ExpenseSummaryCard,
  FinancialTrendsCard,
  IncomeSummaryCard,
  RecentTransactionsCard,
} from "@/components/dashboard/dashboard-widgets";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Overview of your financial health
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <BalanceCard />
        <IncomeSummaryCard />
        <ExpenseSummaryCard />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <BudgetProgressCard />
        <RecentTransactionsCard />
      </div>

      <FinancialTrendsCard />
    </div>
  );
}
