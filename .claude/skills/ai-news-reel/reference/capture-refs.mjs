// Capture SPECIFIC evidence from a source page - benchmark charts, tables,
// the headline block. Element screenshots, so the crop is tight and clean.
//
//   node capture_refs.mjs <url> <outDir> <spec> [<spec> ...]
//   spec = "img:2:name"      nth matching <img> (only those >300x150)
//          "sel:h1:name"     first element matching a CSS selector
//          "clip:x,y,w,h:name"
import { chromium } from 'playwright';
import path from 'path';

const [url, outDir, ...specs] = process.argv.slice(2);
const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1280, height: 1600 }, deviceScaleFactor: 2,
});
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForTimeout(2500);

// force every lazy image to load before we start grabbing
await page.evaluate(async () => {
  await new Promise((res) => {
    let y = 0;
    const id = setInterval(() => {
      window.scrollTo(0, y); y += 900;
      if (y > document.body.scrollHeight) { clearInterval(id); res(); }
    }, 90);
  });
});
await page.waitForTimeout(1200);
await page.evaluate(() => window.scrollTo(0, 0));

const bigImgs = await page.$$eval('img', (els) =>
  els.map((e, i) => ({ i, w: e.getBoundingClientRect().width,
                       h: e.getBoundingClientRect().height, alt: e.alt || '' }))
     .filter(o => o.w > 300 && o.h > 150).map(o => o.i));

for (const spec of specs) {
  const [kind, arg, name] = spec.split(':');
  const out = path.join(outDir, name + '.png');
  try {
    if (kind === 'img') {
      const domIndex = bigImgs[Number(arg)];
      const el = (await page.$$('img'))[domIndex];
      await el.scrollIntoViewIfNeeded();
      await page.waitForTimeout(500);
      await el.screenshot({ path: out });
    } else if (kind === 'sel') {
      const el = await page.$(arg);
      await el.scrollIntoViewIfNeeded();
      await page.waitForTimeout(400);
      await el.screenshot({ path: out });
    } else if (kind === 'clip') {
      const [x, y, w, h] = arg.split(',').map(Number);
      await page.evaluate((yy) => window.scrollTo(0, yy), Math.max(0, y - 100));
      await page.waitForTimeout(400);
      await page.screenshot({ path: out, clip: { x, y: 100, width: w, height: h } });
    }
    console.log('ok', name);
  } catch (e) {
    console.log('FAIL', name, String(e).slice(0, 120));
  }
}
await browser.close();
