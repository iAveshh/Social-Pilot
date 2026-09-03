// What is actually on this page that would be worth putting on screen?
import { chromium } from 'playwright';

const url = process.argv[2];
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 1600 } });
await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForTimeout(2000);

const report = await page.evaluate(() => {
  const out = { headings: [], tables: [], figures: [], images: [] };
  document.querySelectorAll('h1,h2,h3').forEach(h => {
    const r = h.getBoundingClientRect();
    out.headings.push({ tag: h.tagName, text: h.innerText.trim().slice(0, 90),
                        y: Math.round(r.top + window.scrollY) });
  });
  document.querySelectorAll('table').forEach(t => {
    const r = t.getBoundingClientRect();
    out.tables.push({ y: Math.round(r.top + window.scrollY),
                      h: Math.round(r.height),
                      text: t.innerText.replace(/\s+/g, ' ').trim().slice(0, 200) });
  });
  document.querySelectorAll('figure, figcaption').forEach(f => {
    const r = f.getBoundingClientRect();
    if (r.height > 80) out.figures.push({ y: Math.round(r.top + window.scrollY),
      h: Math.round(r.height), text: f.innerText.replace(/\s+/g, ' ').trim().slice(0, 120) });
  });
  document.querySelectorAll('img').forEach(i => {
    const r = i.getBoundingClientRect();
    if (r.width > 300 && r.height > 150) out.images.push({
      y: Math.round(r.top + window.scrollY), w: Math.round(r.width),
      h: Math.round(r.height), alt: (i.alt || '').slice(0, 100) });
  });
  return out;
});

console.log(JSON.stringify(report, null, 1));
await browser.close();
