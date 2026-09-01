type ChartObject = Record<string, unknown>;

type EChartsInstance = {
  setOption(option: ChartObject): void;
  resize(): void;
  dispose(): void;
};

type EChartsApi = {
  init(
    element: HTMLElement,
    theme?: string,
    options?: ChartObject,
  ): EChartsInstance;
};

const chartColors = [
  "#4477aa",
  "#ee6677",
  "#228833",
  "#ccbb44",
  "#66ccee",
  "#aa3377",
  "#bbbbbb",
];

let echartsPromise: Promise<EChartsApi> | undefined;

function record(value: unknown): ChartObject {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error("chart specification must be an object");
  }
  return value as ChartObject;
}

function array(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) throw new Error(`${label} must be an array`);
  return value;
}

function text(value: unknown, label: string): string {
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(`${label} must be a non-empty string`);
  }
  return value;
}

function numberValue(value: unknown): number | null {
  if (value === null) return null;
  if (
    typeof value !== "string" ||
    !/^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$/.test(value)
  ) {
    throw new Error("numeric chart values must be decimal strings or null");
  }
  const parsed = Number(value);
  if (!Number.isFinite(parsed))
    throw new Error("numeric chart value is outside browser range");
  return parsed;
}

function loadECharts(): Promise<EChartsApi> {
  const current = (window as Window & { echarts?: EChartsApi }).echarts;
  if (current) return Promise.resolve(current);
  if (echartsPromise) return echartsPromise;
  echartsPromise = new Promise((resolve, reject) => {
    const postscript = [
      ...document.querySelectorAll<HTMLScriptElement>("script[src]"),
    ].find((script) =>
      new URL(script.src, document.baseURI).pathname.endsWith("/postscript.js"),
    );
    if (!postscript) {
      reject(new Error("cannot resolve the local ECharts asset"));
      return;
    }
    const source = new URL(
      "static/vendor/echarts/echarts.min.js",
      postscript.src,
    ).href;
    const script = document.createElement("script");
    script.src = source;
    script.defer = true;
    script.setAttribute("spa-preserve", "");
    script.dataset.papertraderEcharts = "6.0.0";
    script.addEventListener("load", () => {
      const api = (window as Window & { echarts?: EChartsApi }).echarts;
      if (api) resolve(api);
      else reject(new Error("local ECharts bundle did not expose its API"));
    });
    script.addEventListener("error", () =>
      reject(new Error("local ECharts bundle failed to load")),
    );
    document.head.append(script);
  });
  return echartsPromise;
}

function axisOption(value: unknown, includeZero = false): ChartObject {
  const axis = record(value);
  return {
    type: "value",
    name: text(axis.label, "axis label"),
    min: includeZero ? 0 : undefined,
    scale: !includeZero,
    axisLabel: { hideOverlap: true },
  };
}

function baseOption(): ChartObject {
  return {
    aria: { enabled: true, decal: { show: true } },
    animation: !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
    color: chartColors,
    textStyle: { fontFamily: "inherit" },
    tooltip: { trigger: "item", renderMode: "richText", confine: true },
  };
}

function seriesOption(spec: ChartObject): ChartObject {
  const xAxis = record(spec.x_axis);
  const labels = array(xAxis.values, "x_axis.values").map((value) =>
    text(value, "x value"),
  );
  const axes = array(spec.y_axes, "y_axes");
  const rawSeries = array(spec.series, "series").map(record);
  const includesBars = rawSeries.some((item) => item.render === "bar");
  const allNonnegative = rawSeries.every((item) =>
    array(item.values, "series values").every((value) => {
      const parsed = numberValue(value);
      return parsed === null || parsed >= 0;
    }),
  );
  return {
    ...baseOption(),
    tooltip: { trigger: "axis", renderMode: "richText", confine: true },
    legend: { type: "scroll", bottom: 0 },
    grid: {
      left: 16,
      right: axes.length > 1 ? 32 : 16,
      top: 30,
      bottom: 70,
      containLabel: true,
    },
    xAxis: {
      type: xAxis.type === "time" ? "time" : "category",
      name: text(xAxis.label, "x_axis.label"),
      data: xAxis.type === "time" ? undefined : labels,
      axisLabel: {
        hideOverlap: true,
        rotate: labels.some((label) => label.length > 14) ? 30 : 0,
      },
    },
    yAxis: axes.map((axis) => axisOption(axis, includesBars && allNonnegative)),
    dataZoom:
      labels.length > 14
        ? [{ type: "inside" }, { type: "slider", bottom: 28 }]
        : [],
    series: rawSeries.map((item) => {
      const values = array(item.values, "series values").map(numberValue);
      const data =
        xAxis.type === "time"
          ? labels.map((label, index) => [label, values[index]])
          : values;
      return {
        name: text(item.name, "series name"),
        type: item.render === "bar" ? "bar" : "line",
        areaStyle: item.render === "area" ? {} : undefined,
        connectNulls: false,
        yAxisIndex: item.y_axis,
        stack: item.stack,
        data,
      };
    }),
  };
}

