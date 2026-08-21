"use client";

import { FileCode2, Gauge, Layers, Monitor, Tag } from "lucide-react";
import { createColumnConfigHelper } from "@/components/data-table-filter/core/filters";
import type { Rule } from "@/lib/catalog";

const dtf = createColumnConfigHelper<Rule>();

function option(value: string) {
  return {
    label: value,
    value,
  };
}

function platforms(rule: Rule): string[] {
  return [...new Set(rule.match?.paths?.flatMap((path) => path.platforms) ?? [])].sort();
}

export const columnsConfig = [
  dtf
    .text()
    .id("name")
    .accessor((row) => row.name)
    .displayName("Rule")
    .icon(FileCode2)
    .build(),
  dtf
    .text()
    .id("id")
    .accessor((row) => row.id)
    .displayName("Rule ID")
    .icon(Tag)
    .build(),
  dtf
    .option()
    .id("category")
    .accessor((row) => row.category)
    .displayName("Category")
    .icon(Layers)
    .transformOptionFn(option)
    .build(),
  dtf
    .option()
    .id("sensitivity")
    .accessor((row) => row.sensitivity)
    .displayName("Sensitivity")
    .icon(Gauge)
    .options([
      { label: "Critical", value: "critical" },
      { label: "High", value: "high" },
      { label: "Medium", value: "medium" },
      { label: "Low", value: "low" },
      { label: "Informational", value: "informational" },
    ])
    .build(),
  dtf
    .multiOption()
    .id("platforms")
    .accessor(platforms)
    .displayName("Platforms")
    .icon(Monitor)
    .options([
      { label: "Windows", value: "windows" },
      { label: "Linux", value: "linux" },
      { label: "macOS", value: "macos" },
    ])
    .build(),
] as const;
