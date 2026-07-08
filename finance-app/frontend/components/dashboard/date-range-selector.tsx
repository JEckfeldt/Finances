"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DATE_RANGE_OPTIONS,
  type DateRangePreset,
} from "@/lib/date-range";

interface DateRangeSelectorProps {
  value: DateRangePreset;
  onChange: (value: DateRangePreset) => void;
}

export function DateRangeSelector({ value, onChange }: DateRangeSelectorProps) {
  return (
    <div className="space-y-2">
      <Label>Date range</Label>
      <Select
        value={value}
        onValueChange={(next) => onChange((next ?? "default") as DateRangePreset)}
      >
        <SelectTrigger className="w-full sm:w-56">
          <SelectValue placeholder="Select range" />
        </SelectTrigger>
        <SelectContent>
          {DATE_RANGE_OPTIONS.map((option) => (
            <SelectItem key={option.value} value={option.value}>
              {option.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
