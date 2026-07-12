"use client";

import { useCallback, useEffect, useState } from "react";

import { BudgetCard } from "@/components/budgets/budget-card";
import { BudgetEditDialog } from "@/components/budgets/budget-edit-dialog";
import { BudgetForm } from "@/components/budgets/budget-form";
import { ErrorState } from "@/components/ui/error-state";
import { Skeleton } from "@/components/ui/skeleton";
import {
  deleteBudget,
  getBudgetProgress,
  getBudgets,
} from "@/lib/api";
import type { Budget, BudgetWithProgress } from "@/lib/types";

function mergeBudgetsWithProgress(
  budgets: Budget[],
  progress: Awaited<ReturnType<typeof getBudgetProgress>>
): BudgetWithProgress[] {
  const progressByCategory = new Map(
    progress.map((item) => [item.category, item])
  );

  return budgets.map((budget) => {
    const stats = progressByCategory.get(budget.category);
    return {
      ...budget,
      spent: stats?.spent ?? "0.00",
      remaining: stats?.remaining ?? budget.limit_amount,
      percentage: stats?.percentage ?? 0,
    };
  });
}

function BudgetSkeletonGrid() {
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
      {Array.from({ length: 3 }).map((_, index) => (
        <Skeleton key={index} className="h-52 sm:h-56" />
      ))}
    </div>
  );
}

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<BudgetWithProgress[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingBudget, setEditingBudget] = useState<Budget | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const loadBudgets = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);
      const [budgetList, progress] = await Promise.all([
        getBudgets(),
        getBudgetProgress(),
      ]);
      setBudgets(mergeBudgetsWithProgress(budgetList, progress));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load budgets");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadBudgets();
  }, [loadBudgets]);

  async function handleDelete(budget: BudgetWithProgress) {
    const confirmed = window.confirm(
      `Delete the ${budget.category} budget? This cannot be undone.`
    );
    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(budget.id);
      await deleteBudget(budget.id);
      await loadBudgets();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete budget");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="space-y-5 sm:space-y-6 lg:space-y-8">
      <div>
        <h1 className="text-xl font-semibold tracking-tight sm:text-2xl">Budgets</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage your spending limits and track progress
        </p>
      </div>

      <BudgetForm
        onSuccess={() => {
          loadBudgets();
        }}
      />

      {error && <ErrorState message={error} onRetry={loadBudgets} />}

      {isLoading ? (
        <BudgetSkeletonGrid />
      ) : budgets.length === 0 ? (
        <div className="rounded-lg border border-dashed border-border px-4 py-8 text-center sm:px-6 sm:py-10">
          <p className="text-sm font-medium text-foreground">No budgets yet</p>
          <p className="mt-1 text-sm text-muted-foreground">
            Add your first budget above to start tracking spending limits.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3 [&>*]:min-w-0">
          {budgets.map((budget) => (
            <BudgetCard
              key={budget.id}
              budget={budget}
              onEdit={setEditingBudget}
              onDelete={handleDelete}
              isDeleting={deletingId === budget.id}
            />
          ))}
        </div>
      )}

      <BudgetEditDialog
        budget={editingBudget}
        onClose={() => setEditingBudget(null)}
        onSuccess={() => {
          loadBudgets();
        }}
      />
    </div>
  );
}
