import "./global.css";
import { RootProvider } from "fumadocs-ui/provider/next";
import type { Metadata } from "next/types";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: {
    template: "%s | LOLPaths",
    default: "LOLPaths",
  },
  description:
    "A YAML-first catalog of filesystem paths and file characteristics associated with sensitive artifacts.",
  metadataBase: new URL("https://lolpaths.dev/"),
};

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="flex min-h-screen flex-col">
        <RootProvider
          theme={{
            enabled: false,
            defaultTheme: "dark",
          }}
        >
          {children}
        </RootProvider>
      </body>
    </html>
  );
}
