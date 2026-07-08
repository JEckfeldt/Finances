"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ErrorState } from "@/components/ui/error-state";
import { TransactionEditDialog } from "@/components/transactions/transaction-edit-dialog";
import {
  TransactionFilters,
  type TypeFilter,
} from "@/components/transactions/transaction-filters";
import { TransactionForm } from "@/components/transactions/transaction-form";
import { TransactionList } from "@/components/transactions/transaction-list";
import { TransactionPagination } from "@/components/transactions/transaction-pagination";
import {
  deleteTransaction,
  getTransactionCategories,
  getTransactions,
} from "@/lib/api";
import type {
  SortOrder,
  Transaction,
  TransactionSortBy,
} from "@/lib/types";

const PAGE_SIZE = 25;

export default function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingTransaction, setEditingTransaction] =
    useState<Transaction | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState<TypeFilter>("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [sortBy, setSortBy] = useState<TransactionSortBy>("date");
  const [sortOrder, setSortOrder] = useState<SortOrder>("desc");
  const [categories, setCategories] = useState<string[]>([]);
  const [hasAnyTransactions, setHasAnyTransactions] = useState(false);

  useEffect(() => {
    const timer = window.setTimeout(() => setDebouncedSearch(search), 300);
    return () => window.clearTimeout(timer);
  }, [search]);

  const isFiltered = useMemo(
    () =>
      debouncedSearch.trim().length > 0 ||
      typeFilter !== "all" ||
      categoryFilter !== "all",
    [debouncedSearch, typeFilter, categoryFilter]
  );

  const loadCategories = useCallback(async () => {
    try {
      const data = await getTransactionCategories();
      setCategories(data);
    } catch {
      // Categories are used for filter dropdown; ignore fetch failures.
    }
  }, []);

  const loadTransactions = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);
      const data = await getTransactions({
        page,
        page_size: PAGE_SIZE,
        sort_by: sortBy,
        sort_order: sortOrder,
        search: debouncedSearch.trim() || undefined,
        type: typeFilter === "all" ? undefined : typeFilter,
        category: categoryFilter,
      });
      setTransactions(data.items);
      setTotalCount(data.total_count);
      setTotalPages(data.total_pages);

      if (!isFiltered && page === 1) {
        setHasAnyTransactions(data.total_count > 0);
      } else {
        setHasAnyTransactions((prev) => prev || data.total_count > 0);
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load transactions"
      );
    } finally {
      setIsLoading(false);
    }
  }, [page, sortBy, sortOrder, debouncedSearch, typeFilter, categoryFilter, isFiltered]);

  useEffect(() => {
    loadCategories();
  }, [loadCategories]);

  useEffect(() => {
    loadTransactions();
  }, [loadTransactions]);

  useEffect(() => {
    setPage(1);
  }, [debouncedSearch, typeFilter, categoryFilter, sortBy, sortOrder]);

  function clearFilters() {
    setSearch("");
    setDebouncedSearch("");
    setTypeFilter("all");
    setCategoryFilter("all");
    setPage(1);
  }

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
      await loadCategories();
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
        onSuccess={async () => {
          await loadCategories();
          await loadTransactions();
        }}
      />

      <Card>
        <CardHeader>
          <CardTitle>All Transactions</CardTitle>
          <CardDescription>
            {totalCount} transaction{totalCount !== 1 ? "s" : ""} total
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {(hasAnyTransactions || isFiltered) && (
            <TransactionFilters
              search={search}
              typeFilter={typeFilter}
              categoryFilter={categoryFilter}
              sortBy={sortBy}
              sortOrder={sortOrder}
              categories={categories}
              onSearchChange={setSearch}
              onTypeFilterChange={setTypeFilter}
              onCategoryFilterChange={setCategoryFilter}
              onSortByChange={setSortBy}
              onSortOrderChange={setSortOrder}
            />
          )}

          {error ? (
            <ErrorState message={error} onRetry={loadTransactions} />
          ) : (
            <>
              <TransactionList
                transactions={transactions}
                isLoading={isLoading}
                hasAnyTransactions={hasAnyTransactions || totalCount > 0}
                isFiltered={isFiltered}
                onEdit={setEditingTransaction}
                onDelete={handleDelete}
                onClearFilters={clearFilters}
                deletingId={deletingId}
              />
              <TransactionPagination
                page={page}
                totalPages={totalPages}
                totalCount={totalCount}
                onPageChange={setPage}
              />
            </>
          )}
        </CardContent>
      </Card>

      <TransactionEditDialog
        transaction={editingTransaction}
        onClose={() => setEditingTransaction(null)}
        onSuccess={async () => {
          await loadCategories();
          await loadTransactions();
        }}
      />
    </div>
  );
}
