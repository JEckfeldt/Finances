"use client";

import { useCallback, useEffect, useState } from "react";
import { Sparkles } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { getAIInsights } from "@/lib/api";
import type { AIInsightsResponse } from "@/lib/types";

function formatInsightLines(insights: string): string[] {
  return insights
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean);
}

function stripBulletPrefix(line: string): string {
  return line.replace(/^[-*•]\s*/, "");
}

export function AIInsightsCard() {
  const [data, setData] = useState<AIInsightsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadInsights = useCallback(async () => {
    try {
      setError(null);
      setIsLoading(true);
      const response = await getAIInsights();
      setData(response);
    } catch (err) {
      setData(null);
      setError(
        err instanceof Error ? err.message : "Failed to load AI insights"
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadInsights();
  }, [loadInsights]);

  return (
    <Card className="min-w-0">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="size-4 shrink-0 text-primary" />
          AI Financial Insights
        </CardTitle>
        <CardDescription>
          Personalized guidance based on your recent activity
        </CardDescription>
      </CardHeader>
      <CardContent className="min-w-0">
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
          </div>
        ) : error ? (
          <div className="rounded-lg border border-dashed border-destructive/30 bg-destructive/5 px-4 py-6 text-center sm:px-6">
            <p className="text-sm font-medium text-destructive">{error}</p>
            <Button
              variant="outline"
              className="mt-4 h-10 w-full sm:h-8 sm:w-auto"
              onClick={loadInsights}
            >
              Try again
            </Button>
          </div>
        ) : data && !data.enabled ? (
          <p className="text-sm leading-relaxed text-muted-foreground">
            {data.message ?? "AI insights are currently unavailable."}
          </p>
        ) : data?.enabled && data.insights ? (
          <ul className="space-y-2.5 text-sm leading-relaxed text-foreground">
            {formatInsightLines(data.insights).map((line, index) => (
              <li key={`${index}-${line}`} className="flex gap-2">
                <span className="mt-0.5 shrink-0 text-primary">•</span>
                <span className="min-w-0 flex-1 break-words">
                  {stripBulletPrefix(line)}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-muted-foreground">
            No insights are available right now.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
