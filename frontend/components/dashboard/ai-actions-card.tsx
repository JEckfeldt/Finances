"use client";

import { useCallback, useRef, useState } from "react";
import { Loader2, MessageSquareText } from "lucide-react";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { executeAIAction } from "@/lib/api";
import { formatCurrency, formatTransactionDate } from "@/lib/format";
import type { AIActionResponse } from "@/lib/types";
import { cn } from "@/lib/utils";

type ActionCardStatus = "idle" | "loading" | "success" | "error" | "disabled";

function resolveErrorMessage(response: AIActionResponse): string {
  if (response.status === "parse_error" || response.status === "validation_error") {
    return (
      response.message ??
      "Could not process that request. Please try rephrasing your message."
    );
  }

  if (response.action?.intent === "unknown") {
    return (
      response.action.reason ??
      "That message could not be understood as a financial action."
    );
  }

  return response.message ?? "The action could not be completed.";
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

  if (data.action?.intent === "unknown" && data.action.reason) {
    return (
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
        {data.action.reason}
      </p>
    );
  }

  return null;
}

export function AIActionsCard() {
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

      if (response.status === "success") {
        setResult(response);
        setStatus("success");
        setMessage("");
        return;
      }

      setResult(response);
      setStatus("error");
      setError(resolveErrorMessage(response));
    } catch (err) {
      setResult(null);
      setStatus("error");
      setError(
        err instanceof Error ? err.message : "Failed to execute AI action"
      );
    } finally {
      isExecutingRef.current = false;
    }
  }, [message]);

  const isLoading = status === "loading";
  const canExecute = message.trim().length > 0 && !isLoading;

  return (
    <Card className="min-w-0">
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
            <p className="text-xs text-muted-foreground">Executing action...</p>
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
            placeholder='Try "I spent $42 on dinner" or "Create a $500 gas budget"'
            disabled={isLoading}
            className={cn(
              "min-h-24 w-full min-w-0 resize-y rounded-lg border border-input bg-transparent px-3 py-2 text-base transition-colors outline-none placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-not-allowed disabled:bg-input/50 disabled:opacity-50 md:text-sm dark:bg-input/30"
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

        {status === "disabled" && (
          <p className="text-sm leading-relaxed text-muted-foreground">
            {result?.message ?? "AI actions are currently unavailable."}
          </p>
        )}

        {status === "success" && result && (
          <div className="rounded-lg border border-border/70 bg-muted/20 px-3 py-3 sm:px-4 sm:py-4">
            <p className="text-sm font-medium text-primary">
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
