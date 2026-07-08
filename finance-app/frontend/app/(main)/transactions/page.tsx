"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { TransactionEditDialog } from "@/components/transactions/transaction-edit-dialog";
import {
  TransactionFilters,
  type TypeFilter,
} from "@/components/transactions/transaction-filters";
import { TransactionForm } from "@/components/transactions/transaction-form";
import { TransactionList } from "@/components/transactions/transaction-list";
import { deleteTransaction, getTransactions } from "@/lib/api";
import type { Transaction } from "@/lib/types";

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingTransaction, setEditingTransaction] =
    useState<Transaction | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("all");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const loadTransactions = useCallback(async () => {
    try {
      setError(null);
      const data = await getTransactions();
      setTransactions(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load transactions"
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTransactions();
  }, [loadTransactions]);

  const categories = useMemo(
    () =>
      [...new Set(transactions.map((transaction) => transaction.category))].sort(
        (a, b) => a.localeCompare(b)
      ),
    [transactions]
  );

  const filteredTransactions = useMemo(() => {
    const query = search.trim().toLowerCase();

    return transactions.filter((transaction) => {
      const matchesSearch =
        query.length === 0 ||
        transaction.description.toLowerCase().includes(query) ||
        transaction.category.toLowerCase().includes(query);

      const matchesType =
        typeFilter === "all" || transaction.type === typeFilter;

      const matchesCategory =
        categoryFilter === "all" || transaction.category === categoryFilter;

      return matchesSearch && matchesType && matchesCategory;
    });
  }, [transactions, search, typeFilter, categoryFilter]);

  async function handleDelete(transaction: Transaction) {
    const confirmed = window.confirm(
      `Delete "${transaction.description}"? This cannot be undone.`
    );
    if (!confirmed) {
      return;
    }

    try {
      setDeletingId(transaction.id);
      await deleteTransaction(transaction.id);
      setIsLoading(true);
      await loadTransactions();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete transaction");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Transactions</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          View and manage your financial transactions
        </p>
      </div>

      <TransactionForm
        onSuccess={() => {
          setIsLoading(true);
          loadTransactions();
        }}
      />

      <Card>
        <CardHeader>
          <CardTitle>All Transactions</CardTitle>
          <CardDescription>
            {filteredTransactions.length} of {transactions.length} transaction
            {transactions.length !== 1 ? "s" : ""} shown
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {transactions.length > 0 && (
            <TransactionFilters
              search={search}
              typeFilter={typeFilter}
              categoryFilter={categoryFilter}
              categories={categories}
              onSearchChange={setSearch}
              onTypeFilterChange={setTypeFilter}
              onCategoryFilterChange={setCategoryFilter}
            />
          )}

          {error ? (
            <p className="py-8 text-center text-sm text-destructive">{error}</p>
          ) : (
            <TransactionList
              transactions={filteredTransactions}
              isLoading={isLoading}
              hasAnyTransactions={transactions.length > 0}
              onEdit={setEditingTransaction}
              onDelete={handleDelete}
              deletingId={deletingId}
            />
          )}
        </CardContent>
      </Card>

      <TransactionEditDialog
        transaction={editingTransaction}
        onClose={() => setEditingTransaction(null)}
        onSuccess={() => {
          setIsLoading(true);
          loadTransactions();
        }}
      />
    </div>
  );
}
