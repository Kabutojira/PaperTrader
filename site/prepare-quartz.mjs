import {
  copyFileSync,
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  rmSync,
} from "node:fs";
import { createRequire } from "node:module";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const siteRoot = dirname(fileURLToPath(import.meta.url));
const destination = resolve(siteRoot, "quartz");
if (destination !== join(siteRoot, "quartz")) {
  throw new Error(`refusing unexpected Quartz destination: ${destination}`);
}

const require = createRequire(import.meta.url);
const engineRoot = dirname(require.resolve("@jackyzha0/quartz/package.json"));
const source = join(engineRoot, "quartz");
if (!existsSync(source) || !lstatSync(source).isDirectory()) {
  throw new Error(`pinned Quartz source directory is unavailable: ${source}`);
}

rmSync(destination, { recursive: true, force: true });
cpSync(source, destination, { recursive: true, dereference: false });

const echartsRoot = dirname(require.resolve("echarts/package.json"));
const vendorDestination = join(destination, "static", "vendor", "echarts");
mkdirSync(vendorDestination, { recursive: true });
for (const [sourceName, destinationName] of [
  ["dist/echarts.min.js", "echarts.min.js"],
  ["LICENSE", "LICENSE"],
  ["NOTICE", "NOTICE"],
]) {
  const vendorSource = join(echartsRoot, sourceName);
  if (
    !existsSync(vendorSource) ||
    lstatSync(vendorSource).isSymbolicLink() ||
    !lstatSync(vendorSource).isFile()
  ) {
    throw new Error(`pinned ECharts asset is unavailable: ${vendorSource}`);
  }
  copyFileSync(vendorSource, join(vendorDestination, destinationName));
}
