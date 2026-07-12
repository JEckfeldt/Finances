"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { DialogShell } from "@/components/ui/dialog-shell";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { updateBudget } from "@/lib/api";
import type { Budget, BudgetUpdate } from "@/lib/types";

const budgetEditSchema = z.object({
  category: z.string().min(1, "Category is required").max(100),
  limit_amount: z.number().positive("Limit must be greater than zero"),
});

type BudgetEditFormValues = z.infer<typeof budgetEditSchema>;

interface BudgetEditDialogProps {
  budget: Budget | null;
  onClose: () => void;
  onSuccess: () => void;
}

export function BudgetEditDialog({
  budget,
  onClose,
  onSuccess,
}: BudgetEditDialogProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<BudgetEditFormValues>({
    resolver: zodResolver(budgetEditSchema),
  });

  useEffect(() => {
    if (budget) {
      reset({
        category: budget.category,
        limit_amount: parseFloat(budget.limit_amount),
      });
    }
  }, [budget, reset]);

  if (!budget) {
    return null;
  }

  const budgetId = budget.id;

  async function onSubmit(data: BudgetEditFormValues) {
    const payload: BudgetUpdate = {
      category: data.category,
      limit_amount: data.limit_amount,
    };

    await updateBudget(budgetId, payload);
    onSuccess();
    onClose();
  }

  return (
    <DialogShell>
      <Card className="max-h-[calc(100dvh-2rem)] w-full min-w-0 max-w-md overflow-y-auto">
        <CardHeader>
          <CardTitle>Edit Budget</CardTitle>
          <CardDescription>Update category or monthly limit</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-category">Category</Label>
              <Input id="edit-category" {...register("category")} />
              {errors.category && (
                <p className="text-sm text-destructive">
                  {errors.category.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-limit">Monthly Limit</Label>
              <Input
                id="edit-limit"
                type="number"
                step="0.01"
                min="0"
                {...register("limit_amount", { valueAsNumber: true })}
              />
              {errors.limit_amount && (
                <p className="text-sm text-destructive">
                  {errors.limit_amount.message}
                </p>
              )}
            </div>

            <div className="flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
              <Button type="button" variant="outline" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? "Saving..." : "Save Changes"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </DialogShell>
  );
}
