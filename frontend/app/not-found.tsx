import { Button } from "@/components/ui/button";
import { Wallet } from "lucide-react";
import Link from "next/link";

export default function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md space-y-8 text-center">
        <div className="flex flex-col items-center gap-3">
          <div className="flex size-12 items-center justify-center rounded-xl bg-primary/10">
            <Wallet className="size-6 text-primary" />
          </div>
          <p className="text-7xl font-semibold tracking-tight text-primary sm:text-8xl">
            404
          </p>
          <div className="space-y-2">
            <h1 className="text-2xl font-semibold tracking-tight text-foreground">
              Page Not Found
            </h1>
            <p className="text-sm text-muted-foreground">
              The page you are looking for does not exist or may have been moved.
            </p>
          </div>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row sm:justify-center">
          <Link href="/dashboard">
            <Button className="w-full sm:w-auto">Go to Dashboard</Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" className="w-full sm:w-auto">
              Go to Login
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
