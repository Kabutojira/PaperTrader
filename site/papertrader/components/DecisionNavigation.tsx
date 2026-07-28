import {
  QuartzComponent,
  QuartzComponentConstructor,
  QuartzComponentProps,
} from "../../quartz/components/types";
import { FullSlug, resolveRelative } from "../../quartz/util/path";

// @ts-ignore
import dashboardScript from "../scripts/dashboard.inline";
import styles from "../styles.scss";

const links = [
  { label: "Today", slug: "index" },
  { label: "Model portfolio", slug: "model-portfolio" },
  { label: "Securities", slug: "security-catalog" },
  { label: "Signals", slug: "signals" },
  { label: "Research", slug: "research-catalog" },
  { label: "Performance", slug: "performance" },
  { label: "System status", slug: "system-status" },
] as const;

function linkIsActive(current: string, target: string): boolean {
  if (target === "research-catalog") {
    return (
      current === target ||
      [
        "ideas/",
        "securities/",
        "relationships/",
        "strategies/",
        "raw/",
        "inbox/",
      ].some((prefix) => current.startsWith(prefix))
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
        <span>PaperTrader</span>
        <small>decision dashboard</small>
      </a>
      <nav class="papertrader-nav" aria-label="Primary navigation">
        {links.map(({ label, slug }) => {
          const active = linkIsActive(current, slug);
          return (
            <a
              href={resolveRelative(current, slug as FullSlug)}
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
DecisionNavigation.afterDOMLoaded = dashboardScript;

export default (() => DecisionNavigation) satisfies QuartzComponentConstructor;
