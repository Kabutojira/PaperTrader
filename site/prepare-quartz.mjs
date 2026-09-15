import {
  copyFileSync,
  cpSync,
  existsSync,
  lstatSync,
  mkdirSync,
  rmSync,
} from "node:fs";
import sharp from "sharp";
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

// Brand assets are repository-owned; regenerating Quartz must preserve them.
const brandSource = join(siteRoot, "papertrader", "assets");
cpSync(brandSource, join(destination, "static"), { recursive: true });
await sharp(join(brandSource, "icon.svg"))
  .resize(512, 512)
  .png()
  .toFile(join(destination, "static", "icon.png"));
await sharp(join(brandSource, "social-card.svg"))
  .png()
  .toFile(join(destination, "static", "og-image.png"));
await sharp(join(brandSource, "icon.svg"))
  .resize(180, 180)
  .png()
  .toFile(join(destination, "static", "apple-touch-icon.png"));
