"use client";

import { useTranslations } from "next-intl";
import { useQuery } from "@tanstack/react-query";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { getStats } from "@/lib/api/stats";
import type { StatsResponse } from "@/lib/api/stats";
import { useAuth } from "@/lib/hooks/use-auth";

function StatCard({
  label,
  value,
  unit,
}: {
  label: string;
  value: string | number;
  unit?: string;
}) {
  return (
    <Card className="flex flex-col gap-1 p-5">
      <span className="text-2xl font-bold tabular-nums">
        {value}
        {unit && <span className="ml-1 text-base font-normal text-muted-foreground">{unit}</span>}
      </span>
      <span className="text-sm text-muted-foreground">{label}</span>
    </Card>
  );
}

function StatsSkeleton() {
  return (
    <div className="space-y-10">
      <div className="flex flex-col items-center gap-2">
        <Skeleton className="h-16 w-48" />
        <Skeleton className="h-5 w-64" />
      </div>
      {[0, 1, 2].map((i) => (
        <div key={i} className="space-y-4">
          <Skeleton className="h-7 w-40" />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[0, 1, 2, 3].map((j) => (
              <Skeleton key={j} className="h-24" />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

function fmt(value: number, decimals = 0): string {
  return value.toLocaleString("fr-FR", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function StatsContent({ stats }: { stats: StatsResponse }) {
  const t = useTranslations("stats");

  return (
    <div className="space-y-12">
      {/* North Star */}
      <div className="flex flex-col items-center gap-2 py-8 text-center">
        <p className="text-sm font-medium uppercase tracking-widest text-muted-foreground">
          {t("northStar.label")}
        </p>
        <p className="text-6xl font-bold tabular-nums">
          {fmt(stats.north_star_reliable_answers)}
        </p>
        <p className="max-w-md text-muted-foreground">{t("northStar.description")}</p>
      </div>

      {/* Fonctionnement */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">{t("fonctionnement.title")}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label={t("fonctionnement.indexingSuccessRate")}
            value={fmt(stats.fonctionnement.indexing_success_rate_percent, 1)}
            unit="%"
          />
          <StatCard
            label={t("fonctionnement.projectsWithDocuments")}
            value={fmt(stats.fonctionnement.projects_with_documents)}
          />
          <StatCard
            label={t("fonctionnement.totalDocumentSize")}
            value={fmt(stats.fonctionnement.total_document_size_mb, 1)}
            unit="Mo"
          />
          <StatCard
            label={t("fonctionnement.totalChunks")}
            value={fmt(stats.fonctionnement.total_chunks)}
          />
        </div>
      </section>

      {/* Usage */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">{t("usage.title")}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard label={t("usage.usersTotal")} value={fmt(stats.usage.users_total)} />
          <StatCard label={t("usage.usersActive30d")} value={fmt(stats.usage.users_active_30d)} />
          <StatCard
            label={t("usage.organizationsTotal")}
            value={fmt(stats.usage.organizations_total)}
          />
          <StatCard label={t("usage.projectsTotal")} value={fmt(stats.usage.projects_total)} />
          <StatCard
            label={t("usage.projectsPublished")}
            value={fmt(stats.usage.projects_published)}
          />
          <StatCard
            label={t("usage.conversationsTotal")}
            value={fmt(stats.usage.conversations_total)}
          />
          <StatCard
            label={t("usage.messagesTotal")}
            value={fmt(stats.usage.messages_total)}
          />
          <StatCard
            label={t("usage.documentsTotal")}
            value={fmt(stats.usage.documents_total)}
          />
        </div>
      </section>

      {/* Impact */}
      <section className="space-y-4">
        <h2 className="text-xl font-semibold">{t("impact.title")}</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            label={t("impact.reliableAnswersTotal")}
            value={fmt(stats.impact.reliable_answers_total)}
          />
          <StatCard
            label={t("impact.averageReliability")}
            value={fmt(stats.impact.average_reliability_percent, 1)}
            unit="%"
          />
          <StatCard
            label={t("impact.relevantAnswersRate")}
            value={fmt(stats.impact.relevant_answers_rate_percent, 1)}
            unit="%"
          />
          <StatCard
            label={t("impact.multiTurnRate")}
            value={fmt(stats.impact.multi_turn_conversations_rate_percent, 1)}
            unit="%"
          />
          <StatCard
            label={t("impact.averageSources")}
            value={fmt(stats.impact.average_sources_per_answer, 1)}
          />
        </div>
      </section>

      <p className="text-center text-xs text-muted-foreground">
        {t("generatedAt", {
          date: new Date(stats.generated_at).toLocaleString("fr-FR", {
            dateStyle: "long",
            timeStyle: "short",
          }),
        })}
      </p>
    </div>
  );
}

export function StatsPage() {
  const t = useTranslations("stats");
  const { token } = useAuth();
  const { data, isLoading, error } = useQuery({
    queryKey: ["stats"],
    queryFn: () => getStats(token!),
    enabled: !!token,
    staleTime: 5 * 60 * 1000,
  });

  return (
    <div className="mx-auto max-w-5xl px-4 py-10">
      <header className="mb-10 space-y-1">
        <h1 className="text-3xl font-bold">{t("pageTitle")}</h1>
        <p className="text-muted-foreground">{t("pageDescription")}</p>
      </header>

      {isLoading && <StatsSkeleton />}

      {error && (
        <p className="text-destructive">{t("loadError")}</p>
      )}

      {data && <StatsContent stats={data} />}
    </div>
  );
}
