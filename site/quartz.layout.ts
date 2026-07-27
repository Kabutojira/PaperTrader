import { PageLayout, SharedLayout } from "./quartz/cfg";
import * as Component from "./quartz/components";
import { QuartzComponentProps } from "./quartz/components/types";
import DecisionNavigation from "./papertrader/components/DecisionNavigation";

const dashboardPages = new Set([
  "index",
  "model-portfolio",
  "signals",
  "performance",
  "system-status",
]);

const isDashboardPage = (page: QuartzComponentProps): boolean =>
  dashboardPages.has(page.fileData.slug ?? "");

const repository = process.env.GITHUB_REPOSITORY;
const repositoryUrl = repository
  ? `https://github.com/${repository}`
  : "https://github.com";

export const sharedPageComponents: SharedLayout = {
  head: Component.Head(),
  header: [DecisionNavigation()],
  afterBody: [],
  footer: Component.Footer({
    links: {
      "Source repository": repositoryUrl,
    },
  }),
};

export const defaultContentPageLayout: PageLayout = {
  beforeBody: [
    Component.ConditionalRender({
      component: Component.Breadcrumbs(),
      condition: (page) => page.fileData.slug !== "index",
    }),
    Component.ConditionalRender({
      component: Component.ArticleTitle(),
      condition: (page) => !isDashboardPage(page),
    }),
    Component.ConditionalRender({
      component: Component.ContentMeta(),
      condition: (page) => !isDashboardPage(page),
    }),
    Component.ConditionalRender({
      component: Component.TagList(),
      condition: (page) => !isDashboardPage(page),
    }),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        { Component: Component.Search(), grow: true },
        { Component: Component.Darkmode() },
        { Component: Component.ReaderMode() },
      ],
    }),
    Component.ConditionalRender({
      component: Component.Explorer(),
      condition: (page) => !isDashboardPage(page),
    }),
  ],
  right: [
    Component.ConditionalRender({
      component: Component.DesktopOnly(Component.TableOfContents()),
      condition: (page) => !isDashboardPage(page),
    }),
    Component.ConditionalRender({
      component: Component.Backlinks(),
      condition: (page) => !isDashboardPage(page),
    }),
  ],
};

export const defaultListPageLayout: PageLayout = {
  beforeBody: [
    Component.Breadcrumbs(),
    Component.ArticleTitle(),
    Component.ContentMeta(),
  ],
  left: [
    Component.PageTitle(),
    Component.MobileOnly(Component.Spacer()),
    Component.Flex({
      components: [
        { Component: Component.Search(), grow: true },
        { Component: Component.Darkmode() },
      ],
    }),
    Component.Explorer(),
  ],
  right: [],
};
