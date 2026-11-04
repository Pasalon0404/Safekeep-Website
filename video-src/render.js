// Renders explainer.html to an MP4 with voiceover and background music.
//
//   node video-src/render.js [out.mp4] [fps]          full build
//   node video-src/render.js [out.mp4] [fps] --audio  re-mix the sound only,
//                                                      reusing the last frames
//
// Needs Playwright (Chromium), ffmpeg on PATH, and python3 with numpy for the music.
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2).filter(a => !a.startsWith('--'));
const audioOnly = process.argv.includes('--audio');
const out = args[0] || path.join(__dirname, '..', 'safekeepvault-explainer.mp4');
const fps = Number(args[1] || 30);
const buildDir = path.join(__dirname, 'build');
const silent = path.join(buildDir, 'silent.mp4');

function run(cmd, argv) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, argv, { stdio: ['ignore', 'inherit', 'inherit'] });
    p.on('close', code => code === 0 ? resolve() : reject(new Error(`${cmd} exited ${code}`)));
  });
}

(async () => {
  fs.mkdirSync(buildDir, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'explainer.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.evaluate(() => Promise.all([...document.images].map(i => i.decode())));
  const duration = await page.evaluate(() => window.DURATION);
  const voiceover = await page.evaluate(() => window.VOICEOVER);

  // 1. Frames -> silent video
  if (!audioOnly || !fs.existsSync(silent)) {
    const frames = Math.round(duration * fps);
    const ff = spawn('ffmpeg', [
      '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', silent,
    ], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let i = 0; i < frames; i++) {
      await page.evaluate(t => window.render(t), i / fps);
      const buf = await page.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (i % (fps * 5) === 0) console.error(`frame ${i}/${frames}`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
  }
  await browser.close();

  // 2. Music
  execFileSync('python3', [path.join(__dirname, 'music.py'), String(duration)], { stdio: 'inherit' });

  // 3. Mix: voice clips placed on the timeline, music ducked under the voice
  const inputs = ['-i', silent, '-i', path.join(__dirname, 'music.wav')];
  const parts = [];
  voiceover.forEach((v, i) => {
    inputs.push('-i', path.join(__dirname, 'voiceover', v.clip + '.wav'));
    const ms = Math.round(v.at * 1000);
    parts.push(`[${i + 2}:a]aresample=48000,aformat=channel_layouts=stereo,adelay=${ms}|${ms}[v${i}]`);
  });
  const vlabels = voiceover.map((_, i) => `[v${i}]`).join('');
  const filter = [
    ...parts,
    `${vlabels}amix=inputs=${voiceover.length}:normalize=0,apad,atrim=0:${duration},asplit=2[vo][key]`,
    `[1:a]volume=0.12[mus]`,
    `[mus][key]sidechaincompress=threshold=0.015:ratio=8:attack=30:release=600[duck]`,
    `[vo][duck]amix=inputs=2:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000[a]`,
  ].join(';');

  await run('ffmpeg', [
    '-y', '-v', 'error', ...inputs, '-filter_complex', filter,
    '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k',
    '-t', String(duration), '-movflags', '+faststart', out,
  ]);
  console.error('wrote ' + out);
})();
