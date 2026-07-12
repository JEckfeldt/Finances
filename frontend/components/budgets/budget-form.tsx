"use client";

import { zodResolver } from "@hookform/resolvers/zod";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createBudget } from "@/lib/api";
import type { BudgetCreate } from "@/lib/types";

const budgetSchema = z.object({
  category: z.string().min(1, "Category is required").max(100),
  limit_amount: z.number().positive("Limit must be greater than zero"),
});

type BudgetFormValues = z.infer<typeof budgetSchema>;

interface BudgetFormProps {
  onSuccess: () => void;
}

export function BudgetForm({ onSuccess }: BudgetFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<BudgetFormValues>({
    resolver: zodResolver(budgetSchema),
    defaultValues: {
      category: "",
      limit_amount: undefined,
    },
  });

  async function onSubmit(data: BudgetFormValues) {
    const payload: BudgetCreate = {
      category: data.category,
      limit_amount: data.limit_amount,
    };

    await createBudget(payload);
    reset();
    onSuccess();
  }

  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Add Budget</CardTitle>
        <CardDescription>Set a monthly spending limit for a category</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="min-w-0 space-y-2">
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                className="h-10 w-full sm:h-8"
                placeholder="e.g. Groceries, Transportation"
                {...register("category")}
              />
              {errors.category && (
                <p className="text-sm text-destructive">
                  {errors.category.message}
                </p>
              )}
            </div>

            <div className="min-w-0 space-y-2">
              <Label htmlFor="limit_amount">Monthly Limit</Label>
              <Input
                id="limit_amount"
                className="h-10 w-full sm:h-8"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                {...register("limit_amount", { valueAsNumber: true })}
              />
              {errors.limit_amount && (
                <p className="text-sm text-destructive">
                  {errors.limit_amount.message}
                </p>
              )}
            </div>
          </div>

          <Button
            type="submit"
            className="h-10 w-full sm:h-8 sm:w-auto"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Adding..." : "Add Budget"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
