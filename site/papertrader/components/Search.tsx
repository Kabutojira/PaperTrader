import {
  QuartzComponent,
  QuartzComponentConstructor,
} from "../../quartz/components/types";
import { pathToRoot } from "../../quartz/util/path";

// @ts-ignore
import searchScript from "../scripts/search.inline";
import styles from "../search.scss";

const Search: QuartzComponent = ({ displayClass, fileData }) => (
  <div
    class={`${displayClass ?? ""} papertrader-search`}
    data-search-root={pathToRoot(fileData.slug!)}
  >
    <button
      type="button"
      class="papertrader-search__open"
      aria-label="Search"
      aria-haspopup="dialog"
    >
      <svg role="img" aria-hidden="true" viewBox="0 0 20 20">
        <circle cx="8" cy="8" r="6" />
        <path d="m12.5 12.5 5 5" />
      </svg>
      <span>Search</span>
    </button>
    <dialog class="papertrader-search__dialog" aria-label="Search PaperTrader">
      <form method="dialog" class="papertrader-search__header">
        <input
          class="papertrader-search__input"
          name="search"
          type="search"
          autocomplete="off"
          placeholder="Search research and reports…"
          aria-label="Search research and reports"
        />
        <button type="submit" aria-label="Close search">
          Close
        </button>
      </form>
      <p class="papertrader-search__status" aria-live="polite">
        Type to search titles, tags, and research prose.
      </p>
      <ol class="papertrader-search__results"></ol>
    </dialog>
  </div>
);

Search.css = styles;
Search.afterDOMLoaded = searchScript;

export default (() => Search) satisfies QuartzComponentConstructor;
