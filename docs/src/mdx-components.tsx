import * as FilesComponents from "fumadocs-ui/components/files";
import * as TabsComponents from "fumadocs-ui/components/tabs";
import defaultMdxComponents from "fumadocs-ui/mdx";
import { Database, FileCode2, ShieldCheck, Terminal } from "lucide-react";
import type { MDXComponents } from "mdx/types";

export function getMDXComponents(components?: MDXComponents): MDXComponents {
  return {
    ...defaultMdxComponents,
    ...TabsComponents,
    ...FilesComponents,
    Database,
    FileCode2,
    ShieldCheck,
    Terminal,
    ...components,
  };
}
