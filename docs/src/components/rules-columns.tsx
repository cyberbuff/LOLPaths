"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { ArrowUpDown, FileCode2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Rule } from "@/lib/catalog";

function platforms(rule: Rule): string[] {
  return [...new Set(rule.match?.paths?.flatMap((path) => path.platforms) ?? [])].sort();
}

const sensitivityRank: Record<Rule["sensitivity"], number> = {
  informational: 0,
  low: 1,
  medium: 2,
  high: 3,
  critical: 4,
};

function sensitivityBadgeClass(sensitivity: Rule["sensitivity"]): string {
  const base =
    "inline-flex rounded-md border px-2 py-0.5 font-mono text-xs font-medium capitalize";

  if (sensitivity === "critical") {
    return `${base} border-red-500/40 bg-red-500/15 text-red-200`;
  }
  if (sensitivity === "high") {
    return `${base} border-amber-500/40 bg-amber-500/15 text-amber-200`;
  }
  if (sensitivity === "medium") {
    return `${base} border-sky-500/40 bg-sky-500/15 text-sky-200`;
  }
  if (sensitivity === "low") {
    return `${base} border-emerald-500/40 bg-emerald-500/15 text-emerald-200`;
  }
  return `${base} border-zinc-500/40 bg-zinc-500/15 text-zinc-200`;
}

export const columns: ColumnDef<Rule>[] = [
  {
    accessorKey: "id",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="h-auto p-0 font-medium"
        >
          Rule ID
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => {
      return <div className="font-mono text-sm">{row.getValue("id")}</div>;
    },
  },
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="h-auto p-0 font-medium"
        >
          Rule
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => {
      return (
        <div>
          <div className="flex items-center gap-2 font-medium">
            <FileCode2 className="h-4 w-4 text-fd-primary" />
            {row.original.name}
          </div>
          <div className="mt-1 max-w-[34rem] truncate text-xs text-muted-foreground">
            {row.original.description?.trim()}
          </div>
        </div>
      );
    },
  },
  {
    accessorKey: "category",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="h-auto p-0 font-medium"
        >
          Category
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => {
      return <div className="font-mono text-sm">{row.getValue("category")}</div>;
    },
  },
  {
    accessorKey: "sensitivity",
    sortingFn: (first, second) => {
      return (
        sensitivityRank[first.original.sensitivity] -
        sensitivityRank[second.original.sensitivity]
      );
    },
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="h-auto p-0 font-medium"
        >
          Sensitivity
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      );
    },
    cell: ({ row }) => {
      const sensitivity = row.original.sensitivity;

      return (
        <span className={sensitivityBadgeClass(sensitivity)}>{sensitivity}</span>
      );
    },
  },
  {
    id: "platforms",
    accessorFn: platforms,
    header: "Platforms",
    cell: ({ row }) => {
      return (
        <div className="text-xs text-muted-foreground">
          {platforms(row.original).join(", ")}
        </div>
      );
    },
  },
];
