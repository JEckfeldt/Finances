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
import type { TransactionType } from "@/lib/types";

export type TypeFilter = "all" | TransactionType;

interface TransactionFiltersProps {
  search: string;
  typeFilter: TypeFilter;
  categoryFilter: string;
  categories: string[];
  onSearchChange: (value: string) => void;
  onTypeFilterChange: (value: TypeFilter) => void;
  onCategoryFilterChange: (value: string) => void;
}

export function TransactionFilters({
  search,
  typeFilter,
  categoryFilter,
  categories,
  onSearchChange,
  onTypeFilterChange,
  onCategoryFilterChange,
}: TransactionFiltersProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <div className="space-y-2 sm:col-span-2 lg:col-span-1">
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
    </div>
  );
}
