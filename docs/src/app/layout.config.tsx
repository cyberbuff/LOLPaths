import type { BaseLayoutProps } from "fumadocs-ui/layouts/shared";

export const baseOptions: BaseLayoutProps = {
  nav: {
    title: (
      <span className="flex items-center gap-2 font-semibold tracking-normal">
        <span className="font-mono text-fd-primary">/</span>
        <span>LOLPaths</span>
      </span>
    ),
  },
  themeSwitch: {
    enabled: false,
  },
  githubUrl: "https://github.com/cyberbuff/lolpaths",
};
