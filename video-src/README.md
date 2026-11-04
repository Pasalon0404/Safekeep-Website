# Explainer video

`safekeepvault-explainer.mp4` (site root) is an 80-second, 1920x1080 overview of
SafeKeepVault: on-screen text and app screenshots, a recorded narration, and
background music. It is embedded on the home page with
`safekeepvault-explainer-poster.jpg` as its poster frame and
`safekeepvault-explainer.vtt` as its captions. It can be uploaded to YouTube
as-is (see `YOUTUBE.md`).

## What's in here

- `narration.flac`: the narration, edited (retakes removed) and cleaned up
  (high-pass, light noise reduction, gentle compression).
- `explainer.html`: every frame of the video. The timeline follows the
  narration: `LINES` near the bottom lists when each line (and each phrase
  within it) starts and ends in `narration.flac`, with its text. Scenes change
  between lines and each card appears as its words are spoken. Open the file in
  a browser with `?play` to preview the picture (no sound).
- `music.py`: generates the background music from code (an original track,
  no samples or licensed audio).
- `render.js`: renders the frames, makes the music, and mixes it all to MP4.
  The music is turned down automatically while the narration is playing.
- `captions.js`: writes the captions file from `LINES`.

## Rebuilding

Needs Node.js, Playwright (Chromium), ffmpeg, and python3 with numpy. From the
repository root:

    node video-src/render.js safekeepvault-explainer.mp4 30
    node video-src/captions.js
    ffmpeg -y -ss 20 -i safekeepvault-explainer.mp4 -frames:v 1 -vf scale=1280:720 -q:v 3 safekeepvault-explainer-poster.jpg

A full render takes about 10 minutes. To change only the sound (music level),
add `--audio` to the render command to reuse the last frames. After replacing
the video, bump the `?v=` number on its links in `index.html` so browsers fetch
the new file.

## Re-recording the narration

Replace `narration.flac`, then update the times in `LINES` to match (the start
and end of each line, and of each phrase where a line has more than one). The
scenes, cards, music length and captions all follow from those times.
