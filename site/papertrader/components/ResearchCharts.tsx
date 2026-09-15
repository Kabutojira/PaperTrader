import {
  QuartzComponent,
  QuartzComponentConstructor,
} from "../../quartz/components/types";
import { pathToRoot } from "../../quartz/util/path";

// @ts-ignore
import researchChartsScript from "../scripts/research-charts.inline";
import styles from "../research-charts.scss";

const ResearchCharts: QuartzComponent = ({ fileData }) => (
  <span
    hidden
    data-papertrader-site-root={pathToRoot(fileData.slug!)}
    aria-hidden="true"
  />
);

ResearchCharts.css = styles;
ResearchCharts.afterDOMLoaded = researchChartsScript;

export default (() => ResearchCharts) satisfies QuartzComponentConstructor;
