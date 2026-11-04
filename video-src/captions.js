// Writes safekeepvault-explainer.vtt (captions) from the voiceover timings in
// explainer.html and the words in voiceover/script.json.
//   node video-src/captions.js
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const fmt = s => {
  const h = Math.floor(s / 3600), m = Math.floor(s / 60) % 60, sec = (s % 60).toFixed(3).padStart(6, '0');
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${sec}`;
};
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.join(__dirname, 'explainer.html'));
  const vo = await page.evaluate(() => window.VOICEOVER);
  await browser.close();
  const words = JSON.parse(fs.readFileSync(path.join(__dirname, 'voiceover', 'script.json'), 'utf8'));
  // The script spells some names out for the voice; captions use the real spelling.
  const display = t => t.replace(/Safe Keep Vault/g, 'SafeKeepVault').replace(/safe keep bitcoin dot com/g, 'safekeepbitcoin.com');
  let vtt = 'WEBVTT\n\n';
  vo.forEach((v, i) => {
    const len = Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
      path.join(__dirname, 'voiceover', v.clip + '.wav')]).toString());
    const end = Math.min(v.at + len + 0.3, vo[i + 1] ? vo[i + 1].at - 0.05 : v.at + len + 1);
    vtt += `${i + 1}\n${fmt(v.at)} --> ${fmt(end)}\n${display(words[v.clip])}\n\n`;
  });
  const out = path.join(__dirname, '..', 'safekeepvault-explainer.vtt');
  fs.writeFileSync(out, vtt);
  console.log('wrote ' + out);
})();
