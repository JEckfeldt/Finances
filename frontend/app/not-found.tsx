import { Button } from "@/components/ui/button";
import { Wallet } from "lucide-react";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center overflow-x-hidden bg-background px-4 py-6 sm:py-8">
      <div className="w-full min-w-0 max-w-md space-y-6 text-center sm:space-y-8">
        <div className="flex flex-col items-center gap-3">
          <div className="flex size-12 items-center justify-center rounded-xl bg-primary/10">
            <Wallet className="size-6 text-primary" />
          </div>
          <p className="text-6xl font-semibold tracking-tight text-primary sm:text-7xl lg:text-8xl">
            404
          </p>
          <div className="min-w-0 space-y-2">
            <h1 className="text-xl font-semibold tracking-tight text-foreground sm:text-2xl">
              Page Not Found
            </h1>
            <p className="text-sm text-muted-foreground">
              The page you are looking for does not exist or may have been moved.
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link href="/dashboard" className="w-full sm:w-auto">
            <Button className="h-10 w-full sm:h-8 sm:w-auto">
              Go to Dashboard
            </Button>
          </Link>
          <Link href="/login" className="w-full sm:w-auto">
            <Button variant="outline" className="h-10 w-full sm:h-8 sm:w-auto">
              Go to Login
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
