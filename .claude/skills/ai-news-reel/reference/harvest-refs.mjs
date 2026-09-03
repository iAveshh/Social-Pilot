// Harvest reference material from ANY article URL.
//
//   node harvest-refs.mjs <url> <outDir>
//
// Writes <outDir>/manifest.json plus the captures it found:
//   header.png   the title block, WITH headroom (never crop tight to the text)
//   hero.png     the article's hero art - og:image, or the big image under <h1>
//   chart_N.png  every figure that looks like a chart/benchmark/table
//
// Nothing here is story-specific: it reads the page and reports what exists.
import { chromium } from 'playwright';
import path from 'path';
import fs from 'fs';

const [url, outDir] = process.argv.slice(2);
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1280, height: 1600 }, deviceScaleFactor: 2,
});
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForTimeout(2500);

// lazy-loaded charts only exist after a full scroll
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
await page.waitForTimeout(400);

// Sticky/fixed chrome (nav bars, cookie banners, share rails) floats over
// element screenshots and lands in the crop. Hide it before capturing.
await page.addStyleTag({ content: `
  [data-hf-hidden]{visibility:hidden !important}
` });
await page.evaluate(() => {
  document.querySelectorAll('body *').forEach((el) => {
    const p = getComputedStyle(el).position;
    if (p === 'fixed' || p === 'sticky') el.setAttribute('data-hf-hidden', '1');
  });
});
await page.waitForTimeout(200);

const meta = await page.evaluate(() => {
  const pick = (s) => document.querySelector(s)?.getAttribute('content') || null;
  const h1 = document.querySelector('h1');
  const CHARTY = /(chart|graph|benchmark|comparison|score|results?|eval|performance|vs\b|pass@)/i;

  const imgs = [...document.querySelectorAll('img')].map((e, domIndex) => {
    const r = e.getBoundingClientRect();
    return {
      domIndex,
      w: Math.round(r.width), h: Math.round(r.height),
      y: Math.round(r.top + window.scrollY),
      alt: e.alt || '',
      charty: CHARTY.test(e.alt || ''),
    };
  }).filter(o => o.w > 280 && o.h > 140);

  return {
    title: document.title,
    h1: h1 ? h1.innerText.trim() : null,
    ogImage: pick('meta[property="og:image"]') || pick('meta[name="twitter:image"]'),
    siteName: pick('meta[property="og:site_name"]'),
    imgs,
  };
});

const manifest = { url, ...meta, captured: {} };

// --- header block, with headroom -----------------------------------------
// Cropping flush to the headline reads as misaligned. Take the H1's box and
// pad generously above it so the title has air.
try {
  const box = await (await page.$('h1')).boundingBox();
  const PAD_TOP = 120, PAD_X = 56, BELOW = 330;
  const clip = {
    x: Math.max(0, box.x - PAD_X),
    y: Math.max(0, box.y - PAD_TOP),
    width: Math.min(1280 - Math.max(0, box.x - PAD_X), box.width + PAD_X * 2),
    height: PAD_TOP + box.height + BELOW,
  };
  await page.screenshot({ path: path.join(outDir, 'header.png'), clip });
  manifest.captured.header = 'header.png';
} catch (e) { manifest.captured.headerError = String(e).slice(0, 120); }

// --- hero art -------------------------------------------------------------
// Prefer og:image (the publisher's own choice); else the largest image
// sitting above the first 1600px of the page.
try {
  if (meta.ogImage) {
    const buf = await (await page.request.get(meta.ogImage)).body();
    fs.writeFileSync(path.join(outDir, 'hero.png'), buf);
    manifest.captured.hero = 'hero.png';
    manifest.captured.heroSource = 'og:image';
  } else {
    const top = meta.imgs.filter(i => i.y < 1600).sort((a, b) => b.w * b.h - a.w * a.h)[0];
    if (top) {
      const el = (await page.$$('img'))[top.domIndex];
      await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(300);
      await el.screenshot({ path: path.join(outDir, 'hero.png') });
      manifest.captured.hero = 'hero.png';
      manifest.captured.heroSource = 'first-large-image';
    }
  }
} catch (e) { manifest.captured.heroError = String(e).slice(0, 120); }

// --- charts ---------------------------------------------------------------
const charts = meta.imgs.filter(i => i.charty && i.y > 900);
manifest.captured.charts = [];
for (let n = 0; n < charts.length && n < 8; n++) {
  const c = charts[n];
  const name = `chart_${n}.png`;
  try {
    const el = (await page.$$('img'))[c.domIndex];
    await el.scrollIntoViewIfNeeded(); await page.waitForTimeout(400);
    await el.screenshot({ path: path.join(outDir, name) });
    manifest.captured.charts.push({ file: name, alt: c.alt, w: c.w, h: c.h });
  } catch (e) { /* a chart that won't capture is not fatal */ }
}

fs.writeFileSync(path.join(outDir, 'manifest.json'), JSON.stringify(manifest, null, 1));
console.log(JSON.stringify({
  h1: manifest.h1, hero: manifest.captured.heroSource,
  header: !!manifest.captured.header,
  charts: manifest.captured.charts.map(c => c.alt.slice(0, 70)),
}, null, 1));
await browser.close();
