"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { clearAuth } from "@/lib/auth";
import { getCurrentUser, logout } from "@/lib/api";
import {
  ArrowLeftRight,
  LayoutDashboard,
  LogOut,
  PiggyBank,
  Wallet,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { href: "/budgets", label: "Budgets", icon: PiggyBank },
];

interface SidebarNavContentProps {
  onNavigate?: () => void;
  onClose?: () => void;
}

export function SidebarNavContent({ onNavigate, onClose }: SidebarNavContentProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const user = await getCurrentUser();
        setEmail(user.email);
      } catch {
        setEmail(null);
      }
    }

    loadUser();
  }, []);

  async function handleLogout() {
    try {
      await logout();
    } catch {
      // Continue clearing client state even if the API call fails.
    }
    clearAuth();
    onNavigate?.();
    router.replace("/login");
  }

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex items-center gap-2.5 border-b border-border px-6 py-5">
        <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
          <Wallet className="size-5 text-primary" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate font-semibold text-foreground">Finance Tracker</p>
        </div>
        {onClose && (
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={onClose}
            aria-label="Close navigation menu"
            className="size-9 shrink-0 sm:size-7"
          >
            <X className="size-4" />
          </Button>
        )}
      </div>

      <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-4">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              onClick={() => onNavigate?.()}
              className={cn(
                "flex min-h-11 items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className="size-4 shrink-0" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border p-4">
        {email && (
          <p className="mb-3 truncate px-3 text-xs text-muted-foreground">
            Signed in as {email}
          </p>
        )}
        <Button
          variant="outline"
          className={cn(
            "w-full justify-start gap-2",
            onClose ? "h-10" : "h-8"
          )}
          onClick={handleLogout}
        >
          <LogOut className="size-4" />
          Log out
        </Button>
      </div>
    </div>
  );
}

export function SidebarNav() {
  return (
    <aside className="hidden h-full w-64 shrink-0 flex-col border-r border-border bg-card lg:flex">
      <SidebarNavContent />
    </aside>
  );
}
