import {
  createSearchIndexLoader,
  normalizeSearchText,
  shouldCloseSearchForActivation,
  type SearchDocument,
} from "../search";

const fetchSearchIndex = createSearchIndexLoader();

function indexUrl(root: HTMLElement): string {
  return new URL(
    `${root.dataset.searchRoot ?? "."}/static/searchIndex.json`,
    window.location.href,
  ).href;
}

function loadIndex(root: HTMLElement): Promise<SearchDocument[]> {
  return fetchSearchIndex(indexUrl(root));
}

function score(
  document: SearchDocument,
  query: string,
  terms: string[],
): number {
  const title = normalizeSearchText(document.title);
  const tags = document.tags.map(normalizeSearchText);
  const tagQuery = query.startsWith("#") ? query.slice(1) : undefined;
  if (tagQuery) {
    if (!tags.some((tag) => tag.includes(tagQuery))) return -1;
  } else if (!terms.every((term) => document.text.includes(term))) {
    return -1;
  }

  let value = title === query ? 2_000 : 0;
  if (title.startsWith(query)) value += 1_000;
  if (title.includes(query)) value += 500;
  value += terms.filter((term) => title.includes(term)).length * 100;
  value +=
    terms.filter((term) => tags.some((tag) => tag.includes(term))).length * 50;
  if (document.text.includes(query)) value += 20;
  return value;
}

function resultUrl(root: HTMLElement, slug: string): string {
  const target = slug === "index" ? "" : slug;
  return new URL(
    `${root.dataset.searchRoot ?? "."}/${target}`,
    window.location.href,
  ).href;
}

function renderResults(
  root: HTMLElement,
  list: HTMLOListElement,
  status: HTMLElement,
  documents: SearchDocument[],
  rawQuery: string,
): void {
  const query = normalizeSearchText(rawQuery.trim());
  const terms = query.replace(/^#/, "").split(/\s+/).filter(Boolean);
  list.replaceChildren();
  if (terms.length === 0) {
    status.textContent = "Type to search titles, tags, and research prose.";
    return;
  }

  const matches = documents
    .map((document) => ({ document, score: score(document, query, terms) }))
    .filter((match) => match.score >= 0)
    .sort(
      (left, right) =>
        right.score - left.score ||
        left.document.title.localeCompare(right.document.title),
    )
    .slice(0, 20);

  status.textContent = matches.length
    ? `Showing ${matches.length} best result${matches.length === 1 ? "" : "s"}.`
    : "No matching research found.";

  for (const { document: searchDocument } of matches) {
    const item = document.createElement("li");
    const link = document.createElement("a");
    const title = document.createElement("strong");
    const excerpt = document.createElement("span");
    link.href = resultUrl(root, searchDocument.slug);
    title.textContent = searchDocument.title || searchDocument.slug;
    excerpt.textContent = searchDocument.excerpt;
    link.append(title, excerpt);
    item.append(link);
    list.append(item);
  }
}

function setupSearch(): void {
  const root = document.querySelector<HTMLElement>(".papertrader-search");
  const openButton = root?.querySelector<HTMLButtonElement>(
    ".papertrader-search__open",
  );
  const dialog = root?.querySelector<HTMLDialogElement>(
    ".papertrader-search__dialog",
  );
  const input = root?.querySelector<HTMLInputElement>(
    ".papertrader-search__input",
  );
  const status = root?.querySelector<HTMLElement>(
    ".papertrader-search__status",
  );
  const results = root?.querySelector<HTMLOListElement>(
    ".papertrader-search__results",
  );
  if (!root || !openButton || !dialog || !input || !status || !results) return;

  let requestedQuery = "";
  const showLoadError = (error: unknown): void => {
    results.replaceChildren();
    status.textContent = `Search is unavailable: ${
      error instanceof Error ? error.message : "unknown error"
    }. Type again to retry.`;
  };
  const open = (): void => {
    if (!dialog.open) dialog.showModal();
    input.focus();
    status.textContent = "Loading the research search index…";
    void loadIndex(root)
      .then((documents) => {
        if (input.value === requestedQuery)
          renderResults(root, results, status, documents, input.value);
      })
      .catch(showLoadError);
  };
  const onInput = (): void => {
    requestedQuery = input.value;
    status.textContent = "Searching…";
    void loadIndex(root)
      .then((documents) => {
        if (input.value === requestedQuery)
          renderResults(root, results, status, documents, input.value);
      })
      .catch(showLoadError);
  };
  const onKeydown = (event: KeyboardEvent): void => {
    if (
      event.key.toLocaleLowerCase() === "k" &&
      (event.ctrlKey || event.metaKey) &&
      !event.shiftKey
    ) {
      event.preventDefault();
      open();
    }
    if (event.key === "Enter" && dialog.open && event.target === input) {
      const first = results.querySelector<HTMLAnchorElement>("a");
      if (first) {
        event.preventDefault();
        first.click();
      }
    }
  };
  const onClick = (): void => open();
  const onResultClick = (event: MouseEvent): void => {
    const target =
      event.target instanceof Element ? event.target.closest("a") : null;
    if (
      target &&
      results.contains(target) &&
      shouldCloseSearchForActivation(event) &&
      dialog.open
    ) {
      dialog.close();
    }
  };
  const onPrenav = (): void => {
    if (dialog.open) dialog.close();
  };

  openButton.addEventListener("click", onClick);
  input.addEventListener("input", onInput);
  results.addEventListener("click", onResultClick);
  document.addEventListener("keydown", onKeydown);
  document.addEventListener("prenav", onPrenav);
  window.addCleanup(() => {
    openButton.removeEventListener("click", onClick);
    input.removeEventListener("input", onInput);
    results.removeEventListener("click", onResultClick);
    document.removeEventListener("keydown", onKeydown);
    document.removeEventListener("prenav", onPrenav);
  });
}

document.addEventListener("nav", setupSearch);
