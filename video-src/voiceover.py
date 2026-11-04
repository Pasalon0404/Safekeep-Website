"""Regenerates the voiceover clips in voiceover/ from voiceover/script.json.

Uses the open-source Kokoro text-to-speech model through kokoro-onnx:
    pip install kokoro-onnx soundfile
    and download kokoro-v1.0.onnx and voices-v1.0.bin from
    https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0)

    python video-src/voiceover.py MODEL_DIR [clip ...]

voiceover/pronunciation.json fixes words the model says wrongly: each entry
swaps the model's phonemes for a phrase with corrected ones (stress marks are
ˈ primary and ˌ secondary).
"""
import json, sys, pathlib
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

VOICE, SPEED, LANG = 'af_heart', 1.0, 'en-us'
here = pathlib.Path(__file__).parent / 'voiceover'
model = pathlib.Path(sys.argv[1])
only = set(sys.argv[2:])
k = Kokoro(str(model / 'kokoro-v1.0.onnx'), str(model / 'voices-v1.0.bin'))
script = json.loads((here / 'script.json').read_text())
fixes = json.loads((here / 'pronunciation.json').read_text())

for clip, text in script.items():
    if only and clip not in only:
        continue
    ph = k.tokenizer.phonemize(text, LANG)
    for f in fixes:
        ph = ph.replace(f['from'], f['to'])
    audio, sr = k.create(ph, voice=VOICE, speed=SPEED, lang=LANG, is_phonemes=True)
    # trim silence, keeping a short tail so soft word endings aren't clipped
    loud = np.where(np.abs(audio) > 0.005)[0]
    audio = audio[max(0, loud[0] - 600): loud[-1] + int(0.2 * sr)]
    sf.write(here / f'{clip}.wav', audio, sr)
    print(f'{clip}: {len(audio) / sr:.2f}s  {ph}')
