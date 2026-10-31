import {
  QuartzComponent,
  QuartzComponentConstructor,
  QuartzComponentProps,
} from "../../quartz/components/types";
import {
  FullSlug,
  resolveRelative,
  joinSegments,
  pathToRoot,
} from "../../quartz/util/path";

import styles from "../styles.scss";

const links = [
  { label: "Rankings", slug: "index" },
  { label: "Shorts", slug: "short-candidates" },
  { label: "Companies", slug: "security-catalog" },
  { label: "Ideas", slug: "idea-catalog" },
  { label: "Research", slug: "research-catalog" },
] as const;

function linkIsActive(current: string, target: string): boolean {
  if (target === "ideas" || target === "podcasts") {
    return current === target || current.startsWith(`${target}/`);
  }
  if (target === "research-catalog") {
    return (
      current === target ||
      ["securities/", "relationships/", "strategies/", "raw/", "inbox/"].some(
        (prefix) => current.startsWith(prefix),
      )
    );
  }
  return current === target;
}

const DecisionNavigation: QuartzComponent = ({
  fileData,
}: QuartzComponentProps) => {
  const current = (fileData.slug ?? "index") as FullSlug;
  return (
    <div class="papertrader-header">
      <a
        class="papertrader-brand"
        href={resolveRelative(current, "index" as FullSlug)}
      >
        <img
          src={joinSegments(pathToRoot(current), "static/icon.svg")}
          width="42"
          height="42"
          alt=""
        />
        <span>
          PaperTrader<small>Research, made tangible</small>
        </span>
      </a>
      <nav class="papertrader-nav" aria-label="Primary navigation">
        {links.map((link) => {
          const { label, slug } = link;
          const active = linkIsActive(current, slug);
          const destination = slug as FullSlug;
          return (
            <a
              href={resolveRelative(current, destination)}
              class={active ? "active" : undefined}
              aria-current={active ? "page" : undefined}
            >
              {label}
            </a>
          );
        })}
      </nav>
    </div>
  );
};

DecisionNavigation.css = styles;

export default (() => DecisionNavigation) satisfies QuartzComponentConstructor;
