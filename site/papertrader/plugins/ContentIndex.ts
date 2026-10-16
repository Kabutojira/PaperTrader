import fs from "node:fs/promises";
import { ContentIndex as CommunityContentIndex } from "@quartz-community/content-index";
import type {
  BuildCtx,
  ChangeEvent,
  FilePath,
  ProcessedContent,
  QuartzEmitterPlugin,
  QuartzEmitterPluginInstance,
  StaticResources,
} from "@quartz-community/types";
import { joinSegments } from "@quartz-community/types";
import type { Element, Root, RootContent } from "hast";
import { createSearchDocument, type SearchDocument } from "../search";

type ContentIndexOptions = Parameters<typeof CommunityContentIndex>[0];

const whitespace = /\s+/g;

function isElement(node: RootContent): node is Element {
  return node.type === "element";
}

function property(node: Element, name: string): unknown {
  return node.properties?.[name];
}

function isEchartBlock(node: Element): boolean {
  if (node.tagName !== "pre") return false;
  const language =
    property(node, "dataLanguage") ?? property(node, "data-language");
  return language === "echart";
}

function containsEchartBlock(node: Element): boolean {
  return (
    isEchartBlock(node) ||
    node.children.some(
      (child) => isElement(child) && containsEchartBlock(child),
    )
  );
}

/**
 * Produce the browser search corpus from rendered prose while omitting validated
 * echart payloads. Charts keep their complete visible data/JSON fallback in the
 * page; indexing thousands of deterministic numeric cells adds no useful prose
 * search signal and multiplies browser memory use.
 */
export function extractSearchText(tree: Root): string {
  const parts: string[] = [];

  const visit = (node: Root | RootContent): void => {
    if (node.type === "text") {
      parts.push(node.value);
      return;
    }
    if (node.type !== "root" && node.type !== "element") return;

    const element = node.type === "root" ? undefined : node;
    if (
      element &&
      (element.tagName === "script" ||
        element.tagName === "style" ||
        isEchartBlock(element) ||
        (element.tagName === "figure" && containsEchartBlock(element)))
    ) {
      return;
    }

    for (const child of node.children) visit(child);
  };

  visit(tree);
  return parts.join(" ").replace(whitespace, " ").trim();
}

function createSearchIndex(content: ProcessedContent[]): SearchDocument[] {
  const documents: SearchDocument[] = [];
  for (const [tree, file] of content) {
    const data = file.data as Record<string, unknown>;
    if (data.unlisted === true) continue;
    const slug = data.slug;
    if (typeof slug !== "string") continue;
    const frontmatter =
      (data.frontmatter as Record<string, unknown> | undefined) ?? {};
    const title =
      typeof frontmatter.title === "string" ? frontmatter.title : "";
    const tags = Array.isArray(frontmatter.tags)
      ? frontmatter.tags.filter((tag): tag is string => typeof tag === "string")
      : [];
    const prose = extractSearchText(tree as Root);
    documents.push(createSearchDocument(slug, title, tags, prose));
  }
  return documents;
}

async function writeIndexes(
  ctx: BuildCtx,
  content: ProcessedContent[],
): Promise<FilePath> {
  const outputDirectory = joinSegments(ctx.argv.output, "static");
  const metadataPath = joinSegments(outputDirectory, "contentIndex.json");
  const searchPath = joinSegments(outputDirectory, "searchIndex.json");

  const metadata = JSON.parse(
    await fs.readFile(metadataPath, "utf8"),
  ) as Record<string, Record<string, unknown>>;
  for (const entry of Object.values(metadata)) entry.content = "";

  await fs.writeFile(metadataPath, JSON.stringify(metadata));
  await fs.writeFile(searchPath, JSON.stringify(createSearchIndex(content)));
  return searchPath as FilePath;
}

async function collect(
  result: ReturnType<QuartzEmitterPluginInstance["emit"]>,
): Promise<FilePath[]> {
  if (Symbol.asyncIterator in result) {
    const paths: FilePath[] = [];
    for await (const filePath of result) paths.push(filePath);
    return paths;
  }
  return await result;
}

export const ContentIndex: QuartzEmitterPlugin<ContentIndexOptions> = (
  options,
) => {
  const community = CommunityContentIndex(options);

  const emit = async (
    ctx: BuildCtx,
    content: ProcessedContent[],
    resources: StaticResources,
  ): Promise<FilePath[]> => {
    const outputs = await collect(community.emit(ctx, content, resources));
    outputs.push(await writeIndexes(ctx, content));
    return outputs;
  };

  const partialEmit = async (
    ctx: BuildCtx,
    content: ProcessedContent[],
    resources: StaticResources,
    changes: ChangeEvent[],
  ): Promise<FilePath[]> => {
    const result = community.partialEmit?.(ctx, content, resources, changes);
    const outputs =
      result === null || result === undefined ? [] : await collect(result);
    outputs.push(await writeIndexes(ctx, content));
    return outputs;
  };

  return {
    ...community,
    name: "PaperTraderContentIndex",
    emit,
    partialEmit,
  };
};
