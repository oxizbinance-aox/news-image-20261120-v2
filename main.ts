// Entry program for make.fun news-image-20261120 (Node 22, stdlib only).
//
// The image is drawn in code by draw_image.py (PIL) and ships in this
// repository as entry.png: one 1024x1024 picture summing up the world
// news of Friday 20 November 2026. This program just copies it to the
// output directory, so both grader runs write identical bytes.
//
// Local run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
// The grader's /output already exists; creating it is only for local runs.
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
