// Writes a captions file from the narration timings in a video page
// (window.CAPTIONS, built from LINES).
//   node video-src/captions.js                                   explainer
//   node video-src/captions.js features.html safekeepvault-features.vtt
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const fmt = s => {
  const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, sec = (s % 60).toFixed(3).padStart(6, '0');
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${sec}`;
};
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, process.argv[2] || 'explainer.html'));
  const caps = await page.evaluate(() => window.CAPTIONS);
  await browser.close();
  let vtt = 'WEBVTT\n\n';
  caps.forEach((c, i) => { vtt += `${i + 1}\n${fmt(c.start)} --> ${fmt(c.end)}\n${c.text}\n\n`; });
  const out = path.join(__dirname, '..', process.argv[3] || 'safekeepvault-explainer.vtt');
  fs.writeFileSync(out, vtt);
  console.log('wrote ' + out);
})();
