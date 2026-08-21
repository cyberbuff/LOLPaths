import { HomeLayout } from "fumadocs-ui/layouts/home";
import type { ReactNode } from "react";
import { baseOptions } from "@/app/layout.config";

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <HomeLayout
      {...baseOptions}
      links={[
        {
          text: "Docs",
          url: "/docs",
        },
        {
          text: "Rules",
          url: "/docs/rules",
        },
        {
          text: "Contributing",
          url: "/docs/contributing",
        },
      ]}
    >
      {children}
    </HomeLayout>
  );
}
