"use client";

import { useCallback, useRef, useState } from "react";
import { CheckCircle2, Loader2, MessageSquareText } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { executeAIAction } from "@/lib/api";
import { formatCurrency, formatTransactionDate } from "@/lib/format";
import type { AIActionResponse } from "@/lib/types";
import { cn } from "@/lib/utils";

type ActionCardStatus = "idle" | "loading" | "success" | "error" | "disabled";

type AIActionsCardProps = {
  onActionSuccess?: (response: AIActionResponse) => void | Promise<void>;
};

function resolveErrorMessage(
  response: AIActionResponse,
  fallback?: string
): string {
  if (response.message) {
    return response.message;
  }

  if (response.status === "parse_error") {
    return (
      "Could not understand that request. Try including an amount and purpose, " +
      'such as "I spent $42 at Costco" or "Make a $250 grocery budget".'
    );
  }

  if (response.status === "validation_error") {
    return (
      "The request was incomplete or unclear. Add an amount, category, and " +
      "what the money was for."
    );
  }

  return fallback ?? "The action could not be completed. Please try again.";
}

function resolveApiErrorMessage(error: unknown): string {
  if (!(error instanceof Error)) {
    return "Something went wrong while executing the action. Please try again.";
  }

  const message = error.message.toLowerCase();

  if (message.includes("rate limit")) {
    return "AI is temporarily busy. Please wait a moment and try again.";
  }

  if (message.includes("temporarily unavailable") || message.includes("503")) {
    return "AI is temporarily unavailable. Please try again shortly.";
  }

  if (message.includes("not authenticated") || message.includes("401")) {
    return "Your session expired. Please sign in again and retry.";
  }

  return error.message;
}

function ActionResultDetails({ data }: { data: AIActionResponse }) {
  if (data.transaction) {
    return (
      <dl className="mt-3 space-y-1.5 text-sm text-foreground">
        <div className="flex flex-wrap justify-between gap-x-4 gap-y-1">
          <dt className="text-muted-foreground">Description</dt>
          <dd className="font-medium">{data.transaction.description}</dd>
        </div>
        <div className="flex flex-wrap justify-between gap-x-4 gap-y-1">
          <dt className="text-muted-foreground">Amount</dt>
          <dd className="font-medium">
            {formatCurrency(data.transaction.amount)}
          </dd>
        </div>
        <div className="flex flex-wrap justify-between gap-x-4 gap-y-1">
          <dt className="text-muted-foreground">Category</dt>
          <dd className="font-medium">{data.transaction.category}</dd>
        </div>
        <div className="flex flex-wrap justify-between gap-x-4 gap-y-1">
          <dt className="text-muted-foreground">Date</dt>
          <dd className="font-medium">
            {formatTransactionDate(data.transaction.transaction_date)}
          </dd>
        </div>
      </dl>
    );
  }

  if (data.budget) {
    return (
      <dl className="mt-3 space-y-1.5 text-sm text-foreground">
        <div className="flex flex-wrap justify-between gap-x-4 gap-y-1">
          <dt className="text-muted-foreground">Category</dt>
          <dd className="font-medium">{data.budget.category}</dd>
        </div>
        <div className="flex flex-wrap justify-between gap-x-4 gap-y-1">
          <dt className="text-muted-foreground">Limit</dt>
          <dd className="font-medium">
            {formatCurrency(data.budget.limit_amount)}
          </dd>
        </div>
      </dl>
    );
  }

  return null;
}

