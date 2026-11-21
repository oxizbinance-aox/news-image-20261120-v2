// News Image 20 Nov 2026 — entrypoint.
//
// The grader runs this file at the repository root. Its job is to place the
// finished picture (entry.png) into the output folder the harness provides,
// so the graded run can find it there.
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";

const artworkName = "entry.png";
const fallbackDir = "/output";
const destinationDir = process.env.MAKEFUN_OUTPUT_DIR || fallbackDir;
const artworkPath = resolve(process.cwd(), artworkName);

if (!existsSync(artworkPath)) {
  throw new Error(`missing artwork: ${artworkPath}`);
}

mkdirSync(destinationDir, { recursive: true });
const pixels = readFileSync(artworkPath);
const destination = join(destinationDir, artworkName);
writeFileSync(destination, pixels);
console.log(`wrote ${destination}`);
