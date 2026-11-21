import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

// The artwork lives next to this script, so locate it from the script's own
// location. The grader may launch us from any working directory, therefore
// the current working directory is never consulted for the artwork path.
function artworkDirectory(): string {
  const override = process.env.MAKEFUN_BOT_DIR;
  if (override !== undefined && override !== "") {
    return resolve(override);
  }
  return dirname(fileURLToPath(import.meta.url));
}

function outputDirectory(): string {
  const override = process.env.MAKEFUN_OUTPUT_DIR;
  if (override !== undefined && override !== "") {
    return resolve(override);
  }
  return "/output";
}

const artworkPath = join(artworkDirectory(), "entry.png");
const destinationDir = outputDirectory();

if (!existsSync(artworkPath)) {
  console.error(`entry.png not found next to the script: ${artworkPath}`);
  process.exit(1);
}

mkdirSync(destinationDir, { recursive: true });
copyFileSync(artworkPath, join(destinationDir, "entry.png"));
console.log(`entry.png copied to ${destinationDir}`);
