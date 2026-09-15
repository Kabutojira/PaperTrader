import { QuartzConfig } from "./quartz/cfg";
import * as Plugin from "./quartz/plugins";
import * as Community from "./papertrader/plugins";
import { layout } from "./quartz.layout";

const config: QuartzConfig = {
  configuration: {
    pageTitle: "PaperTrader",
    pageTitleSuffix: " — investment research",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "en-US",
    baseUrl: process.env.PAPERTRADER_BASE_URL,
    ignorePatterns: ["**/.gitkeep", "_archive"],
    theme: {
      fontOrigin: "local",
      cdnCaching: false,
      typography: {
        header: "system-ui",
        body: "system-ui",
        code: "ui-monospace",
      },
      colors: {
        lightMode: {
          light: "#faf8f2",
          lightgray: "#e4e5da",
          gray: "#9aa59a",
          darkgray: "#435047",
          dark: "#172019",
          secondary: "#176b45",
          tertiary: "#9b6115",
          highlight: "rgba(23, 107, 69, 0.14)",
          textHighlight: "#f4d35e66",
        },
        darkMode: {
          light: "#121713",
          lightgray: "#273029",
          gray: "#68766c",
          darkgray: "#ced8d0",
          dark: "#f2f7f3",
          secondary: "#62c995",
          tertiary: "#e5ad5f",
          highlight: "rgba(98, 201, 149, 0.16)",
          textHighlight: "#c99b2966",
        },
      },
    },
  },
  plugins: {
    transformers: [
      Community.NoteProperties(),
      Community.CreatedModifiedDate({
        priority: ["frontmatter", "git"],
        defaultDateType: "modified",
      }),
      Community.SyntaxHighlighting({
        theme: { light: "github-light", dark: "github-dark" },
        keepBackground: false,
      }),
      Community.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Community.GitHubFlavoredMarkdown(),
      Community.TableOfContentsTransformer(),
      Community.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Community.Description(),
    ],
    filters: [Community.RemoveDrafts()],
    emitters: [
      Community.AliasRedirects(),
      Plugin.ComponentResources(),
      Community.ContentIndex({ enableSiteMap: true, enableRSS: true }),
      Plugin.Assets(),
      Plugin.Static(),
      Community.Favicon(),
      Plugin.PageTypes.PageTypeDispatcher(layout),
    ],
    pageTypes: [
      Community.FolderPage(),
      Community.TagPage(),
      Community.ContentPage(),
      Plugin.PageTypes.NotFoundPageType(),
    ],
  },
};

export default config;
