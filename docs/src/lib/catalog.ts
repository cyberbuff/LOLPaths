import { readFile } from "node:fs/promises";
import { join } from "node:path";

export type CatalogStats = {
  ruleCount: number;
  categoryCount: number;
  criticalCount: number;
  platformCount: number;
};

export type PathMatcher = {
  kind: "file" | "directory" | "glob";
  path: string;
  platforms: string[];
};

export type Rule = {
  id: string;
  name: string;
  description?: string;
  category: string;
  subcategory?: string;
  sensitivity: "informational" | "low" | "medium" | "high" | "critical";
  artifact_types?: string[];
  match?: {
    paths?: PathMatcher[];
  };
};

export async function getCatalogStats(): Promise<CatalogStats> {
  const statsPath = join(process.cwd(), "public", "api", "stats.json");
  const stats = JSON.parse(await readFile(statsPath, "utf8")) as {
    rules: number;
    categories: number;
    critical: number;
    platforms: string[];
  };

  return {
    ruleCount: stats.rules,
    categoryCount: stats.categories,
    criticalCount: stats.critical,
    platformCount: stats.platforms.length,
  };
}

export async function getRules(): Promise<Rule[]> {
  const rulesPath = join(process.cwd(), "public", "api", "rules.json");
  const catalog = JSON.parse(await readFile(rulesPath, "utf8")) as {
    rules: Rule[];
  };

  return catalog.rules;
}
