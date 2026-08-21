import {
  ArrowRight,
  Database,
} from "lucide-react";
import Link from "next/link";
import { DataTableWithFilters } from "@/components/data-table-with-filters";
import { columns } from "@/components/rules-columns";
import { getCatalogStats, getRules } from "@/lib/catalog";

export default async function HomePage() {
  const [stats, rules] = await Promise.all([getCatalogStats(), getRules()]);

  return (
    <main className="min-h-screen overflow-hidden">
      <section className="path-grid relative px-6 py-20 sm:px-10 lg:px-16">
        <div className="mx-auto grid max-w-6xl gap-10 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div>
            <p className="mb-4 font-mono text-sm uppercase text-fd-primary">
              YAML-first sensitive path intelligence
            </p>
            <h1 className="max-w-3xl text-5xl font-semibold leading-tight tracking-normal sm:text-6xl">
              LOLPaths maps where sensitive artifacts live.
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-fd-muted-foreground">
              A community-maintained catalog for detection engineering, secret
              scanning, DLP, EDR monitoring, security validation, and filesystem
              guardrails.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/docs"
                className="inline-flex items-center gap-2 rounded-md bg-fd-primary px-4 py-2 text-sm font-medium text-fd-primary-foreground"
              >
                Read the docs
                <ArrowRight className="size-4" />
              </Link>
              <Link
                href="/docs/rules"
                className="inline-flex items-center gap-2 rounded-md border border-fd-border px-4 py-2 text-sm font-medium"
              >
                View Rules
              </Link>
            </div>
          </div>

          <div className="rounded-lg border border-fd-border bg-fd-background/80 p-5 shadow-2xl shadow-black/20 backdrop-blur">
            <div className="mb-4 flex items-center justify-between border-b border-fd-border pb-3">
              <span className="font-mono text-sm text-fd-muted-foreground">
                public/api/rules.json
              </span>
              <Database className="size-4 text-fd-primary" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <Stat label="rules" value={stats.ruleCount} />
              <Stat label="categories" value={stats.categoryCount} />
              <Stat label="critical" value={stats.criticalCount} />
              <Stat label="platforms" value={stats.platformCount} />
            </div>
          </div>
        </div>
      </section>

      <section className="container mx-auto px-6 pb-20 sm:px-10 lg:px-16">
        <div className="mb-6">
          <h2 className="text-2xl font-semibold tracking-normal">
            Rules Database
          </h2>
          <p className="mt-2 text-sm leading-6 text-fd-muted-foreground">
            Filter by rule, category, sensitivity, or platform.
          </p>
        </div>
        <DataTableWithFilters columns={columns} data={rules} />
      </section>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-fd-border bg-fd-muted/40 p-4">
      <div className="font-mono text-3xl font-semibold text-fd-primary">{value}</div>
      <div className="mt-1 text-sm text-fd-muted-foreground">{label}</div>
    </div>
  );
}
