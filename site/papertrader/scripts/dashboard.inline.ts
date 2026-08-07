type PortfolioCard = {
  element: HTMLElement;
  ticker: string;
  company: string;
  targetWeight: number;
  mark: number;
  markCurrency: string;
  fx: number;
  marketDataAsOf: string;
  scalable: boolean;
};

function parseFinite(value: string | undefined): number | null {
  if (value === undefined || value.trim() === "") return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function portfolioCards(): PortfolioCard[] {
  const cards: PortfolioCard[] = [];
  for (const element of document.querySelectorAll<HTMLElement>(
    ".portfolio-card",
  )) {
    const targetWeight = parseFinite(element.dataset.targetWeight);
    const mark = parseFinite(element.dataset.mark);
    const fx = parseFinite(element.dataset.fx);
    if (targetWeight === null || mark === null || fx === null) continue;
    cards.push({
      element,
      ticker: element.dataset.ticker || "CASH",
      company: element.dataset.company || "Cash",
      targetWeight,
      mark,
      markCurrency: element.dataset.markCurrency || "",
      fx,
      marketDataAsOf: element.dataset.marketDataAsOf || "",
      scalable: element.dataset.scalable === "true",
    });
  }
  return cards;
}

function setResult(
  container: HTMLElement,
  heading: string,
  rows: string[][],
): void {
  container.replaceChildren();
  const title = document.createElement("h3");
  title.textContent = heading;
  container.append(title);
  if (rows.length === 0) return;
  const table = document.createElement("table");
  const head = document.createElement("thead");
  const body = document.createElement("tbody");
  const headerRow = document.createElement("tr");
  for (const label of rows[0]) {
    const cell = document.createElement("th");
    cell.scope = "col";
    cell.textContent = label;
    headerRow.append(cell);
  }
  head.append(headerRow);
  for (const values of rows.slice(1)) {
    const row = document.createElement("tr");
    for (const value of values) {
      const cell = document.createElement("td");
      cell.textContent = value;
      row.append(cell);
    }
    body.append(row);
  }
  table.append(head, body);
  container.append(table);
}

function setupCopyButton(): void {
  const button = document.querySelector<HTMLButtonElement>("#copy-portfolio");
  const result = document.querySelector<HTMLElement>("#scaled-portfolio");
  if (!button || !result) return;
  const copy = async (): Promise<void> => {
    const rows = portfolioCards();
    const tsv = [
      [
        "Ticker",
        "Company",
        "Target weight %",
        "Reference mark",
        "Currency",
        "FX to base",
        "Market data as of",
      ],
      ...rows.map((row) => [
        row.ticker,
        row.company,
        String(row.targetWeight),
        String(row.mark),
        row.markCurrency,
        String(row.fx),
        row.marketDataAsOf,
      ]),
    ]
      .map((row) => row.join("\t"))
      .join("\n");
    try {
      await navigator.clipboard.writeText(tsv);
      setResult(result, "Portfolio copied as TSV.", []);
    } catch {
      setResult(
        result,
        "Copy failed; use the committed CSV download instead.",
        [],
      );
    }
  };
  button.addEventListener("click", copy);
  window.addCleanup(() => button.removeEventListener("click", copy));
}

function setupScaler(): void {
  const button = document.querySelector<HTMLButtonElement>("#scale-portfolio");
  const input = document.querySelector<HTMLInputElement>("#reference-notional");
  const result = document.querySelector<HTMLElement>("#scaled-portfolio");
  if (!button || !input || !result) return;
  const scale = (): void => {
    const notional = parseFinite(input.value);
    if (notional === null || notional <= 0) {
      setResult(result, "Enter a positive portfolio value.", []);
      return;
    }
    const positions = portfolioCards().filter(
      (row) =>
        row.scalable && row.targetWeight > 0 && row.mark > 0 && row.fx > 0,
    );
    if (positions.length === 0) {
      setResult(result, "No long-equity targets are available to scale.", []);
      return;
    }
    let deployed = 0;
    const output: string[][] = [
      [
        "Holding",
        "Whole shares",
        "Reference mark / FX",
        "Reference time",
        "Base value",
      ],
    ];
    for (const position of positions) {
      const basePrice = position.mark * position.fx;
      const targetValue = (notional * position.targetWeight) / 100;
      const quantity = Math.floor(targetValue / basePrice);
      const baseValue = quantity * basePrice;
      deployed += baseValue;
      output.push([
        `${position.ticker} — ${position.company}`,
        String(quantity),
        `${position.mark} ${position.markCurrency} / ${position.fx}`,
        position.marketDataAsOf,
        baseValue.toFixed(2),
      ]);
    }
    output.push([
      "Residual cash (target cash plus whole-share rounding)",
      "—",
      "—",
      "—",
      Math.max(0, notional - deployed).toFixed(2),
    ]);
    setResult(result, "Whole-share long-equity quantities", output);
  };
  button.addEventListener("click", scale);
  window.addCleanup(() => button.removeEventListener("click", scale));
}

document.addEventListener("nav", () => {
  setupCopyButton();
  setupScaler();
});
