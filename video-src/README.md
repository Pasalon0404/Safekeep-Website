# Explainer video

`safekeepvault-explainer.mp4` (site root) is a roughly one-minute, 1920x1080 overview of
SafeKeepVault: on-screen text and app screenshots, a synthetic voiceover, and
background music. It is embedded on the home page with
`safekeepvault-explainer-poster.jpg` as its poster frame and
`safekeepvault-explainer.vtt` as its captions. It can be uploaded to YouTube
as-is (see `YOUTUBE.md`).

## What's in here

- `explainer.html`: every frame of the video. Scene timings (`SCENES`) and
  when each voice clip plays (`VO`) are near the bottom. Open it in a browser
  with `?play` to preview the picture (no sound).
- `voiceover/`: one WAV clip per sentence, and `script.json` with the words.
  Made with the open-source Kokoro text-to-speech model (voice `af_heart`)
  by `voiceover.py`; `pronunciation.json` fixes words it says wrongly, and
  `delivery.json` sets each line's pace, emphasis and pauses to match a human
  reference reading of the script. Names
  are spelled out for the voice ("Safe Keep Vault").
- `music.py`: generates the background music from code (an original track,
  no samples or licensed audio).
- `render.js`: renders the frames, makes the music, and mixes it all to MP4.
  The music is turned down automatically while the voice is speaking.
- `captions.js`: writes the captions file from `VO` and `script.json`.

## Rebuilding

Needs Node.js, Playwright (Chromium), ffmpeg, and python3 with numpy. From the
repository root:

    node video-src/render.js safekeepvault-explainer.mp4 30
    node video-src/captions.js
    ffmpeg -y -ss 18 -i safekeepvault-explainer.mp4 -frames:v 1 -vf scale=1280:720 -q:v 3 safekeepvault-explainer-poster.jpg

A full render takes about 8 minutes. To change only the sound (music level,
clip timing), add `--audio` to the render command to reuse the last frames.
After replacing the video, bump the `?v=` number on its links in `index.html`
so browsers fetch the new file.

## Changing the voiceover

Edit the sentence in `voiceover/script.json`, then regenerate its clip with
`voiceover.py` (instructions for installing the Kokoro model are at the top of
that file):

    python video-src/voiceover.py MODEL_DIR s1b

If a word comes out wrong, add an entry to `voiceover/pronunciation.json`
swapping the model's phonemes for corrected ones (`voiceover.py` prints the
phonemes it used for each clip). If a clip gets longer, adjust the scene
timings (`SCENES` and `VO`) in `explainer.html` and re-run `captions.js`.
