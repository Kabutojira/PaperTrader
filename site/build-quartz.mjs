import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  copyFileSync,
  existsSync,
  lstatSync,
  mkdirSync,
  readFileSync,
  readdirSync,
} from "node:fs";
import { dirname, isAbsolute, join, parse, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const publicationFiles = {
  "decision_snapshot.json": null,
  "model_portfolio.csv": [
    "snapshot_id",
    "as_of",
    "holding_type",
    "security_id",
    "ticker",
    "company_name",
    "instrument_type",
    "sleeve",
    "current_weight_pct",
    "approved_target_weight_pct",
    "current_value_base",
    "approved_target_value_base",
    "delta_value_base",
    "current_quantity",
    "approved_target_quantity",
    "mark",
    "mark_currency",
    "mark_base",
    "fx_rate_to_base",
    "fx_as_of",
    "market_data_as_of",
    "action",
    "action_status",
    "strategy_id",
    "signal_id",
    "order_id",
    "confidence",
    "effective_score",
    "downside_pct",
    "base_upside_pct",
    "bear_fair_value",
    "bear_return_pct",
    "bear_probability_pct",
    "base_fair_value",
    "base_return_pct",
    "base_probability_pct",
    "bull_fair_value",
    "bull_return_pct",
    "bull_probability_pct",
    "expected_return_pct",
    "confidence_adjusted_expected_return_pct",
    "buy_below_price",
    "canonical_rating",
    "portfolio_action",
    "evidence_state",
    "rating_change_conditions",
    "valuation_horizon_months",
    "thesis_summary",
    "entry_rule",
    "exit_rule",
    "invalidation",
    "review_at",
    "security_research_page",
    "strategy_research_page",
    "research_page",
    "reason_codes",
  ],
  "actionable_signals.csv": [
    "snapshot_id",
    "as_of",
    "signal_id",
    "strategy_id",
    "order_id",
    "security_id",
    "ticker",
    "company_name",
    "action",
    "action_status",
    "copy_ready",
    "quantity",
    "order_type",
    "limit_price",
    "currency",
    "created_at",
    "expires_at",
    "market_data_as_of",
    "current_weight_pct",
    "approved_target_weight_pct",
    "strategy_name",
    "entry_rule",
    "exit_rule",
    "invalidation",
    "rationale",
    "security_research_page",
    "strategy_research_page",
    "research_page",
    "reason_codes",
  ],
  "research_benchmark.csv": [
    "snapshot_id",
    "as_of",
    "policy_version",
    "non_approved",
    "copy_ready",
    "security_id",
    "ticker",
    "company_name",
    "rating",
    "weight_pct",
    "reference_price",
    "currency",
    "research_page",
  ],
};

function assertRegularFile(path) {
  if (!existsSync(path))
    throw new Error(`publication artifact is missing: ${path}`);
  const status = lstatSync(path);
  if (!status.isFile() || status.isSymbolicLink()) {
    throw new Error(`publication artifact must be a regular file: ${path}`);
  }
}

function parseCsv(content, label) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  let quoteClosed = false;
  for (let index = 0; index < content.length; index += 1) {
    const character = content[index];
    if (quoted) {
      if (character !== '"') {
        field += character;
      } else if (content[index + 1] === '"') {
        field += '"';
        index += 1;
      } else {
        quoted = false;
        quoteClosed = true;
      }
      continue;
    }
    if (character === '"') {
      if (field !== "" || quoteClosed)
        throw new Error(`${label}: malformed CSV quote`);
      quoted = true;
      continue;
    }
    if (character === ",") {
      row.push(field);
      field = "";
      quoteClosed = false;
      continue;
    }
    if (character === "\n" || character === "\r") {
      if (character === "\r" && content[index + 1] === "\n") index += 1;
      row.push(field);
      rows.push(row);
      row = [];
      field = "";
      quoteClosed = false;
      continue;
    }
    if (quoteClosed)
      throw new Error(`${label}: characters follow a closing CSV quote`);
    field += character;
  }
  if (quoted) throw new Error(`${label}: unterminated CSV quote`);
  if (field !== "" || row.length > 0) {
    row.push(field);
    rows.push(row);
  }
  return rows;
}

