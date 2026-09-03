// Capture a "receipt" — the actual source page behind a claim.
// Free, and a screenshot is inherently on-aesthetic for a terminal look.
import { chromium } from 'playwright';

const url = process.argv[2];
const out = process.argv[3];
const clipH = Number(process.argv[4] || 720);

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1280, height: 1600 },
  deviceScaleFactor: 2,
});
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
// let webfonts settle so the capture isn't a fallback-font frame
await page.waitForTimeout(2500);
await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1280, height: clipH } });
await browser.close();
console.log('captured', out);
