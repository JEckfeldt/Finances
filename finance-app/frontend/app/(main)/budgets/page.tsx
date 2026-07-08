"use client";

import { useCallback, useEffect, useState } from "react";

import { BudgetCard } from "@/components/budgets/budget-card";
import { BudgetEditDialog } from "@/components/budgets/budget-edit-dialog";
import { BudgetForm } from "@/components/budgets/budget-form";
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

export default function BudgetsPage() {
  const [budgets, setBudgets] = useState<BudgetWithProgress[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingBudget, setEditingBudget] = useState<Budget | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const loadBudgets = useCallback(async () => {
    try {
      setError(null);
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
      setIsLoading(true);
      await loadBudgets();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete budget");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Budgets</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage your spending limits and track progress
        </p>
      </div>

      <BudgetForm
        onSuccess={() => {
          setIsLoading(true);
          loadBudgets();
        }}
      />

      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}

      {isLoading ? (
        <p className="py-8 text-center text-sm text-muted-foreground">
          Loading budgets...
        </p>
      ) : budgets.length === 0 ? (
        <p className="py-8 text-center text-sm text-muted-foreground">
          No budgets yet. Add your first budget above.
        </p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
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
          setIsLoading(true);
          loadBudgets();
        }}
      />
    </div>
  );
}
