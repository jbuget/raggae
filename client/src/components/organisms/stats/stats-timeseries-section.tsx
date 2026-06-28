"use client";

import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { Skeleton } from "@/components/ui/skeleton";
import { SparklineCard } from "@/components/atoms/stats/sparkline";
import { getStatsTimeseries } from "@/lib/api/stats";
import { useAuth } from "@/lib/hooks/use-auth";

const DEFAULT_DAYS = 90;

function SectionSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[0, 1, 2, 3, 4, 5].map((i) => (
        <Skeleton key={i} className="h-36" />
      ))}
    </div>
  );
}

export function StatsTimeseriesSection() {
  const t = useTranslations("stats");
  const { token } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ["stats", "timeseries", DEFAULT_DAYS],
    queryFn: () => getStatsTimeseries(token!, DEFAULT_DAYS),
    enabled: !!token,
    staleTime: 5 * 60 * 1000,
  });

  return (
    <section className="space-y-4">
      <div className="space-y-1">
        <h2 className="text-xl font-semibold">{t("timeseries.title")}</h2>
        <p className="text-sm text-muted-foreground">{t("timeseries.description")}</p>
      </div>

      {isLoading && <SectionSkeleton />}

      {error && <p className="text-destructive">{t("loadError")}</p>}

      {data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          <SparklineCard label={t("timeseries.userMessages")} points={data.user_messages} />
          <SparklineCard label={t("timeseries.conversations")} points={data.conversations} />
          <SparklineCard
            label={t("timeseries.dailyActiveUsers")}
            points={data.daily_active_users}
          />
          <SparklineCard label={t("timeseries.reliableAnswers")} points={data.reliable_answers} />
          <SparklineCard
            label={t("timeseries.documentsIndexed")}
            points={data.documents_indexed}
          />
          <SparklineCard label={t("timeseries.projectsCreated")} points={data.projects_created} />
        </div>
      )}
    </section>
  );
}
