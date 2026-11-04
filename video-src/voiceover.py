"""Regenerates the voiceover clips in voiceover/ from voiceover/script.json.

Uses the open-source Kokoro text-to-speech model through kokoro-onnx:
    pip install kokoro-onnx soundfile
    and download kokoro-v1.0.onnx and voices-v1.0.bin from
    https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0)

    python video-src/voiceover.py MODEL_DIR [clip ...]

voiceover/pronunciation.json fixes words the model says wrongly: each entry
swaps the model's phonemes for a phrase with corrected ones (stress marks are
ˈ primary and ˌ secondary).

voiceover/delivery.json sets each clip's pace, emphasis and pauses, matched to
a human reference reading of the script.
"""
import json, sys, pathlib
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

VOICE, LANG = 'af_heart', 'en-us'
here = pathlib.Path(__file__).parent / 'voiceover'
model = pathlib.Path(sys.argv[1])
only = set(sys.argv[2:])
k = Kokoro(str(model / 'kokoro-v1.0.onnx'), str(model / 'voices-v1.0.bin'))
script = json.loads((here / 'script.json').read_text())
fixes = json.loads((here / 'pronunciation.json').read_text())
delivery = json.loads((here / 'delivery.json').read_text())


def shape_pauses(audio, sr, wanted):
    """Set pause lengths to the reference reading's: each pause longer than
    0.15 s is matched to the nearest wanted [position, seconds] pause, and
    pauses with no match are shortened to 0.1 s."""
    win = int(0.01 * sr)
    env = np.array([np.sqrt(np.mean(audio[i:i + win] ** 2)) for i in range(0, len(audio) - win, win)])
    quiet = env < env.max() * 0.04
    first = int(np.argmax(~quiet)); last = len(quiet) - int(np.argmax(~quiet[::-1]))
    span = last - first
    runs, i = [], first
    while i < last:
        if quiet[i]:
            j = i
            while j < last and quiet[j]: j += 1
            if (j - i) * 0.01 >= 0.15: runs.append((i, j))
            i = j
        else:
            i += 1
    out, pos, used = [], 0, set()
    for i, j in runs:
        rel = (i - first) / span
        match = min((k for k in range(len(wanted)) if k not in used and abs(wanted[k][0] - rel) < 0.15),
                    key=lambda k: abs(wanted[k][0] - rel), default=None)
        target = wanted[match][1] if match is not None else 0.1
        if match is not None: used.add(match)
        a, b = i * win + int(0.03 * sr), j * win - int(0.03 * sr)   # keep 30 ms of natural decay each side
        out += [audio[pos:a], np.zeros(max(0, int((target - 0.06) * sr)), dtype=audio.dtype)]
        pos = b
    out.append(audio[pos:])
    return np.concatenate(out)


for clip, text in script.items():
    if only and clip not in only:
        continue
    ph = k.tokenizer.phonemize(text, LANG)
    for f in fixes:
        ph = ph.replace(f['from'], f['to'])
    d = delivery[clip]
    for old, new in d['stress']:
        assert old in ph, f'{clip}: {old} not in {ph}'
        ph = ph.replace(old, new)
    audio, sr = k.create(ph, voice=VOICE, speed=d['speed'], lang=LANG, is_phonemes=True)
    # trim silence, keeping a short tail so soft word endings aren't clipped
    loud = np.where(np.abs(audio) > 0.005)[0]
    audio = audio[max(0, loud[0] - 600): loud[-1] + int(0.2 * sr)]
    audio = shape_pauses(audio, sr, d['pauses'])
    sf.write(here / f'{clip}.wav', audio, sr)
    print(f'{clip}: {len(audio) / sr:.2f}s  {ph}')