function scatterOption(spec: ChartObject): ChartObject {
  const points = array(spec.points, "points").map(record);
  return {
    ...baseOption(),
    grid: { left: 16, right: 16, top: 24, bottom: 24, containLabel: true },
    xAxis: axisOption(spec.x_axis),
    yAxis: axisOption(spec.y_axis),
    series: [
      {
        type: "scatter",
        data: points.map((point) => ({
          name: text(point.label, "point label"),
          value: [
            numberValue(point.x),
            numberValue(point.y),
            point.size ? numberValue(point.size) : null,
          ],
        })),
        symbolSize: 12,
      },
    ],
  };
}

function compositionOption(spec: ChartObject): ChartObject {
  const items = array(spec.items, "items").map(record);
  const data = items.map((item) => ({
    name: text(item.label, "item label"),
    value: numberValue(item.value),
  }));
  if (spec.display === "donut") {
    return {
      ...baseOption(),
      legend: { type: "scroll", bottom: 0 },
      series: [{ type: "pie", radius: ["42%", "70%"], data }],
    };
  }
  if (spec.display === "treemap") {
    return {
      ...baseOption(),
      series: [{ type: "treemap", roam: false, data }],
    };
  }
  return {
    ...baseOption(),
    grid: { left: 16, right: 16, top: 16, bottom: 24, containLabel: true },
    xAxis: axisOption(spec.axis, true),
    yAxis: { type: "category", data: data.map((item) => item.name) },
    series: [{ type: "bar", data: data.map((item) => item.value) }],
  };
}

function candlestickOption(spec: ChartObject): ChartObject {
  const rows = array(spec.rows, "rows").map(record);
  return {
    ...baseOption(),
    tooltip: { trigger: "axis", renderMode: "richText", confine: true },
    grid: { left: 16, right: 16, top: 20, bottom: 55, containLabel: true },
    xAxis: {
      type: "category",
      data: rows.map((row) => text(row.at, "row date")),
    },
    yAxis: {
      type: "value",
      scale: true,
      name: text(spec.currency, "currency"),
    },
    dataZoom: [{ type: "inside" }, { type: "slider", bottom: 18 }],
    series: [
      {
        type: "candlestick",
        data: rows.map((row) => [
          numberValue(row.open),
          numberValue(row.close),
          numberValue(row.low),
          numberValue(row.high),
        ]),
      },
    ],
  };
}

function heatmapOption(spec: ChartObject): ChartObject {
  const xLabels = array(spec.x_labels, "x_labels").map((value) =>
    text(value, "x label"),
  );
  const yLabels = array(spec.y_labels, "y_labels").map((value) =>
    text(value, "y label"),
  );
  const cells = array(spec.cells, "cells").map(record);
  const data = cells.map((cell) => [cell.x, cell.y, numberValue(cell.value)]);
  const values = data
    .map((cell) => cell[2])
    .filter((value): value is number => typeof value === "number");
  return {
    ...baseOption(),
    grid: { left: 16, right: 50, top: 20, bottom: 35, containLabel: true },
    xAxis: { type: "category", data: xLabels, splitArea: { show: true } },
    yAxis: { type: "category", data: yLabels, splitArea: { show: true } },
    visualMap: {
      min: Math.min(...values),
      max: Math.max(...values),
      calculable: true,
      orient: "vertical",
      right: 0,
    },
    series: [{ type: "heatmap", data, label: { show: data.length <= 36 } }],
  };
}

