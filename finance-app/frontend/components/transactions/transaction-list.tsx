"use client";

import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import type { Transaction } from "@/lib/types";

function formatCurrency(amount: string) {
  const value = parseFloat(amount);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatDate(dateString: string) {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(dateString));
}

interface TransactionListProps {
  transactions: Transaction[];
  isLoading?: boolean;
}

export function TransactionList({
  transactions,
  isLoading,
}: TransactionListProps) {
  if (isLoading) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        Loading transactions...
      </p>
    );
  }

  if (transactions.length === 0) {
    return (
      <p className="py-8 text-center text-sm text-muted-foreground">
        No transactions yet. Add your first transaction above.
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Description</TableHead>
          <TableHead>Category</TableHead>
          <TableHead>Type</TableHead>
          <TableHead>Date</TableHead>
          <TableHead className="text-right">Amount</TableHead>
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
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
