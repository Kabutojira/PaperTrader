import { spawnSync } from "node:child_process";
import { cpSync, existsSync, lstatSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, parse, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = dirname(fileURLToPath(import.meta.url));
const sourceRoot = resolve(
  process.env.WIKI_PATH || join(siteRoot, "../data/wiki"),
  "../..",
);
const output = resolve(
  process.env.PAPERTRADER_SITE_OUTPUT || join(siteRoot, "public"),
);
if (
  [parse(output).root, siteRoot, sourceRoot].includes(output) ||
  output.startsWith(`${sourceRoot}/data/`)
) {
  throw new Error("unsafe Quartz output directory");
}
if (existsSync(output) && lstatSync(output).isSymbolicLink())
  throw new Error("symlink output");
const temporary = mkdtempSync(join(tmpdir(), "papertrader-research-site-"));
try {
  const localPython = join(siteRoot, "../.venv/bin/python");
  const python =
    process.env.PAPERTRADER_PYTHON ||
    (existsSync(localPython) ? localPython : "python3");
  const prepared = spawnSync(
    python,
    [
      join(siteRoot, "../scripts/prepare_research_site.py"),
      "--repository",
      sourceRoot,
      "--output",
      temporary,
    ],
    { stdio: "inherit", env: process.env },
  );
  if (prepared.status !== 0)
    throw new Error("current research site validation failed");
  rmSync(output, { recursive: true, force: true });
  const built = spawnSync(
    process.execPath,
    [
      join(siteRoot, "quartz/bootstrap-cli.mjs"),
      "build",
      "-d",
      temporary,
      "-o",
      output,
      "--concurrency=1",
    ],
    { cwd: siteRoot, env: process.env, stdio: "inherit" },
  );
  if (built.error) throw built.error;
  if (built.status !== 0) process.exitCode = built.status ?? 1;
  else {
    cpSync(join(siteRoot, "quartz/static"), join(output, "static"), {
      recursive: true,
      dereference: false,
    });
    cpSync(join(temporary, "data"), join(output, "data"), {
      recursive: true,
      dereference: false,
    });
  }
} finally {
  rmSync(temporary, { recursive: true, force: true });
}
