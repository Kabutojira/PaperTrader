import { spawnSync } from "node:child_process";
import { existsSync, lstatSync } from "node:fs";
import { dirname, join, parse, resolve } from "node:path";
import { fileURLToPath } from "node:url";

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
}
