import { Button } from "@/components/ui/button";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="min-w-0 rounded-lg border border-dashed border-destructive/30 bg-destructive/5 px-4 py-8 text-center sm:px-6 sm:py-10">
      <p className="text-sm font-medium text-destructive">{message}</p>
      {onRetry && (
        <Button
          variant="outline"
          className="mt-4 h-10 w-full sm:h-8 sm:w-auto"
          onClick={onRetry}
        >
          Try again
        </Button>
      )}
    </div>
  );
}
