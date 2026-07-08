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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { updateTransaction } from "@/lib/api";
import type { Transaction, TransactionUpdate } from "@/lib/types";
import { CategoryAutocomplete } from "@/components/transactions/category-autocomplete";

const transactionEditSchema = z.object({
  description: z.string().min(1, "Description is required").max(255),
  amount: z.number().positive("Amount must be greater than zero"),
  type: z.enum(["income", "expense"]),
  category: z.string().min(1, "Category is required").max(100),
});

type TransactionEditFormValues = z.infer<typeof transactionEditSchema>;

interface TransactionEditDialogProps {
  transaction: Transaction | null;
  categorySuggestions?: string[];
  onClose: () => void;
  onSuccess: () => void | Promise<void>;
}

export function TransactionEditDialog({
  transaction,
  categorySuggestions = [],
  onClose,
  onSuccess,
}: TransactionEditDialogProps) {
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors, isSubmitting },
  } = useForm<TransactionEditFormValues>({
    resolver: zodResolver(transactionEditSchema),
  });

  const selectedType = watch("type");
  const categoryValue = watch("category");

  useEffect(() => {
    if (transaction) {
      reset({
        description: transaction.description,
        amount: parseFloat(transaction.amount),
        type: transaction.type,
        category: transaction.category,
      });
    }
  }, [transaction, reset]);

  if (!transaction) {
    return null;
  }

  const transactionId = transaction.id;

  async function onSubmit(data: TransactionEditFormValues) {
    const payload: TransactionUpdate = {
      description: data.description,
      amount: data.amount,
      type: data.type,
      category: data.category,
    };

    await updateTransaction(transactionId, payload);
    await onSuccess();
    onClose();
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-foreground/20 px-4">
      <Card className="w-full max-w-lg">
        <CardHeader>
          <CardTitle>Edit Transaction</CardTitle>
          <CardDescription>Update transaction details</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="space-y-2 sm:col-span-2">
                <Label htmlFor="edit-description">Description</Label>
                <Input id="edit-description" {...register("description")} />
                {errors.description && (
                  <p className="text-sm text-destructive">
                    {errors.description.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="edit-amount">Amount</Label>
                <Input
                  id="edit-amount"
                  type="number"
                  step="0.01"
                  min="0"
                  {...register("amount", { valueAsNumber: true })}
                />
                {errors.amount && (
                  <p className="text-sm text-destructive">
                    {errors.amount.message}
                  </p>
                )}
              </div>

              <div className="space-y-2">
                <Label>Type</Label>
                <Select
                  value={selectedType}
                  onValueChange={(value) =>
                    setValue("type", value as "income" | "expense")
                  }
                >
                  <SelectTrigger className="w-full">
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="income">Income</SelectItem>
                    <SelectItem value="expense">Expense</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2 sm:col-span-2">
                <Label htmlFor="edit-category">Category</Label>
                <CategoryAutocomplete
                  id="edit-category"
                  value={categoryValue ?? ""}
                  onChange={(value) =>
                    setValue("category", value, { shouldValidate: true })
                  }
                  suggestions={categorySuggestions}
                />
                {errors.category && (
                  <p className="text-sm text-destructive">
                    {errors.category.message}
                  </p>
                )}
              </div>
            </div>

            <div className="flex justify-end gap-2">
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
    </div>
  );
}