export function AIActionsCard({ onActionSuccess }: AIActionsCardProps) {
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState<ActionCardStatus>("idle");
  const [result, setResult] = useState<AIActionResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const isExecutingRef = useRef(false);

  const executeAction = useCallback(async () => {
    const trimmed = message.trim();
    if (!trimmed || isExecutingRef.current) {
      return;
    }

    isExecutingRef.current = true;
    setStatus("loading");
    setError(null);
    setResult(null);

    try {
      const response = await executeAIAction(trimmed);

      if (!response.enabled) {
        setResult(response);
        setStatus("disabled");
        return;
      }

      if (response.status === "success" && (response.transaction || response.budget)) {
        setResult(response);
        setStatus("success");
        setMessage("");
        await onActionSuccess?.(response);
        return;
      }

      if (
        response.status === "parse_error" ||
        response.status === "validation_error"
      ) {
        setResult(response);
        setStatus("error");
        setError(resolveErrorMessage(response));
        return;
      }

      setResult(response);
      setStatus("error");
      setError(resolveErrorMessage(response, "No transaction or budget was created."));
    } catch (err) {
      setResult(null);
      setStatus("error");
      setError(resolveApiErrorMessage(err));
    } finally {
      isExecutingRef.current = false;
    }
  }, [message, onActionSuccess]);

  const isLoading = status === "loading";
  const canExecute = message.trim().length > 0 && !isLoading;

  return (
    <Card className={cn("min-w-0 transition-opacity", isLoading && "opacity-95")}>
      <CardHeader className="gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0 space-y-1">
          <CardTitle className="flex items-center gap-2">
            <MessageSquareText className="size-4 shrink-0 text-primary" />
            AI Financial Actions
          </CardTitle>
          <CardDescription>
            Describe a transaction or budget in plain language
          </CardDescription>
          {isLoading && (
            <p className="flex items-center gap-2 text-xs text-primary/80">
              <Loader2 className="size-3 animate-spin" />
              Interpreting your message and applying the action...
            </p>
          )}
        </div>
      </CardHeader>
      <CardContent className="min-w-0 space-y-4">
        <div className="space-y-2">
          <label htmlFor="ai-action-message" className="sr-only">
            Financial action message
          </label>
          <textarea
            id="ai-action-message"
            rows={3}
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            placeholder={
              'Try "I spent $42 at Costco", "I got paid $1800", or "Make a $250 grocery budget"'
            }
            disabled={isLoading}
            className={cn(
              "min-h-24 w-full min-w-0 resize-y rounded-lg border border-input bg-transparent px-3 py-2 text-base transition-colors outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:bg-input/50 disabled:opacity-50 md:text-sm dark:bg-input/30",
              isLoading && "animate-pulse"
            )}
          />
        </div>

        <Button
          type="button"
          className="h-10 w-full sm:h-8 sm:w-auto"
          onClick={executeAction}
          disabled={!canExecute}
        >
          {isLoading ? (
            <>
              <Loader2 className="size-4 animate-spin" />
              Executing...
            </>
          ) : (
            "Execute"
          )}
        </Button>

        {isLoading && (
          <div className="space-y-2 rounded-lg border border-border/70 bg-muted/20 px-3 py-3 sm:px-4">
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-4 w-1/2" />
          </div>
        )}

        {status === "disabled" && (
          <p className="text-sm leading-relaxed text-muted-foreground">
            {result?.message ?? "AI actions are currently unavailable."}
          </p>
        )}

        {status === "success" && result && (
          <div className="rounded-lg border border-primary/20 bg-primary/5 px-3 py-3 sm:px-4 sm:py-4">
            <p className="flex items-center gap-2 text-sm font-medium text-primary">
              <CheckCircle2 className="size-4 shrink-0" />
              {result.message ?? "Action completed."}
            </p>
            <ActionResultDetails data={result} />
          </div>
        )}

        {status === "error" && error && (
          <div className="rounded-lg border border-dashed border-destructive/30 bg-destructive/5 px-4 py-4 sm:px-6">
            <p className="text-sm font-medium text-destructive">{error}</p>
            <Button
              type="button"
              variant="outline"
              className="mt-4 h-10 w-full sm:h-8 sm:w-auto"
              onClick={() => {
                setStatus("idle");
                setError(null);
                setResult(null);
              }}
            >
              Dismiss
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
