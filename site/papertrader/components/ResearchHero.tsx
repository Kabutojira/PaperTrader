import type {
  QuartzComponent,
  QuartzComponentConstructor,
} from "../../quartz/components/types";
import { joinSegments, pathToRoot } from "../../quartz/util/path";

const ResearchHero: QuartzComponent = ({ fileData }) => (
  <section class="research-hero" aria-label="About PaperTrader">
    <div class="research-hero-copy">
      <p class="research-eyebrow">The open investment notebook</p>
      <h2>
        Research with roots.
        <br />
        Decisions with evidence.
      </h2>
      <p>
        Follow the ideas, explore the research, and track a portfolio built on
        paper.
      </p>
      <div class="research-hero-tags" aria-label="Project principles">
        <span>Public research</span>
        <span>Paper trades</span>
        <span>Traceable decisions</span>
      </div>
    </div>
    <img
      class="research-hero-art"
      src={joinSegments(
        pathToRoot(fileData.slug!),
        "static/research-garden.svg",
      )}
      width="560"
      height="360"
      alt=""
      aria-hidden="true"
      decoding="async"
    />
  </section>
);

export default (() => ResearchHero) satisfies QuartzComponentConstructor;
