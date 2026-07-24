import { QuartzConfig } from "./quartz/cfg";
import * as Plugin from "./quartz/plugins";

const config: QuartzConfig = {
  configuration: {
    pageTitle: "PaperTrader",
    pageTitleSuffix: " — paper trading research",
    enableSPA: true,
    enablePopovers: true,
    analytics: null,
    locale: "en-US",
    baseUrl: process.env.PAPERTRADER_BASE_URL,
    ignorePatterns: ["**/.gitkeep", "inbox", "_archive"],
    defaultDateType: "modified",
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
          light: "#fbfcfa",
          lightgray: "#e4e9e2",
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
      Plugin.FrontMatter(),
      Plugin.CreatedModifiedDate({ priority: ["frontmatter", "git"] }),
      Plugin.SyntaxHighlighting({
        theme: { light: "github-light", dark: "github-dark" },
        keepBackground: false,
      }),
      Plugin.ObsidianFlavoredMarkdown({ enableInHtmlEmbed: false }),
      Plugin.GitHubFlavoredMarkdown(),
      Plugin.TableOfContents(),
      Plugin.CrawlLinks({ markdownLinkResolution: "shortest" }),
      Plugin.Description(),
    ],
    filters: [Plugin.RemoveDrafts()],
    emitters: [
      Plugin.AliasRedirects(),
      Plugin.ComponentResources(),
      Plugin.ContentPage(),
      Plugin.FolderPage(),
      Plugin.TagPage(),
      Plugin.ContentIndex({ enableSiteMap: true, enableRSS: true }),
      Plugin.Assets(),
      Plugin.Static(),
      Plugin.Favicon(),
      Plugin.NotFoundPage(),
    ],
  },
};

export default config;