function assertExactKeys(value, expected, label) {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    throw new Error(`${label} must be an object`);
  }
  const actual = Object.keys(value).sort();
  const wanted = [...expected].sort();
  if (JSON.stringify(actual) !== JSON.stringify(wanted)) {
    throw new Error(`${label} has unexpected or missing fields`);
  }
}

function validateSnapshot(content) {
  let snapshot;
  try {
    snapshot = JSON.parse(content);
  } catch (error) {
    throw new Error(`decision_snapshot.json is invalid JSON: ${error.message}`);
  }
  const required = [
    "version",
    "snapshot_id",
    "run_id",
    "as_of",
    "report_date",
    "investment_data_status",
    "operations_status",
    "stance",
    "stance_reason_codes",
    "evidence_state",
    "base_currency",
    "current_portfolio",
    "approved_target_portfolio",
    "actionable_signals",
    "candidate_pipeline",
    "research_benchmark",
    "research_alerts",
    "coverage",
    "performance",
    "system_impacts",
    "source_state_hashes",
  ];
  assertExactKeys(snapshot, required, "decision snapshot");
  if (snapshot.version !== 3)
    throw new Error("unsupported decision snapshot version");
  if (!/^decision_[0-9a-f]{20}$/.test(snapshot.snapshot_id)) {
    throw new Error("decision snapshot ID is invalid");
  }
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(snapshot.as_of)) {
    throw new Error("decision snapshot as_of is invalid");
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(snapshot.report_date)) {
    throw new Error("decision snapshot report_date is invalid");
  }
  for (const field of ["investment_data_status", "operations_status"]) {
    if (!["current", "degraded", "blocked"].includes(snapshot[field])) {
      throw new Error(`decision snapshot ${field} is invalid`);
    }
  }
  if (
    ![
      "hold_cash",
      "maintain",
      "deploy",
      "rebalance",
      "reduce_risk",
      "exit",
      "blocked",
    ].includes(snapshot.stance)
  ) {
    throw new Error("decision snapshot stance is invalid");
  }
  if (
    ![
      "definitive_cash_preference",
      "provisional_cash_research_incomplete",
      "provisional_cash_valuation_unsupported",
      "provisional_cash_strategy_pending",
      "portfolio_blocked",
      "invested_or_actionable",
    ].includes(snapshot.evidence_state)
  ) {
    throw new Error("decision snapshot evidence_state is invalid");
  }
  for (const field of [
    "stance_reason_codes",
    "actionable_signals",
    "candidate_pipeline",
    "research_alerts",
    "system_impacts",
  ]) {
    if (!Array.isArray(snapshot[field]))
      throw new Error(`decision snapshot ${field} must be an array`);
  }
  for (const field of [
    "current_portfolio",
    "approved_target_portfolio",
    "research_benchmark",
    "coverage",
    "performance",
    "source_state_hashes",
  ]) {
    if (
      typeof snapshot[field] !== "object" ||
      snapshot[field] === null ||
      Array.isArray(snapshot[field])
    ) {
      throw new Error(`decision snapshot ${field} must be an object`);
    }
  }
  for (const field of ["current_portfolio", "approved_target_portfolio"]) {
    if (!Array.isArray(snapshot[field].rows)) {
      throw new Error(`decision snapshot ${field}.rows must be an array`);
    }
    for (const row of snapshot[field].rows) {
      if (
        row.snapshot_id !== snapshot.snapshot_id ||
        row.as_of !== snapshot.as_of
      ) {
        throw new Error(`decision snapshot ${field} row identity mismatch`);
      }
    }
  }
  assertExactKeys(
    snapshot.research_benchmark,
    ["policy_version", "non_approved", "copy_ready", "rows"],
    "decision snapshot research_benchmark",
  );
  if (
    snapshot.research_benchmark.policy_version !== "equal_weight_rated_v1" ||
    snapshot.research_benchmark.non_approved !== true ||
    snapshot.research_benchmark.copy_ready !== false ||
    !Array.isArray(snapshot.research_benchmark.rows)
  ) {
    throw new Error("decision snapshot research_benchmark is invalid");
  }
  return snapshot;
}

