"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { RefreshCw, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";

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
import type { AIInsightStatus } from "@/lib/parse-insights";
import type { AIInsightsResponse } from "@/lib/types";

const insightMarkdownComponents: Components = {
  p: ({ children }) => (
    <p className="text-sm leading-relaxed text-foreground">{children}</p>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-foreground">{children}</strong>
  ),
  ul: ({ children }) => (
    <ul className="list-disc space-y-2 pl-5 text-sm leading-relaxed text-foreground">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal space-y-2 pl-5 text-sm leading-relaxed text-foreground">
      {children}
    </ol>
  ),
  li: ({ children }) => <li className="break-words">{children}</li>,
};

function statusMessage(status: AIInsightStatus): string | null {
  switch (status) {
    case "loading":
      return "Generating insights...";
    case "success":
      return "Insights generated from your recent financial activity.";
    case "disabled":
      return null;
    case "error":
      return null;
    default:
      return null;
  }
}

export function AIInsightsCard() {
  const [data, setData] = useState<AIInsightsResponse | null>(null);
  const [status, setStatus] = useState<AIInsightStatus>("loading");
  const [error, setError] = useState<string | null>(null);
  const isFetchingRef = useRef(false);

  const loadInsights = useCallback(async () => {
    if (isFetchingRef.current) {
      return;
    }

    isFetchingRef.current = true;
    setStatus("loading");
    setError(null);

    try {
      const response = await getAIInsights();

      if (!response.enabled) {
        setData(response);
        setStatus("disabled");
        return;
      }

      if (!response.insights?.trim()) {
        setData(response);
        setStatus("error");
        setError("No insights were returned. Please try again.");
        return;
      }

      setData(response);
      setStatus("success");
    } catch (err) {
      setData(null);
      setStatus("error");
      setError(
        err instanceof Error ? err.message : "Failed to load AI insights"
      );
    } finally {
      isFetchingRef.current = false;
    }
  }, []);

  useEffect(() => {
    loadInsights();
  }, [loadInsights]);

  const statusLabel = statusMessage(status);

  return (
    <Card className="min-w-0">
      <CardHeader className="gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-1">
          <CardTitle className="flex items-center gap-2">
            <Sparkles className="size-4 shrink-0 text-primary" />
            AI Financial Insights
          </CardTitle>
          <CardDescription>
            Personalized guidance based on your recent activity
          </CardDescription>
          {statusLabel && (
            <p
              className={`text-xs ${
                status === "loading"
                  ? "text-muted-foreground"
                  : "text-primary/80"
              }`}
            >
              {statusLabel}
            </p>
          )}
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="h-10 w-full shrink-0 sm:h-8 sm:w-auto"
          onClick={loadInsights}
          disabled={status === "loading"}
        >
          <RefreshCw
            className={`size-4 ${status === "loading" ? "animate-spin" : ""}`}
          />
          Refresh Insights
        </Button>
      </CardHeader>
      <CardContent className="min-w-0">
        {status === "loading" ? (
          <div className="space-y-2">
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
            <Skeleton className="h-4 w-4/6" />
          </div>
        ) : status === "error" ? (
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
        ) : status === "disabled" ? (
          <p className="text-sm leading-relaxed text-muted-foreground">
            {data?.message ?? "AI insights are currently unavailable."}
          </p>
        ) : data?.insights ? (
          <div className="space-y-3 rounded-lg border border-border/70 bg-muted/20 px-3 py-3 sm:px-4 sm:py-4">
            <ReactMarkdown components={insightMarkdownComponents}>
              {data.insights}
            </ReactMarkdown>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            No insights are available right now.
          </p>
        )}
      </CardContent>
    </Card>
  );
}
