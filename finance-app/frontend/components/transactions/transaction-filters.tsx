"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { SortOrder, TransactionSortBy, TransactionType } from "@/lib/types";

export type TypeFilter = "all" | TransactionType;

interface TransactionFiltersProps {
  search: string;
  typeFilter: TypeFilter;
  categoryFilter: string;
  sortBy: TransactionSortBy;
  sortOrder: SortOrder;
  categories: string[];
  onSearchChange: (value: string) => void;
  onTypeFilterChange: (value: TypeFilter) => void;
  onCategoryFilterChange: (value: string) => void;
  onSortByChange: (value: TransactionSortBy) => void;
  onSortOrderChange: (value: SortOrder) => void;
}

export function TransactionFilters({
  search,
  typeFilter,
  categoryFilter,
  sortBy,
  sortOrder,
  categories,
  onSearchChange,
  onTypeFilterChange,
  onCategoryFilterChange,
  onSortByChange,
  onSortOrderChange,
}: TransactionFiltersProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
      <div className="space-y-2 sm:col-span-2 lg:col-span-2 xl:col-span-2">
        <Label htmlFor="transaction-search">Search</Label>
        <Input
          id="transaction-search"
          placeholder="Search description or category"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
        />
      </div>

      <div className="space-y-2">
        <Label>Type</Label>
        <Select
          value={typeFilter}
          onValueChange={(value) =>
            onTypeFilterChange((value ?? "all") as TypeFilter)
          }
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="All types" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="income">Income</SelectItem>
            <SelectItem value="expense">Expense</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Category</Label>
        <Select
          value={categoryFilter}
          onValueChange={(value) => onCategoryFilterChange(value ?? "all")}
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="All categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All categories</SelectItem>
            {categories.map((category) => (
              <SelectItem key={category} value={category}>
                {category}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Sort by</Label>
        <Select
          value={sortBy}
          onValueChange={(value) =>
            onSortByChange((value ?? "date") as TransactionSortBy)
          }
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Sort by" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="date">Date</SelectItem>
            <SelectItem value="amount">Amount</SelectItem>
            <SelectItem value="category">Category</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Order</Label>
        <Select
          value={sortOrder}
          onValueChange={(value) =>
            onSortOrderChange((value ?? "desc") as SortOrder)
          }
        >
          <SelectTrigger className="w-full">
            <SelectValue placeholder="Order" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="desc">Descending</SelectItem>
            <SelectItem value="asc">Ascending</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