function validateCsv(content, expectedHeader, snapshot, label) {
  const rows = parseCsv(content, label);
  if (
    rows.length === 0 ||
    JSON.stringify(rows[0]) !== JSON.stringify(expectedHeader)
  ) {
    throw new Error(
      `${label}: CSV header does not match the publication contract`,
    );
  }
  for (const [index, row] of rows.slice(1).entries()) {
    if (row.length !== expectedHeader.length) {
      throw new Error(`${label}: row ${index + 2} has ${row.length} fields`);
    }
    if (row[0] !== snapshot.snapshot_id || row[1] !== snapshot.as_of) {
      throw new Error(
        `${label}: row ${index + 2} does not match the decision snapshot`,
      );
    }
  }
  if (
    label === "model_portfolio.csv" &&
    rows.slice(1).filter((row) => row[2] === "cash").length !== 1
  ) {
    throw new Error(
      "model_portfolio.csv must contain exactly one explicit cash row",
    );
  }
  return rows
    .slice(1)
    .map((row) =>
      Object.fromEntries(
        expectedHeader.map((column, index) => [column, row[index]]),
      ),
    );
}

function publicationValue(value) {
  if (Array.isArray(value)) return value.join("|");
  if (typeof value === "boolean") return value ? "true" : "false";
  return String(value ?? "");
}

function expectedCsvRows(values, header, fixed = {}) {
  return values.map((value) =>
    Object.fromEntries(
      header.map((column) => [
        column,
        publicationValue(
          Object.prototype.hasOwnProperty.call(fixed, column)
            ? fixed[column]
            : value[column],
        ),
      ]),
    ),
  );
}

function assertCsvMatchesSnapshot(name, rows, header, snapshot) {
  let expected;
  if (name === "model_portfolio.csv") {
    expected = expectedCsvRows(snapshot.current_portfolio.rows, header);
  } else if (name === "actionable_signals.csv") {
    expected = expectedCsvRows(snapshot.actionable_signals, header, {
      snapshot_id: snapshot.snapshot_id,
      as_of: snapshot.as_of,
    });
  } else if (name === "research_benchmark.csv") {
    expected = expectedCsvRows(snapshot.research_benchmark.rows, header, {
      snapshot_id: snapshot.snapshot_id,
      as_of: snapshot.as_of,
      policy_version: snapshot.research_benchmark.policy_version,
      non_approved: snapshot.research_benchmark.non_approved,
      copy_ready: snapshot.research_benchmark.copy_ready,
    });
  } else {
    throw new Error(`unsupported publication CSV: ${name}`);
  }
  if (JSON.stringify(rows) !== JSON.stringify(expected)) {
    throw new Error(`${name} differs from decision_snapshot.json`);
  }
}

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function pathIsWithin(parent, candidate) {
  const value = relative(parent, candidate);
  return value !== "" && !value.startsWith("..") && !isAbsolute(value);
}

