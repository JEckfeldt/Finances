"use client";

import { Pencil, Trash2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { BudgetWithProgress } from "@/lib/types";

function formatCurrency(amount: string | number) {
  const value = typeof amount === "string" ? parseFloat(amount) : amount;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

interface BudgetCardProps {
  budget: BudgetWithProgress;
  onEdit: (budget: BudgetWithProgress) => void;
  onDelete: (budget: BudgetWithProgress) => void;
  isDeleting?: boolean;
}

export function BudgetCard({
  budget,
  onEdit,
  onDelete,
  isDeleting,
}: BudgetCardProps) {
  const percentage = Math.min(Math.max(budget.percentage, 0), 100);
  const isOverBudget = parseFloat(budget.remaining) < 0;

  return (
    <Card className="min-w-0">
      <CardHeader className="flex flex-row items-start justify-between gap-3 sm:gap-4">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Category
          </p>
          <CardTitle className="mt-1 truncate">{budget.category}</CardTitle>
        </div>
        <div className="flex shrink-0 gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            className="size-9 sm:size-7"
            onClick={() => onEdit(budget)}
            aria-label={`Edit ${budget.category} budget`}
          >
            <Pencil className="size-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            className="size-9 sm:size-7"
            onClick={() => onDelete(budget)}
            disabled={isDeleting}
            aria-label={`Delete ${budget.category} budget`}
          >
            <Trash2 className="size-4 text-destructive" />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="min-w-0">
        <div className="space-y-2.5 sm:space-y-3">
          <div className="flex items-center justify-between gap-2 text-sm">
            <span className="text-muted-foreground">Budget</span>
            <span className="shrink-0 font-medium">
              {formatCurrency(budget.limit_amount)}
            </span>
          </div>
          <div className="flex items-center justify-between gap-2 text-sm">
            <span className="text-muted-foreground">Spent</span>
            <span className="shrink-0 font-medium">
              {formatCurrency(budget.spent)}
            </span>
          </div>
          <div className="flex items-center justify-between gap-2 text-sm">
            <span className="text-muted-foreground">Remaining</span>
            <span
              className={`shrink-0 font-medium ${
                isOverBudget ? "text-destructive" : "text-primary"
              }`}
            >
              {formatCurrency(budget.remaining)}
            </span>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between gap-2 text-xs text-muted-foreground">
              <span>Progress</span>
              <span className="shrink-0">{budget.percentage.toFixed(0)}%</span>
            </div>
            <div className="h-2.5 overflow-hidden rounded-full bg-muted sm:h-2">
              <div
                className={`h-full rounded-full transition-all ${
                  isOverBudget ? "bg-destructive/70" : "bg-primary/40"
                }`}
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
