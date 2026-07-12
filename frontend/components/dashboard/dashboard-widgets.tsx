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
    <Card>
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <DollarSign className="size-4" />
          Current Balance
        </CardDescription>
        <CardTitle
          className={`text-3xl font-semibold ${
            isNegative ? "text-destructive" : "text-foreground"
          }`}
        >
          {formatCurrency(balance)}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
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
    <Card>
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <TrendingUp className="size-4 text-primary" />
          Income Summary
        </CardDescription>
        <CardTitle className="text-2xl font-semibold text-primary">
          {formatCurrency(income)}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
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
    <Card>
      <CardHeader>
        <CardDescription className="flex items-center gap-2">
          <TrendingDown className="size-4 text-destructive" />
          Expense Summary
        </CardDescription>
        <CardTitle className="text-2xl font-semibold">
          {formatCurrency(expenses)}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
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
    <Card>
      <CardHeader>
        <CardTitle>Budget Progress</CardTitle>
        <CardDescription>Spending against your budgets</CardDescription>
      </CardHeader>
      <CardContent>
        {budgets.length === 0 ? (
          <p className="py-4 text-center text-sm text-muted-foreground">
            No budgets yet. Create one on the Budgets page.
          </p>
        ) : (
          <div className="space-y-4">
            {budgets.map((budget) => {
              const percentage = Math.min(Math.max(budget.percentage, 0), 100);
              const isOverBudget = parseFloat(budget.remaining) < 0;

              return (
                <div key={budget.category} className="space-y-2">
                  <div className="flex justify-between gap-2 text-sm">
                    <span className="truncate font-medium">{budget.category}</span>
                    <span className="text-muted-foreground">
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
    <Card>
      <CardHeader>
        <CardTitle>Recent Transactions</CardTitle>
        <CardDescription>Your latest financial activity</CardDescription>
      </CardHeader>
      <CardContent>
        {transactions.length === 0 ? (
          <p className="py-4 text-center text-sm text-muted-foreground">
            No transactions yet. Add one on the Transactions page.
          </p>
        ) : (
          <div className="space-y-3">
            {transactions.map((transaction) => (
              <div
                key={transaction.id}
                className="flex flex-col gap-2 rounded-lg border border-border px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
              >
                <div className="min-w-0 space-y-1">
                  <p className="truncate text-sm font-medium">
                    {transaction.description}
                  </p>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge
                      variant={
                        transaction.type === "income" ? "default" : "secondary"
                      }
                      className={
                        transaction.type === "income"
                          ? "bg-primary/10 text-primary hover:bg-primary/10"
                          : ""
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
                  className={`shrink-0 text-sm font-medium ${
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
