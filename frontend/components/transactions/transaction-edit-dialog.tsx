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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { updateTransaction } from "@/lib/api";
import type { Transaction, TransactionUpdate } from "@/lib/types";

const transactionEditSchema = z.object({
  description: z.string().min(1, "Description is required").max(255),
  amount: z.number().positive("Amount must be greater than zero"),
  type: z.enum(["income", "expense"]),
  category: z.string().min(1, "Category is required").max(100),
  transaction_date: z.string().min(1, "Date is required"),
});

type TransactionEditFormValues = z.infer<typeof transactionEditSchema>;

interface TransactionEditDialogProps {
  transaction: Transaction | null;
  onClose: () => void;
  onSuccess: () => void | Promise<void>;
}

export function TransactionEditDialog({
  transaction,
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

  useEffect(() => {
    if (transaction) {
      reset({
        description: transaction.description,
        amount: parseFloat(transaction.amount),
        type: transaction.type,
        category: transaction.category,
        transaction_date: transaction.transaction_date,
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
      transaction_date: data.transaction_date,
    };

    await updateTransaction(transactionId, payload);
    await onSuccess();
    onClose();
  }

  return (
    <DialogShell>
      <Card className="max-h-[calc(100dvh-2rem)] w-full min-w-0 max-w-lg overflow-y-auto">
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
                  value={selectedType ?? transaction.type}
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

              <div className="space-y-2">
                <Label htmlFor="edit-transaction-date">Date</Label>
                <Input
                  id="edit-transaction-date"
                  type="date"
                  {...register("transaction_date")}
                />
                {errors.transaction_date && (
                  <p className="text-sm text-destructive">
                    {errors.transaction_date.message}
                  </p>
                )}
              </div>

              <div className="space-y-2 sm:col-span-2">
                <Label htmlFor="edit-category">Category</Label>
                <Input
                  id="edit-category"
                  placeholder="e.g. Food, Salary, Rent"
                  {...register("category")}
                />
                {errors.category && (
                  <p className="text-sm text-destructive">
                    {errors.category.message}
                  </p>
                )}
              </div>
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
