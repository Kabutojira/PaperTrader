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
        Valuations with evidence.
      </h2>
      <p>
        Explore companies, follow investment ideas, and examine sourced
        valuations.
      </p>
      <div class="research-hero-tags" aria-label="Project principles">
        <span>Public research</span>
        <span>Company discovery</span>
        <span>Current evidence</span>
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
