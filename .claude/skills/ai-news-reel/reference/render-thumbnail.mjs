// Render a Reel cover image, and prove it survives the crops Instagram applies.
//
//   node render-thumbnail.mjs <thumbnail.html> <out.png>
//
// Writes the 1080x1920 cover plus two crop proofs beside it:
//   <out>.4x5.png   the 1080x1350 profile-grid crop
//   <out>.1x1.png   the 1080x1080 square crop
//
// Instagram never shows the whole frame in a grid. Anything that has to be
// read - the hook line, the brand, the number - belongs in the centre band
// (roughly y=560..1400), or it gets cut off exactly where it matters.
import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';

const [src, out] = process.argv.slice(2);
if (!src || !out) {
  console.error('usage: node render-thumbnail.mjs <thumbnail.html> <out.png>');
  process.exit(1);
}
fs.mkdirSync(path.dirname(path.resolve(out)), { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
await page.goto('file://' + path.resolve(src), { waitUntil: 'networkidle' });
// webfonts land after networkidle often enough to matter
await page.evaluate(() => document.fonts.ready);
await page.waitForTimeout(600);

await page.screenshot({ path: out });

const base = out.replace(/\.png$/i, '');
const CROPS = [
  { name: `${base}.4x5.png`, clip: { x: 0, y: 285, width: 1080, height: 1350 } },
  { name: `${base}.1x1.png`, clip: { x: 0, y: 420, width: 1080, height: 1080 } },
];
for (const c of CROPS) await page.screenshot({ path: c.name, clip: c.clip });

console.log(JSON.stringify({
  cover: out, crops: CROPS.map((c) => c.name),
  note: 'Open all three. If the hook line is cut in either crop, move it inward.',
}, null, 1));
await browser.close();
