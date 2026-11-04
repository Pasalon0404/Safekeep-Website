"""Generates the explainer's background music (an original track, no samples).

Writes music.wav next to this file: 48 kHz stereo, the length given in seconds
(default 62.1, the video's length). Needs only numpy.

    python3 video-src/music.py [seconds]
"""
import sys, wave, pathlib
import numpy as np

SR = 48000
BPM = 96
BEAT = 60 / BPM
BAR = 4 * BEAT
LENGTH = float(sys.argv[1]) if len(sys.argv) > 1 else 62.1
N = int(LENGTH * SR)
rng = np.random.default_rng(7)

def hz(midi): return 440.0 * 2 ** ((midi - 69) / 12)

# C - G - Am - F, one bar each (MIDI notes)
CHORDS = [
    [48, 55, 60, 64, 67],   # C
    [43, 55, 59, 62, 67],   # G
    [45, 57, 60, 64, 69],   # Am
    [41, 53, 57, 60, 65],   # F
]
ARP = [0, 2, 3, 4, 3, 2, 3, 1]   # chord-tone indexes per 8th note

L = np.zeros(N); R = np.zeros(N)

def add(sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    L[i:i + len(sig)] += sig * (1 - pan) ** 0.5
    R[i:i + len(sig)] += sig * (1 + pan) ** 0.5

def onepole_lp(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    # vectorised enough for a minute of audio
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y

def pad_note(f, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.zeros_like(t)
    for det in (-0.12, 0.0, 0.11):              # three detuned voices
        ff = f * 2 ** (det / 12)
        for h in range(1, 7):                    # soft saw: few harmonics, falling fast
            s += np.sin(2 * np.pi * ff * h * t + rng.uniform(0, 6.28)) / (h ** 1.6)
    env = np.minimum(1, t / 0.9) * np.minimum(1, (dur - t) / 0.9)
    return s * env * 0.05

def pluck(f, dur=0.6):
    t = np.arange(int(dur * SR)) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.1 * np.sin(2 * np.pi * 3 * f * t)
    return s * np.exp(-t * 7) * np.minimum(1, t / 0.004) * 0.11

def bass(f, dur):
    t = np.arange(int(dur * SR)) / SR
    s = np.tanh(1.6 * np.sin(2 * np.pi * f * t)) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
    return s * np.minimum(1, t / 0.01) * np.exp(-t * 1.2) * 0.16

def kick():
    t = np.arange(int(0.35 * SR)) / SR
    f = 48 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * 0.5

def hat():
    t = np.arange(int(0.06 * SR)) / SR
    n = rng.standard_normal(len(t))
    n = n - np.concatenate([[0], n[:-1]])          # crude high-pass
    return n * np.exp(-t * 70) * 0.03

bars = int(np.ceil(LENGTH / BAR))
for b in range(bars):
    t0 = b * BAR
    chord = CHORDS[b % 4]
    last = b == bars - 1
    # pad all the way through
    for k, m in enumerate(chord[1:]):
        add(pad_note(hz(m), BAR + 0.9), t0, pan=(k - 1.5) * 0.25)
    # bass from bar 2
    if b >= 2:
        for q in range(4):
            add(bass(hz(chord[0] - 12 if chord[0] > 44 else chord[0]), BEAT), t0 + q * BEAT)
    # arpeggio from bar 2, an octave up
    if b >= 2 and not last:
        for e in range(8):
            m = chord[ARP[e]] + 12
            add(pluck(hz(m)), t0 + e * BEAT / 2, pan=0.3 if e % 2 else -0.3)
    # soft kick from bar 4, hats from bar 8
    if 4 <= b and not last:
        for q in range(4):
            add(kick(), t0 + q * BEAT)
    if 8 <= b and not last:
        for e in range(8):
            add(hat(), t0 + e * BEAT / 2, pan=0.4, gain=1.0 if e % 2 else 0.5)

# soften the whole mix, simple stereo echo, fade in and out
L = onepole_lp(L, 7000); R = onepole_lp(R, 7000)
d = int(BEAT * 0.75 * SR)
L[d:] += 0.22 * R[:-d]; R[d:] += 0.22 * L[:-d]
t = np.arange(N) / SR
fade = np.minimum(1, t / 1.5) * np.minimum(1, (LENGTH - t) / 3.0)
L *= fade; R *= fade
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.89, R / peak * 0.89

out = pathlib.Path(__file__).with_name('music.wav')
pcm = (np.stack([L, R], axis=1) * 32767).astype('<i2')
with wave.open(str(out), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'wrote {out} ({LENGTH:.1f}s)')