function publishValidatedArtifacts(wikiRoot, outputRoot) {
  const sourceRoot = resolve(wikiRoot, "..", "published");
  if (
    !existsSync(sourceRoot) ||
    !lstatSync(sourceRoot).isDirectory() ||
    lstatSync(sourceRoot).isSymbolicLink()
  ) {
    throw new Error(
      `publication source must be a regular directory: ${sourceRoot}`,
    );
  }
  const expectedNames = Object.keys(publicationFiles).sort();
  const actualNames = readdirSync(sourceRoot).sort();
  if (JSON.stringify(actualNames) !== JSON.stringify(expectedNames)) {
    throw new Error("data/published contains missing or unexpected files");
  }
  for (const name of expectedNames) assertRegularFile(join(sourceRoot, name));

  const snapshot = validateSnapshot(
    readFileSync(join(sourceRoot, "decision_snapshot.json"), "utf8"),
  );
  for (const [name, header] of Object.entries(publicationFiles)) {
    if (header !== null) {
      const rows = validateCsv(
        readFileSync(join(sourceRoot, name), "utf8"),
        header,
        snapshot,
        name,
      );
      assertCsvMatchesSnapshot(name, rows, header, snapshot);
    }
  }

  if (
    !existsSync(outputRoot) ||
    !lstatSync(outputRoot).isDirectory() ||
    lstatSync(outputRoot).isSymbolicLink()
  ) {
    throw new Error(`Quartz output must be a regular directory: ${outputRoot}`);
  }
  const destinationRoot = resolve(outputRoot, "data");
  if (!pathIsWithin(outputRoot, destinationRoot)) {
    throw new Error(
      `publication destination escapes Quartz output: ${destinationRoot}`,
    );
  }
  if (existsSync(destinationRoot)) {
    const status = lstatSync(destinationRoot);
    if (!status.isDirectory() || status.isSymbolicLink()) {
      throw new Error(
        `publication destination must be a regular directory: ${destinationRoot}`,
      );
    }
    const unexpected = readdirSync(destinationRoot).filter(
      (name) => !expectedNames.includes(name),
    );
    if (unexpected.length > 0)
      throw new Error("Quartz data output contains unexpected files");
  } else {
    mkdirSync(destinationRoot, { recursive: true });
  }
  for (const name of expectedNames) {
    const source = join(sourceRoot, name);
    const destination = join(destinationRoot, name);
    if (!pathIsWithin(outputRoot, destination)) {
      throw new Error(
        `publication destination escapes Quartz output: ${destination}`,
      );
    }
    if (existsSync(destination) && lstatSync(destination).isSymbolicLink()) {
      throw new Error(
        `publication destination must not be a symlink: ${destination}`,
      );
    }
    copyFileSync(source, destination);
    if (sha256(source) !== sha256(destination)) {
      throw new Error(`publication artifact hash changed during copy: ${name}`);
    }
  }
}

const siteRoot = dirname(fileURLToPath(import.meta.url));
const repositoryRoot = resolve(siteRoot, "..");
const wikiPath = resolve(
  process.env.WIKI_PATH || join(repositoryRoot, "data", "wiki"),
);
const outputPath = resolve(
  process.env.PAPERTRADER_SITE_OUTPUT || join(siteRoot, "public"),
);
const bootstrap = join(siteRoot, "quartz", "bootstrap-cli.mjs");

if (
  !existsSync(wikiPath) ||
  !lstatSync(wikiPath).isDirectory() ||
  lstatSync(wikiPath).isSymbolicLink()
) {
  throw new Error(`WIKI_PATH must be a regular directory: ${wikiPath}`);
}
if (!existsSync(bootstrap) || !lstatSync(bootstrap).isFile()) {
  throw new Error(
    "pinned Quartz engine is unavailable; run the prepare-engine script first",
  );
}
if (
  outputPath === parse(outputPath).root ||
  outputPath === repositoryRoot ||
  outputPath === siteRoot ||
  outputPath === wikiPath ||
  outputPath.startsWith(`${wikiPath}/`)
) {
  throw new Error(`refusing unsafe Quartz output path: ${outputPath}`);
}

const result = spawnSync(
  process.execPath,
  [bootstrap, "build", "-d", wikiPath, "-o", outputPath, "--concurrency=1"],
  { cwd: siteRoot, env: process.env, stdio: "inherit" },
);
if (result.error) {
  throw result.error;
}
if (result.status !== 0) {
  process.exitCode = result.status ?? 1;
} else {
  publishValidatedArtifacts(wikiPath, outputPath);
}
