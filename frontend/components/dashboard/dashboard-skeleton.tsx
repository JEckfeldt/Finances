import { Skeleton } from "@/components/ui/skeleton";

export function DashboardSkeleton() {
  return (
    <div className="space-y-5 sm:space-y-6 lg:space-y-8">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 sm:gap-4 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <Skeleton key={index} className="h-28 sm:h-32" />
        ))}
      </div>

      <div className="grid grid-cols-1 gap-3 sm:gap-4 lg:grid-cols-2">
        <Skeleton className="h-64 sm:h-72" />
        <Skeleton className="h-64 sm:h-72" />
      </div>

      <div className="grid grid-cols-1 gap-3 sm:gap-4 lg:grid-cols-2">
        <Skeleton className="h-52 sm:h-64 lg:h-72" />
        <Skeleton className="h-52 sm:h-60 lg:h-64" />
      </div>
    </div>
  );
}
