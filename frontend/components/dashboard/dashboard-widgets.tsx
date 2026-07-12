import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { formatCurrency, formatTransactionDate } from "@/lib/format";
import type {
  BudgetProgress,
  DashboardRecentTransaction,
} from "@/lib/types";
import { DollarSign, TrendingDown, TrendingUp } from "lucide-react";

interface BalanceCardProps {
  balance: string;
  periodLabel?: string;
}

export function BalanceCard({ balance, periodLabel }: BalanceCardProps) {
  const value = parseFloat(balance);
  const isNegative = value < 0;

  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <DollarSign className="size-4 shrink-0" />
          Current Balance
        </CardDescription>
        <CardTitle
          className={`text-2xl font-semibold sm:text-3xl ${
            isNegative ? "text-destructive" : "text-foreground"
          }`}
        >
          {formatCurrency(balance)}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="line-clamp-2 text-xs text-muted-foreground sm:text-sm">
          {periodLabel ?? "Current Balance"}
        </p>
      </CardContent>
    </Card>
  );
}

interface IncomeSummaryCardProps {
  income: string;
  periodLabel?: string;
}

export function IncomeSummaryCard({ income, periodLabel }: IncomeSummaryCardProps) {
  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <TrendingUp className="size-4 shrink-0 text-primary" />
          Income Summary
        </CardDescription>
        <CardTitle className="text-xl font-semibold text-primary sm:text-2xl">
          {formatCurrency(income)}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="line-clamp-2 text-xs text-muted-foreground sm:text-sm">
          {periodLabel ?? "This month's income"}
        </p>
      </CardContent>
    </Card>
  );
}

interface ExpenseSummaryCardProps {
  expenses: string;
  periodLabel?: string;
}

export function ExpenseSummaryCard({
  expenses,
  periodLabel,
}: ExpenseSummaryCardProps) {
  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <TrendingDown className="size-4 shrink-0 text-destructive" />
          Expense Summary
        </CardDescription>
        <CardTitle className="text-xl font-semibold sm:text-2xl">
          {formatCurrency(expenses)}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="line-clamp-2 text-xs text-muted-foreground sm:text-sm">
          {periodLabel ?? "This month's expenses"}
        </p>
      </CardContent>
    </Card>
  );
}

interface BudgetProgressCardProps {
  budgets: BudgetProgress[];
}

export function BudgetProgressCard({ budgets }: BudgetProgressCardProps) {
  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Budget Progress</CardTitle>
        <CardDescription>Spending against your budgets</CardDescription>
      </CardHeader>
      <CardContent className="min-w-0">
        {budgets.length === 0 ? (
          <p className="py-3 text-center text-sm text-muted-foreground sm:py-4">
            No budgets yet. Create one on the Budgets page.
          </p>
        ) : (
          <div className="space-y-3 sm:space-y-4">
            {budgets.map((budget) => {
              const percentage = Math.min(Math.max(budget.percentage, 0), 100);
              const isOverBudget = parseFloat(budget.remaining) < 0;

              return (
                <div key={budget.category} className="min-w-0 space-y-2">
                  <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between sm:gap-2">
                    <span className="truncate text-sm font-medium">
                      {budget.category}
                    </span>
                    <span className="shrink-0 text-xs text-muted-foreground sm:text-sm">
                      {formatCurrency(budget.spent)} /{" "}
                      {formatCurrency(budget.limit_amount)}
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-muted">
                    <div
                      className={`h-2 rounded-full transition-all ${
                        isOverBudget ? "bg-destructive/70" : "bg-primary/40"
                      }`}
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {budget.percentage.toFixed(0)}% used
                  </p>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface RecentTransactionsCardProps {
  transactions: DashboardRecentTransaction[];
}

export function RecentTransactionsCard({
  transactions,
}: RecentTransactionsCardProps) {
  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Recent Transactions</CardTitle>
        <CardDescription>Your latest financial activity</CardDescription>
      </CardHeader>
      <CardContent className="min-w-0">
        {transactions.length === 0 ? (
          <p className="py-3 text-center text-sm text-muted-foreground sm:py-4">
            No transactions yet. Add one on the Transactions page.
          </p>
        ) : (
          <div className="space-y-2 sm:space-y-3">
            {transactions.map((transaction) => (
              <div
                key={transaction.id}
                className="flex min-w-0 flex-col gap-2 rounded-lg border border-border px-3 py-2.5 sm:flex-row sm:items-center sm:justify-between sm:px-4 sm:py-3"
              >
                <div className="min-w-0 space-y-1">
                  <p className="truncate text-sm font-medium">
                    {transaction.description}
                  </p>
                  <div className="flex flex-wrap items-center gap-1.5 sm:gap-2">
                    <Badge
                      variant={
                        transaction.type === "income" ? "default" : "secondary"
                      }
                      className={
                        transaction.type === "income"
                          ? "max-w-full truncate bg-primary/10 text-primary hover:bg-primary/10"
                          : "max-w-full truncate"
                      }
                    >
                      {transaction.category}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {formatTransactionDate(transaction.transaction_date)}
                    </span>
                  </div>
                </div>
                <span
                  className={`shrink-0 self-end text-sm font-medium sm:self-center ${
                    transaction.type === "income"
                      ? "text-primary"
                      : "text-foreground"
                  }`}
                >
                  {transaction.type === "income" ? "+" : "-"}
                  {formatCurrency(transaction.amount)}
                </span>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
