"use client";

import { Pencil, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatCurrency, formatDate } from "@/lib/format";
import type { Transaction } from "@/lib/types";

interface TransactionListProps {
  transactions: Transaction[];
  isLoading?: boolean;
  hasAnyTransactions?: boolean;
  onEdit: (transaction: Transaction) => void;
  onDelete: (transaction: Transaction) => void;
  deletingId?: number | null;
}

export function TransactionList({
  transactions,
  isLoading,
  hasAnyTransactions = false,
  onEdit,
  onDelete,
  deletingId,
}: TransactionListProps) {
  if (isLoading) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        Loading transactions...
      </p>
    );
  }

  if (!hasAnyTransactions) {
    return (
      <div className="rounded-lg border border-dashed border-border px-6 py-10 text-center">
        <p className="text-sm font-medium text-foreground">No transactions yet</p>
        <p className="mt-1 text-sm text-muted-foreground">
          Add your first transaction using the form above to start tracking your
          finances.
        </p>
      </div>
    );
  }

  if (transactions.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-border px-6 py-10 text-center">
        <p className="text-sm font-medium text-foreground">
          No matching transactions
        </p>
        <p className="mt-1 text-sm text-muted-foreground">
          Try adjusting your search or filters to find what you are looking for.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Description</TableHead>
            <TableHead>Category</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Date</TableHead>
            <TableHead className="text-right">Amount</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {transactions.map((transaction) => (
            <TableRow key={transaction.id}>
              <TableCell className="font-medium">
                {transaction.description}
              </TableCell>
              <TableCell>{transaction.category}</TableCell>
              <TableCell>
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
                  {transaction.type}
                </Badge>
              </TableCell>
              <TableCell className="text-muted-foreground">
                {formatDate(transaction.created_at)}
              </TableCell>
              <TableCell
                className={`text-right font-medium ${
                  transaction.type === "income"
                    ? "text-primary"
                    : "text-foreground"
                }`}
              >
                {transaction.type === "income" ? "+" : "-"}
                {formatCurrency(transaction.amount)}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex justify-end gap-1">
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => onEdit(transaction)}
                    aria-label={`Edit ${transaction.description}`}
                  >
                    <Pencil className="size-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    onClick={() => onDelete(transaction)}
                    disabled={deletingId === transaction.id}
                    aria-label={`Delete ${transaction.description}`}
                  >
                    <Trash2 className="size-4 text-destructive" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
