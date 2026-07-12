"use client";

import { Pencil, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatCurrency, formatTransactionDate } from "@/lib/format";
import type { Transaction } from "@/lib/types";

interface TransactionListProps {
  transactions: Transaction[];
  isLoading?: boolean;
  hasAnyTransactions?: boolean;
  isFiltered?: boolean;
  onEdit: (transaction: Transaction) => void;
  onDelete: (transaction: Transaction) => void;
  onClearFilters?: () => void;
  deletingId?: number | null;
}

function TransactionActions({
  transaction,
  onEdit,
  onDelete,
  deletingId,
  className,
}: {
  transaction: Transaction;
  onEdit: (transaction: Transaction) => void;
  onDelete: (transaction: Transaction) => void;
  deletingId?: number | null;
  className?: string;
}) {
  return (
    <div className={className}>
      <Button
        variant="ghost"
        size="icon-sm"
        className="size-9 sm:size-7"
        onClick={() => onEdit(transaction)}
        aria-label={`Edit ${transaction.description}`}
      >
        <Pencil className="size-4" />
      </Button>
      <Button
        variant="ghost"
        size="icon-sm"
        className="size-9 sm:size-7"
        onClick={() => onDelete(transaction)}
        disabled={deletingId === transaction.id}
        aria-label={`Delete ${transaction.description}`}
      >
        <Trash2 className="size-4 text-destructive" />
      </Button>
    </div>
  );
}

function TransactionTypeBadge({ type }: { type: Transaction["type"] }) {
  return (
    <Badge
      variant={type === "income" ? "default" : "secondary"}
      className={
        type === "income"
          ? "bg-primary/10 text-primary hover:bg-primary/10"
          : ""
      }
    >
      {type}
    </Badge>
  );
}

function TransactionAmount({
  transaction,
  className,
}: {
  transaction: Transaction;
  className?: string;
}) {
  return (
    <span
      className={`font-medium ${
        transaction.type === "income" ? "text-primary" : "text-foreground"
      } ${className ?? ""}`}
    >
      {transaction.type === "income" ? "+" : "-"}
      {formatCurrency(transaction.amount)}
    </span>
  );
}

function LoadingSkeletons() {
  return (
    <>
      <div className="space-y-3 lg:hidden">
        {Array.from({ length: 5 }).map((_, index) => (
          <Skeleton key={index} className="h-28 w-full" />
        ))}
      </div>
      <div className="hidden space-y-3 lg:block">
        {Array.from({ length: 5 }).map((_, index) => (
          <Skeleton key={index} className="h-12 w-full" />
        ))}
      </div>
    </>
  );
}

function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="rounded-lg border border-dashed border-border px-4 py-8 text-center sm:px-6 sm:py-10">
      <p className="text-sm font-medium text-foreground">{title}</p>
      <p className="mt-1 text-sm text-muted-foreground">{description}</p>
      {action}
    </div>
  );
}

function TransactionCards({
  transactions,
  onEdit,
  onDelete,
  deletingId,
}: {
  transactions: Transaction[];
  onEdit: (transaction: Transaction) => void;
  onDelete: (transaction: Transaction) => void;
  deletingId?: number | null;
}) {
  return (
    <div className="space-y-3 lg:hidden">
      {transactions.map((transaction) => (
        <div
          key={transaction.id}
          className="min-w-0 rounded-lg border border-border px-3 py-3 sm:px-4"
        >
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0 space-y-1">
              <p className="truncate text-sm font-medium">
                {transaction.description}
              </p>
              <p className="truncate text-xs text-muted-foreground">
                {transaction.category}
              </p>
            </div>
            <TransactionAmount
              transaction={transaction}
              className="shrink-0 text-sm"
            />
          </div>

          <div className="mt-2 flex flex-wrap items-center gap-2">
            <TransactionTypeBadge type={transaction.type} />
            <span className="text-xs text-muted-foreground">
              {formatTransactionDate(transaction.transaction_date)}
            </span>
          </div>

          <TransactionActions
            transaction={transaction}
            onEdit={onEdit}
            onDelete={onDelete}
            deletingId={deletingId}
            className="mt-3 flex justify-end gap-1 border-t border-border pt-3"
          />
        </div>
      ))}
    </div>
  );
}

function TransactionTable({
  transactions,
  onEdit,
  onDelete,
  deletingId,
}: {
  transactions: Transaction[];
  onEdit: (transaction: Transaction) => void;
  onDelete: (transaction: Transaction) => void;
  deletingId?: number | null;
}) {
  return (
    <div className="hidden min-w-0 lg:block">
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
              <TableCell className="max-w-[12rem] truncate font-medium">
                {transaction.description}
              </TableCell>
              <TableCell className="max-w-[8rem] truncate">
                {transaction.category}
              </TableCell>
              <TableCell>
                <TransactionTypeBadge type={transaction.type} />
              </TableCell>
              <TableCell className="text-muted-foreground">
                {formatTransactionDate(transaction.transaction_date)}
              </TableCell>
              <TableCell className="text-right">
                <TransactionAmount transaction={transaction} />
              </TableCell>
              <TableCell className="text-right">
                <TransactionActions
                  transaction={transaction}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  deletingId={deletingId}
                  className="flex justify-end gap-1"
                />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

export function TransactionList({
  transactions,
  isLoading,
  hasAnyTransactions = false,
  isFiltered = false,
  onEdit,
  onDelete,
  onClearFilters,
  deletingId,
}: TransactionListProps) {
  if (isLoading) {
    return <LoadingSkeletons />;
  }

  if (!hasAnyTransactions) {
    return (
      <EmptyState
        title="No transactions yet"
        description="Add your first transaction using the form above to start tracking your finances."
      />
    );
  }

  if (transactions.length === 0) {
    return (
      <EmptyState
        title="No matching transactions"
        description="Try adjusting your search or filters to find what you are looking for."
        action={
          isFiltered && onClearFilters ? (
            <Button variant="outline" className="mt-4 h-10 w-full sm:h-8 sm:w-auto" onClick={onClearFilters}>
              Clear filters
            </Button>
          ) : undefined
        }
      />
    );
  }

  return (
    <div className="min-w-0">
      <TransactionCards
        transactions={transactions}
        onEdit={onEdit}
        onDelete={onDelete}
        deletingId={deletingId}
      />
      <TransactionTable
        transactions={transactions}
        onEdit={onEdit}
        onDelete={onDelete}
        deletingId={deletingId}
      />
    </div>
  );
}
