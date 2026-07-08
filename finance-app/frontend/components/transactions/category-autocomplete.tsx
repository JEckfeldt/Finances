"use client";

import { mergeCategorySuggestions } from "@/lib/categories";
import { Input } from "@/components/ui/input";

interface CategoryAutocompleteProps {
  id: string;
  value: string;
  onChange: (value: string) => void;
  suggestions: string[];
  placeholder?: string;
}

export function CategoryAutocomplete({
  id,
  value,
  onChange,
  suggestions,
  placeholder = "e.g. Food, Salary, Rent",
}: CategoryAutocompleteProps) {
  const listId = `${id}-suggestions`;
  const options = mergeCategorySuggestions(suggestions, value);

  return (
    <>
      <Input
        id={id}
        list={listId}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
      />
      <datalist id={listId}>
        {options.map((category) => (
          <option key={category} value={category} />
        ))}
      </datalist>
    </>
  );
}
