import { cn } from "@/lib/utils";

interface DialogShellProps {
  children: React.ReactNode;
  className?: string;
}

export function DialogShell({ children, className }: DialogShellProps) {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-foreground/20 p-4 sm:p-6">
      <div
        className={cn(
          "flex min-h-full items-start justify-center py-4 sm:items-center sm:py-0",
          className
        )}
      >
        {children}
      </div>
    </div>
  );
}