function networkOption(spec: ChartObject): ChartObject {
  const nodes = array(spec.nodes, "nodes")
    .map(record)
    .map((node) => ({
      id: text(node.id, "node id"),
      name: text(node.label, "node label"),
      category: node.category,
      value: node.value ? numberValue(node.value) : undefined,
    }));
  const links = array(spec.links, "links")
    .map(record)
    .map((link) => ({
      source: text(link.source, "link source"),
      target: text(link.target, "link target"),
      value: link.value ? numberValue(link.value) : undefined,
      label: link.label
        ? { show: true, formatter: text(link.label, "link label") }
        : undefined,
    }));
  if (spec.display === "sankey") {
    return {
      ...baseOption(),
      series: [
        {
          type: "sankey",
          data: nodes,
          links,
          emphasis: { focus: "adjacency" },
        },
      ],
    };
  }
  return {
    ...baseOption(),
    series: [
      {
        type: "graph",
        layout: "force",
        roam: true,
        label: { show: true },
        data: nodes,
        links,
        emphasis: { focus: "adjacency" },
      },
    ],
  };
}

function compileOption(spec: ChartObject): ChartObject {
  switch (text(spec.kind, "kind")) {
    case "series":
      return seriesOption(spec);
    case "scatter":
      return scatterOption(spec);
    case "composition":
      return compositionOption(spec);
    case "candlestick":
      return candlestickOption(spec);
    case "heatmap":
      return heatmapOption(spec);
    case "network":
      return networkOption(spec);
    default:
      throw new Error("unsupported chart kind");
  }
}

function tableRows(spec: ChartObject): string[][] {
  if (spec.kind === "series") {
    const xAxis = record(spec.x_axis);
    const labels = array(xAxis.values, "x values").map(String);
    const series = array(spec.series, "series").map(record);
    return [
      [
        text(xAxis.label, "x label"),
        ...series.map((item) => text(item.name, "series name")),
      ],
      ...labels.map((label, index) => [
        label,
        ...series.map((item) =>
          String(array(item.values, "values")[index] ?? "—"),
        ),
      ]),
    ];
  }
  if (spec.kind === "scatter") {
    return [
      ["Observation", "X", "Y", "Size"],
      ...array(spec.points, "points")
        .map(record)
        .map((point) => [
          text(point.label, "point label"),
          String(point.x),
          String(point.y),
          point.size ? String(point.size) : "—",
        ]),
    ];
  }
  if (spec.kind === "composition") {
    return [
      ["Category", "Value"],
      ...array(spec.items, "items")
        .map(record)
        .map((item) => [text(item.label, "item label"), String(item.value)]),
    ];
  }
  if (spec.kind === "candlestick") {
    return [
      ["Date", "Open", "Close", "Low", "High", "Volume"],
      ...array(spec.rows, "rows")
        .map(record)
        .map((row) => [
          text(row.at, "date"),
          String(row.open),
          String(row.close),
          String(row.low),
          String(row.high),
          row.volume === null || row.volume === undefined
            ? "—"
            : String(row.volume),
        ]),
    ];
  }
  if (spec.kind === "heatmap") {
    const xLabels = array(spec.x_labels, "x labels").map(String);
    const yLabels = array(spec.y_labels, "y labels").map(String);
    const cells = array(spec.cells, "cells").map(record);
    return [
      ["Row", ...xLabels],
      ...yLabels.map((label, y) => [
        label,
        ...xLabels.map((_, x) =>
          String(
            cells.find((cell) => cell.x === x && cell.y === y)?.value ?? "—",
          ),
        ),
      ]),
    ];
  }
  return [
    ["Source", "Target", "Value", "Label"],
    ...array(spec.links, "links")
      .map(record)
      .map((link) => [
        text(link.source, "source"),
        text(link.target, "target"),
        link.value ? String(link.value) : "—",
        link.label ? String(link.label) : "—",
      ]),
  ];
}

function createTable(spec: ChartObject): HTMLDivElement {
  const container = document.createElement("div");
  container.className = "research-chart__table";
  const table = document.createElement("table");
  const rows = tableRows(spec);
  const head = table.createTHead();
  const body = table.createTBody();
  rows.forEach((values, rowIndex) => {
    const row = document.createElement("tr");
    values.forEach((value) => {
      const cell = document.createElement(rowIndex === 0 ? "th" : "td");
      if (rowIndex === 0) (cell as HTMLTableCellElement).scope = "col";
      cell.textContent = value;
      row.append(cell);
    });
    (rowIndex === 0 ? head : body).append(row);
  });
  container.append(table);
  return container;
}

