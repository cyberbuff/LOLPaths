import { docs } from "@/.source";
import { loader } from "fumadocs-core/source";
import { FileCode2, icons } from "lucide-react";
import { createElement } from "react";

const extraIcons = { FileCode2 };

export const source = loader({
  baseUrl: "/docs",
  source: docs.toFumadocsSource(),
  icon(icon) {
    if (!icon) {
      return;
    }

    if (icon in icons) {
      return createElement(icons[icon as keyof typeof icons]);
    }

    if (icon in extraIcons) {
      return createElement(extraIcons[icon as keyof typeof extraIcons]);
    }
  },
});
