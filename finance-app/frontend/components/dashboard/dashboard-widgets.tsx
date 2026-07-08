import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { DollarSign, TrendingDown, TrendingUp } from "lucide-react";

function PlaceholderValue() {
  return (
    <span className="text-2xl font-semibold text-muted-foreground/50">—</span>
  );
}

export function BalanceCard() {
  return (
    <Card>
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <DollarSign className="size-4" />
          Current Balance
        </CardDescription>
        <CardTitle className="text-3xl font-semibold">
          <PlaceholderValue />
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          Total available funds across all accounts
        </p>
      </CardContent>
    </Card>
  );
}

export function IncomeSummaryCard() {
  return (
    <Card>
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <TrendingUp className="size-4 text-primary" />
          Income Summary
        </CardDescription>
        <CardTitle className="text-2xl font-semibold">
          <PlaceholderValue />
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">This month&apos;s income</p>
      </CardContent>
    </Card>
  );
}

export function ExpenseSummaryCard() {
  return (
    <Card>
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <TrendingDown className="size-4 text-destructive" />
          Expense Summary
        </CardDescription>
        <CardTitle className="text-2xl font-semibold">
          <PlaceholderValue />
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">This month&apos;s expenses</p>
      </CardContent>
    </Card>
  );
}

export function BudgetProgressCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Budget Progress</CardTitle>
        <CardDescription>Spending against your budgets</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {["Groceries", "Transportation", "Entertainment"].map((category) => (
            <div key={category} className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">{category}</span>
                <span className="text-muted-foreground/50">— / —</span>
              </div>
              <div className="h-2 rounded-full bg-muted">
                <div className="h-2 w-0 rounded-full bg-primary/40" />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function RecentTransactionsCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Transactions</CardTitle>
        <CardDescription>Your latest financial activity</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="flex items-center justify-between rounded-lg border border-dashed border-border px-4 py-3"
            >
              <div className="space-y-1">
                <p className="text-sm text-muted-foreground/50">Transaction</p>
                <p className="text-xs text-muted-foreground/40">Category</p>
              </div>
              <span className="text-sm text-muted-foreground/50">—</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

export function FinancialTrendsCard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Financial Trends</CardTitle>
        <CardDescription>Income vs expenses over time</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex h-48 items-center justify-center rounded-lg border border-dashed border-border bg-muted/30">
          <p className="text-sm text-muted-foreground">
            Chart will be displayed here
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
