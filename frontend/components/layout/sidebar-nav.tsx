"use client";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { clearAuth, getEmail, setAuth, getToken } from "@/lib/auth";
import { getCurrentUser } from "@/lib/api";
import {
  ArrowLeftRight,
  LayoutDashboard,
  LogOut,
  PiggyBank,
  Wallet,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/transactions", label: "Transactions", icon: ArrowLeftRight },
  { href: "/budgets", label: "Budgets", icon: PiggyBank },
];

export function SidebarNav() {
  const pathname = usePathname();
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    async function loadUser() {
      try {
        const user = await getCurrentUser();
        setEmail(user.email);
        const token = getToken();
        if (token) {
          setAuth(token, user.email);
        }
      } catch {
        setEmail(getEmail());
      }
    }

    loadUser();
  }, []);

  function handleLogout() {
    clearAuth();
    router.replace("/login");
  }

  return (
    <aside className="flex h-full w-64 flex-col border-r border-border bg-card">
      <div className="flex items-center gap-2.5 border-b border-border px-6 py-5">
        <div className="flex size-9 items-center justify-center rounded-lg bg-primary/10">
          <Wallet className="size-5 text-primary" />
        </div>
        <div>
          <p className="font-semibold text-foreground">Finance Tracker</p>
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 p-4">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className="size-4" />
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
          className="w-full justify-start gap-2"
          onClick={handleLogout}
        >
          <LogOut className="size-4" />
          Log out
        </Button>
      </div>
    </aside>
  );
}
