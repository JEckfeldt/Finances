import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

function BudgetPlaceholder({ name }: { name: string }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{name}</CardTitle>
        <CardDescription>Budget tracking coming soon</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Spent</span>
            <span className="text-muted-foreground/50">—</span>
          </div>
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Limit</span>
            <span className="text-muted-foreground/50">—</span>
          </div>
          <div className="h-2 rounded-full bg-muted">
            <div className="h-2 w-0 rounded-full bg-primary/40" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default function BudgetsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Budgets</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage your spending limits and track progress
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <BudgetPlaceholder name="Groceries" />
        <BudgetPlaceholder name="Transportation" />
        <BudgetPlaceholder name="Entertainment" />
        <BudgetPlaceholder name="Utilities" />
        <BudgetPlaceholder name="Healthcare" />
        <BudgetPlaceholder name="Savings" />
      </div>
    </div>
  );
}
