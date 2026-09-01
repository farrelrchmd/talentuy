"use client";

import { Layers, MessageCircleQuestion } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";

import { KeywordNetwork, VolumeChart } from "@/components/charts";
import { ActiveFilterChips } from "@/components/filter-panel";
import { PageHeader } from "@/components/shell";
import {
  Card,
  ChangeBadge,
  ChartSkeleton,
  Drawer,
  ErrorState,
  InlineLoader,
  NoResultState,
  SentimentBadge,
  Skeleton,
  Tag,
} from "@/components/ui";
import { useTopicDetail, useTopics } from "@/hooks/useApi";
import { useFilters } from "@/hooks/useFilters";
import { useReportMeta } from "@/hooks/useMeta";
import { ApiError } from "@/lib/api";
import { cn } from "@/lib/cn";
import { formatNumber, formatPercent, formatShortDate, truncate } from "@/lib/format";
import type { TopicRow } from "@/lib/types";

function TopicCard({
  topic,
  isFiltered,
  onOpen,
  onFilter,
}: {
  topic: TopicRow;
  isFiltered: boolean;
  onOpen: () => void;
  onFilter: () => void;
}) {
  const topSentiments = Object.entries(topic.sentiment_counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

  return (
    <article
      className={cn(
        "flex flex-col rounded-card border bg-surface p-4 transition hover:shadow-card",
        isFiltered ? "border-primary" : "border-line",
      )}
    >
      <div className="flex items-start gap-2.5">
        <span
          className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full"
          style={{ backgroundColor: topic.color }}
          aria-hidden
        />
        <div className="min-w-0 flex-1">
          <h3 className="text-[14px] font-semibold leading-snug text-ink">{topic.name}</h3>
          <p className="mt-0.5 text-[11px] text-muted">
            {formatNumber(topic.count)} post · {formatPercent(topic.share)} percakapan
          </p>
        </div>
        <ChangeBadge value={topic.change_percent} />
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-1.5">
        <SentimentBadge label={topic.dominant_sentiment} />
        {topic.negative_share >= 25 && (
          <Tag tone="warning">{formatPercent(topic.negative_share)} negatif</Tag>
        )}
      </div>

      {/* Bar komposisi sentimen tetap disertai angka agar tidak bergantung warna. */}
      <div className="mt-3">
        <div className="flex h-1.5 overflow-hidden rounded-full bg-surface-muted">
          {topSentiments.map(([label, count]) => (
            <span
              key={label}
              style={{
                width: `${(count / Math.max(topic.count, 1)) * 100}%`,
                backgroundColor:
                  label === "Positif"
                    ? "#16a34a"
                    : label === "Negatif"
                      ? "#dc2626"
                      : label === "Tidak Yakin"
                        ? "#f59e0b"
                        : "#64748b",
              }}
              aria-hidden
            />
          ))}
        </div>
        <p className="mt-1.5 text-[11px] text-muted">
          {topSentiments.map(([label, count]) => `${label} ${count}`).join(" · ")}
        </p>
      </div>

      <div className="mt-3 flex items-center gap-3 border-t border-line pt-2.5">
        <button
          type="button"
          onClick={onOpen}
          className="text-xs font-medium text-primary hover:underline"
        >
          Buka detail
        </button>
        <button
          type="button"
          onClick={onFilter}
          className="text-xs text-muted hover:text-ink"
        >
          {isFiltered ? "Hapus dari filter" : "Tambahkan ke filter"}
        </button>
      </div>
    </article>
  );
}

function TopicExplorer() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { apiParams, filters, toggleValue, setFilters, reset } = useFilters();
  const { data, isLoading, isError, error, refetch } = useTopics(apiParams);
  useReportMeta(data?.meta);

  const [activeSlug, setActiveSlug] = useState<string | null>(null);
  const { data: detail, isLoading: detailLoading } = useTopicDetail(activeSlug, apiParams);

  // Mendukung tautan drill-down dari Overview (?fokus=slug).
  useEffect(() => {
    const focus = searchParams.get("fokus");
    if (focus) setActiveSlug(focus);
  }, [searchParams]);

  if (isError) {
    return (
      <>
        <PageHeader title="Eksplorasi Topik" />
        <Card title="Data tidak dapat ditampilkan">
          <ErrorState
            message={error instanceof ApiError ? error.userMessage : "Kesalahan tidak terduga."}
            onRetry={() => refetch()}
          />
        </Card>
      </>
    );
  }

  const isEmpty = !isLoading && data && data.topics.length === 0;

  return (
    <>
      <PageHeader
        title="Eksplorasi Topik"
        subtitle={
          data
            ? `${formatNumber(data.total_posts)} post terklasifikasi ke dalam ${data.topics.length} topik pada ${data.meta.period_label}.`
            : "Menyiapkan daftar topik…"
        }
        badge={data && <Tag tone="warning">{data.meta.is_synthetic ? "DATA DEMO" : "DATA LIVE"}</Tag>}
      />

      <ActiveFilterChips />

      {isEmpty ? (
        <Card title="Tidak ada topik pada filter ini">
          <NoResultState query={filters.q} onReset={reset} />
        </Card>
      ) : (
        <div className="grid gap-4">
          <section aria-label="Daftar topik">
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
              {isLoading || !data
                ? Array.from({ length: 6 }).map((_, index) => (
                    <Skeleton key={index} className="h-[186px] w-full rounded-card" />
                  ))
                : data.topics.map((topic) => (
                    <TopicCard
                      key={topic.slug}
                      topic={topic}
                      isFiltered={filters.topics.includes(topic.slug)}
                      onOpen={() => setActiveSlug(topic.slug)}
                      onFilter={() => toggleValue("topics", topic.slug)}
                    />
                  ))}
            </div>
          </section>

          <div className="grid gap-4 lg:grid-cols-2">
            <Card
              title="Kata kunci terkait"
              description="Klik kata untuk menjadikannya kata kunci pencarian."
              definition="Kata kunci diekstraksi per post. Garis penghubung berarti dua kata sering muncul pada post yang sama."
            >
              {isLoading || !data ? (
                <ChartSkeleton height={300} />
              ) : (
                <KeywordNetwork
                  nodes={data.related_keywords.nodes}
                  edges={data.related_keywords.edges}
                  activeKeyword={filters.q}
                  onSelect={(keyword) => {
                    setFilters({ q: keyword });
                    router.push("/post");
                  }}
                />
              )}
            </Card>

            <Card
              title="Pertanyaan yang sering muncul"
              description="Kandidat konten FAQ untuk komunikasi rekrutmen."
              definition="Post ber-intent 'Pertanyaan' diurutkan berdasarkan relevansi pencarian."
            >
              {isLoading || !data ? (
                <div className="space-y-2">
                  {Array.from({ length: 6 }).map((_, index) => (
                    <Skeleton key={index} className="h-12 w-full" />
                  ))}
                </div>
              ) : data.questions.length === 0 ? (
                <p className="py-6 text-center text-xs text-muted">
                  Belum ada pertanyaan terdeteksi pada filter ini.
                </p>
              ) : (
                <ul className="space-y-2.5">
                  {data.questions.map((question) => (
                    <li key={question.external_post_id} className="flex gap-2.5">
                      <MessageCircleQuestion
                        className="mt-0.5 h-4 w-4 shrink-0 text-primary"
                        aria-hidden
                      />
                      <div className="min-w-0">
                        <p className="text-[13px] leading-relaxed text-ink">
                          {truncate(question.text, 130)}
                        </p>
                        <p className="mt-0.5 text-[11px] text-muted">
                          {question.topic} · {question.job_role}
                        </p>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </Card>
          </div>
        </div>
      )}

      <Drawer
        open={Boolean(activeSlug)}
        onClose={() => setActiveSlug(null)}
        title={detail?.topic?.name ?? "Detail topik"}
        subtitle={
          detail?.topic
            ? `${formatNumber(detail.topic.count)} post · ${formatPercent(detail.topic.share)} dari percakapan periode ini`
            : undefined
        }
        width="max-w-2xl"
        footer={
          activeSlug && (
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="tp-btn tp-btn-primary"
                onClick={() => {
                  setFilters({ topics: [activeSlug] });
                  router.push("/post");
                }}
              >
                Lihat post topik ini
              </button>
              <button
                type="button"
                className="tp-btn"
                onClick={() => {
                  toggleValue("topics", activeSlug);
                  setActiveSlug(null);
                }}
              >
                {filters.topics.includes(activeSlug)
                  ? "Hapus dari filter global"
                  : "Tambahkan ke filter global"}
              </button>
            </div>
          )
        }
      >
        {detailLoading || !detail ? (
          <InlineLoader label="Memuat detail topik" />
        ) : (
          <div className="space-y-5">
            <div className="rounded-lg border border-primary/20 bg-primary-soft px-3.5 py-3">
              <p className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-primary">
                <Layers className="h-3.5 w-3.5" aria-hidden />
                Draft ringkasan (perlu ditinjau)
              </p>
              <p className="mt-1.5 text-[13px] leading-relaxed text-ink">
                {detail.suggested_summary}
              </p>
            </div>

            <section>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
                Volume harian topik
              </h3>
              <VolumeChart series={detail.series} peaks={detail.peaks} height={180} />
            </section>

            <div className="grid gap-4 sm:grid-cols-2">
              <section>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
                  Sentimen
                </h3>
                <ul className="space-y-1.5">
                  {detail.sentiment.map((item) => (
                    <li key={item.label} className="flex items-center justify-between gap-2">
                      <SentimentBadge label={item.label} />
                      <span className="tabular text-xs text-muted">
                        {formatNumber(item.count)} ({formatPercent(item.share)})
                      </span>
                    </li>
                  ))}
                </ul>
              </section>

              <section>
                <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
                  Kategori percakapan
                </h3>
                <ul className="space-y-1.5">
                  {detail.intents.slice(0, 5).map((item) => (
                    <li key={item.label} className="flex items-center justify-between gap-2 text-xs">
                      <span className="text-ink">{item.label}</span>
                      <span className="tabular text-muted">
                        {formatNumber(item.count)} ({formatPercent(item.share)})
                      </span>
                    </li>
                  ))}
                </ul>
              </section>
            </div>

            <section>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
                Jenis pekerjaan terkait
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {detail.job_roles.map((role) => (
                  <button
                    key={role.label}
                    type="button"
                    className="tp-chip transition hover:border-primary hover:text-primary"
                    onClick={() => toggleValue("job_roles", role.label)}
                  >
                    {role.label}
                    <span className="tabular text-muted">{formatNumber(role.count)}</span>
                  </button>
                ))}
              </div>
            </section>

            <section>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
                Kata kunci terkait
              </h3>
              <KeywordNetwork
                nodes={detail.related_keywords.nodes}
                edges={detail.related_keywords.edges}
                onSelect={(keyword) => {
                  setFilters({ q: keyword, topics: activeSlug ? [activeSlug] : [] });
                  setActiveSlug(null);
                  router.push("/post");
                }}
              />
            </section>

            <section>
              <h3 className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted">
                Contoh post representatif
              </h3>
              <ul className="space-y-2">
                {detail.questions.slice(0, 5).map((question) => (
                  <li
                    key={question.external_post_id}
                    className="rounded-lg border border-line px-3 py-2"
                  >
                    <p className="text-[13px] leading-relaxed text-ink">{question.text}</p>
                    <p className="mt-1 text-[11px] text-muted">
                      {question.job_role} · {formatShortDate(question.created_at)} ·{" "}
                      {question.external_post_id}
                    </p>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        )}
      </Drawer>
    </>
  );
}

export default function TopicPage() {
  return (
    <Suspense fallback={<InlineLoader label="Memuat eksplorasi topik" />}>
      <TopicExplorer />
    </Suspense>
  );
}
