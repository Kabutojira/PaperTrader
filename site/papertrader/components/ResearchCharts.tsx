import {
  QuartzComponent,
  QuartzComponentConstructor,
} from "../../quartz/components/types";

// @ts-ignore
import researchChartsScript from "../scripts/research-charts.inline";
import styles from "../research-charts.scss";

const ResearchCharts: QuartzComponent = () => <></>;

ResearchCharts.css = styles;
ResearchCharts.afterDOMLoaded = researchChartsScript;

export default (() => ResearchCharts) satisfies QuartzComponentConstructor;
