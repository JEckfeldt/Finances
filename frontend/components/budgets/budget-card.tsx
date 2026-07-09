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
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Category
          </p>
          <CardTitle className="mt-1">{budget.category}</CardTitle>
        </div>
        <div className="flex gap-1">
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => onEdit(budget)}
            aria-label={`Edit ${budget.category} budget`}
          >
            <Pencil className="size-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={() => onDelete(budget)}
            disabled={isDeleting}
            aria-label={`Delete ${budget.category} budget`}
          >
            <Trash2 className="size-4 text-destructive" />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Budget</span>
            <span className="font-medium">
              {formatCurrency(budget.limit_amount)}
            </span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Spent</span>
            <span className="font-medium">{formatCurrency(budget.spent)}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Remaining</span>
            <span
              className={`font-medium ${
                isOverBudget ? "text-destructive" : "text-primary"
              }`}
            >
              {formatCurrency(budget.remaining)}
            </span>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Progress</span>
              <span>{budget.percentage.toFixed(0)}%</span>
            </div>
            <div className="h-2 rounded-full bg-muted">
              <div
                className={`h-2 rounded-full transition-all ${
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
