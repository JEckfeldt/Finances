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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { createTransaction } from "@/lib/api";
import { todayDateInputValue } from "@/lib/format";
import type { TransactionCreate } from "@/lib/types";

const transactionSchema = z.object({
  description: z.string().min(1, "Description is required").max(255),
  amount: z.number().positive("Amount must be greater than zero"),
  type: z.enum(["income", "expense"]),
  category: z.string().min(1, "Category is required").max(100),
  transaction_date: z.string().min(1, "Date is required"),
});

type TransactionFormValues = z.infer<typeof transactionSchema>;

interface TransactionFormProps {
  onSuccess: () => void | Promise<void>;
}

export function TransactionForm({ onSuccess }: TransactionFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<TransactionFormValues>({
    resolver: zodResolver(transactionSchema),
    defaultValues: {
      description: "",
      amount: undefined,
      type: "expense",
      category: "",
      transaction_date: todayDateInputValue(),
    },
  });

  const selectedType = watch("type");

  async function onSubmit(data: TransactionFormValues) {
    const payload: TransactionCreate = {
      description: data.description,
      amount: data.amount,
      type: data.type,
      category: data.category,
      transaction_date: data.transaction_date,
    };

    await createTransaction(payload);
    reset({
      description: "",
      amount: undefined,
      type: "expense",
      category: "",
      transaction_date: todayDateInputValue(),
    });
    await onSuccess();
  }

  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Add Transaction</CardTitle>
        <CardDescription>Record a new income or expense</CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="min-w-0 space-y-2 sm:col-span-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                className="h-10 w-full sm:h-8"
                placeholder="e.g. Grocery shopping"
                {...register("description")}
              />
              {errors.description && (
                <p className="text-sm text-destructive">
                  {errors.description.message}
                </p>
              )}
            </div>

            <div className="min-w-0 space-y-2">
              <Label htmlFor="amount">Amount</Label>
              <Input
                id="amount"
                className="h-10 w-full sm:h-8"
                type="number"
                step="0.01"
                min="0"
                placeholder="0.00"
                {...register("amount", { valueAsNumber: true })}
              />
              {errors.amount && (
                <p className="text-sm text-destructive">
                  {errors.amount.message}
                </p>
              )}
            </div>

            <div className="min-w-0 space-y-2">
              <Label htmlFor="transaction-type">Type</Label>
              <Select
                value={selectedType}
                onValueChange={(value) =>
                  setValue("type", value as "income" | "expense")
                }
              >
                <SelectTrigger id="transaction-type" className="h-10 w-full sm:h-8">
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="income">Income</SelectItem>
                  <SelectItem value="expense">Expense</SelectItem>
                </SelectContent>
              </Select>
              {errors.type && (
                <p className="text-sm text-destructive">
                  {errors.type.message}
                </p>
              )}
            </div>

            <div className="min-w-0 space-y-2">
              <Label htmlFor="transaction-date">Date</Label>
              <Input
                id="transaction-date"
                className="h-10 w-full sm:h-8"
                type="date"
                {...register("transaction_date")}
              />
              {errors.transaction_date && (
                <p className="text-sm text-destructive">
                  {errors.transaction_date.message}
                </p>
              )}
            </div>

            <div className="min-w-0 space-y-2 sm:col-span-2">
              <Label htmlFor="category">Category</Label>
              <Input
                id="category"
                className="h-10 w-full sm:h-8"
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

          <Button
            type="submit"
            className="h-10 w-full sm:h-8 sm:w-auto"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Adding..." : "Add Transaction"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