function appendSources(figure: HTMLElement, spec: ChartObject): void {
  const list = document.createElement("ul");
  list.className = "research-chart__sources";
  for (const sourceValue of array(spec.sources, "sources")) {
    const source = record(sourceValue);
    const item = document.createElement("li");
    const label = text(source.label, "source label");
    if (typeof source.url === "string" && /^https?:\/\//.test(source.url)) {
      const link = document.createElement("a");
      link.href = source.url;
      link.textContent = label;
      link.rel = "noopener noreferrer";
      item.append(link);
    } else {
      item.textContent = label;
    }
    list.append(item);
  }
  figure.append(list);
}

async function renderResearchCharts(): Promise<void> {
  const blocks = [
    ...document.querySelectorAll<HTMLPreElement>('pre[data-language="echart"]'),
  ].filter((block) => !block.closest(".research-chart"));
  if (blocks.length === 0) return;
  let api: EChartsApi;
  try {
    api = await loadECharts();
  } catch (error) {
    for (const block of blocks) {
      const message = document.createElement("p");
      message.className = "research-chart__error";
      message.textContent = `Interactive chart unavailable: ${error instanceof Error ? error.message : "unknown error"}. The validated data follows.`;
      (block.closest("figure[data-rehype-pretty-code-figure]") ?? block).before(
        message,
      );
    }
    return;
  }

  for (const block of blocks) {
    const rawContainer =
      block.closest<HTMLElement>("figure[data-rehype-pretty-code-figure]") ??
      block;
    try {
      const spec = record(JSON.parse(block.textContent ?? ""));
      if (spec.schema_version !== 1)
        throw new Error("unsupported chart schema version");
      const option = compileOption(spec);
      const figure = document.createElement("figure");
      figure.className = "research-chart";
      figure.dataset.chartId = text(spec.chart_id, "chart_id");
      const heading = document.createElement("h3");
      heading.textContent = text(spec.title, "title");
      const description = document.createElement("p");
      description.className = "research-chart__description";
      description.textContent = text(spec.description, "description");
      const asOf = document.createElement("p");
      asOf.className = "research-chart__as-of";
      asOf.textContent = `Data as of ${text(spec.as_of, "as_of")}`;
      const canvas = document.createElement("div");
      canvas.className = "research-chart__canvas";
      canvas.setAttribute("role", "img");
      canvas.setAttribute(
        "aria-label",
        `${heading.textContent}. ${description.textContent}`,
      );
      const dataDetails = document.createElement("details");
      const dataSummary = document.createElement("summary");
      dataSummary.textContent = "View chart data table";
      dataDetails.append(dataSummary, createTable(spec));
      const rawDetails = document.createElement("details");
      const rawSummary = document.createElement("summary");
      rawSummary.textContent = "View validated chart JSON";
      rawContainer.replaceWith(figure);
      rawDetails.append(rawSummary, rawContainer);
      figure.append(heading, description, asOf, canvas, dataDetails);
      appendSources(figure, spec);
      figure.append(rawDetails);

      let instance = api.init(
        canvas,
        document.documentElement.getAttribute("saved-theme") === "dark"
          ? "dark"
          : undefined,
        { renderer: "svg" },
      );
      instance.setOption(option);
      const observer = new ResizeObserver(() => instance.resize());
      observer.observe(canvas);
      const changeTheme = (): void => {
        instance.dispose();
        instance = api.init(
          canvas,
          document.documentElement.getAttribute("saved-theme") === "dark"
            ? "dark"
            : undefined,
          { renderer: "svg" },
        );
        instance.setOption(option);
      };
      document.addEventListener("themechange", changeTheme);
      window.addCleanup(() => {
        observer.disconnect();
        document.removeEventListener("themechange", changeTheme);
        instance.dispose();
      });
    } catch (error) {
      const message = document.createElement("p");
      message.className = "research-chart__error";
      message.textContent = `Chart could not be rendered: ${error instanceof Error ? error.message : "invalid specification"}. The validated data follows.`;
      rawContainer.before(message);
    }
  }
}

document.addEventListener("nav", () => void renderResearchCharts());
