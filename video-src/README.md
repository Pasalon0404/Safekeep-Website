# Explainer video

`safekeepvault-explainer.mp4` (site root) is a 60-second, 1920x1080 overview of
SafeKeepVault: on-screen text and app screenshots, no narration, no music.
It is embedded on the home page with `safekeepvault-explainer-poster.jpg` as its
poster frame, and can be uploaded to YouTube as-is (see `YOUTUBE.md`).

## Editing it

All of the video is in `explainer.html`. Change the wording there, then preview it
in a browser by opening `explainer.html?play`.

## Rebuilding the MP4

Needs Node.js, Playwright (Chromium) and ffmpeg. From the repository root:

    node video-src/render.js safekeepvault-explainer.mp4 30
    ffmpeg -y -ss 14 -i safekeepvault-explainer.mp4 -frames:v 1 -vf scale=1280:720 -q:v 3 safekeepvault-explainer-poster.jpg

The render takes about 7 minutes. Scene timings are in the `SCENES` list near the
bottom of `explainer.html`.
