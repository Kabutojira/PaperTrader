export type SearchDocument = {
  slug: string;
  title: string;
  tags: string[];
  text: string;
  excerpt: string;
};

type FetchSearchIndex = (url: string) => Promise<Response>;

type SearchActivation = Pick<
  MouseEvent,
  "altKey" | "button" | "ctrlKey" | "metaKey" | "shiftKey"
>;

export function normalizeSearchText(value: string): string {
  return value.toLocaleLowerCase("en-US").normalize("NFKD");
}

export function shouldCloseSearchForActivation(
  event: SearchActivation,
): boolean {
  return (
    event.button === 0 &&
    !event.altKey &&
    !event.ctrlKey &&
    !event.metaKey &&
    !event.shiftKey
  );
}

export function createSearchDocument(
  slug: string,
  title: string,
  tags: string[],
  prose: string,
): SearchDocument {
  return {
    slug,
    title,
    tags,
    text: normalizeSearchText(`${title} ${tags.join(" ")} ${prose}`),
    excerpt: prose.slice(0, 280),
  };
}

export function createSearchIndexLoader(
  fetchIndex: FetchSearchIndex = (url) => fetch(url),
): (url: string) => Promise<SearchDocument[]> {
  let pending: Promise<SearchDocument[]> | undefined;

  return (url) => {
    if (!pending) {
      pending = fetchIndex(url)
        .then((response) => {
          if (!response.ok)
            throw new Error(`search index returned HTTP ${response.status}`);
          return response.json() as Promise<unknown>;
        })
        .then((documents) =>
          Array.isArray(documents) ? (documents as SearchDocument[]) : [],
        )
        .catch((error: unknown) => {
          pending = undefined;
          throw error;
        });
    }
    return pending;
  };
}
