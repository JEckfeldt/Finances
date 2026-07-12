"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useMediaQuery } from "@/hooks/use-media-query";
import { formatCurrency } from "@/lib/format";
import type { MonthlySpendingTrend } from "@/lib/types";

interface SpendingTrendsChartProps {
  data: MonthlySpendingTrend[];
}

export function SpendingTrendsChart({ data }: SpendingTrendsChartProps) {
  const isNarrow = useMediaQuery("(max-width: 639px)");
  const chartData = data.map((item) => ({
    month: item.month,
    expenses: parseFloat(item.total_expenses),
  }));

  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle>Financial Trends</CardTitle>
        <CardDescription>Monthly spending over the last 6 months</CardDescription>
      </CardHeader>
      <CardContent className="min-w-0 overflow-hidden">
        {chartData.length === 0 ? (
          <div className="flex h-44 items-center justify-center rounded-lg border border-dashed border-border bg-muted/30 sm:h-48">
            <p className="text-sm text-muted-foreground">
              No spending data yet
            </p>
          </div>
        ) : (
          <div className="h-52 w-full min-w-0 sm:h-60 lg:h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{
                  top: 8,
                  right: isNarrow ? 4 : 8,
                  left: isNarrow ? 0 : 0,
                  bottom: 0,
                }}
              >
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis
                  dataKey="month"
                  tick={{ fill: "var(--muted-foreground)", fontSize: isNarrow ? 10 : 12 }}
                  axisLine={false}
                  tickLine={false}
                  interval={isNarrow ? "preserveStartEnd" : 0}
                />
                <YAxis
                  width={isNarrow ? 36 : 44}
                  tick={{ fill: "var(--muted-foreground)", fontSize: isNarrow ? 10 : 12 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(value: number) =>
                    `$${value >= 1000 ? `${(value / 1000).toFixed(0)}k` : value}`
                  }
                />
                <Tooltip
                  formatter={(value) => formatCurrency(Number(value))}
                  labelStyle={{ color: "var(--foreground)" }}
                  contentStyle={{
                    backgroundColor: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: "0.5rem",
                    fontSize: isNarrow ? "12px" : "14px",
                  }}
                />
                <Bar
                  dataKey="expenses"
                  fill="oklch(0.55 0.12 155 / 0.7)"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
