"""Renders reference_sketch.py track by track, adds Balatro-style pitch wobble, and mixes to an mp3.

Wobble measured from the original (Demucs stems): fast vibrato ~5 Hz, +-10-25 cents, plus a slow
tape-like drift of about +-25 cents. Applied as a time-varying delay (pitch modulation) per track.
Usage: python reference_render.py OUT.mp3 [module, default reference_sketch]
"""
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfiltfilt

sys.path.insert(0, str(Path(__file__).parent))
import importlib  # noqa: E402
from lmmsgen import build  # noqa: E402

LMMS = "C:/Program Files/LMMS/lmms.exe"
RATE = 44100
# track: (gain, fast cents, fast Hz, slow cents, slow Hz)
MIX = {"Bass": (1.0, 4, 5.0, 10, 0.31), "Pad": (0.55, 8, 4.7, 22, 0.37),
       "Lead": (0.6, 20, 5.6, 22, 0.43), "Drums": (0.7, 0, 0, 0, 0)}


def render(track, tmp):
    tree = build([track], rs.BPM, -(-(rs.LEAD_IN + rs.BARS * rs.BEATS_PER_BAR + 4) // 4))
    mmp, wav = tmp / f"{track[0]}.mmp", tmp / f"{track[0]}.wav"
    with open(mmp, "wb") as f:
        f.write(b'<?xml version="1.0"?>\n<!DOCTYPE lmms-project>\n')
        tree.write(f, encoding="utf-8")
    subprocess.run([LMMS, "render", str(mmp), "-f", "wav", "-s", str(RATE), "-o", str(wav)], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(wav), "-f", "f32le", "-ac", "2", "-ar", str(RATE), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def wobble(x, fast_c, fast_hz, slow_c, slow_hz, seed):
    """Pitch modulation via a time-varying read position: pitch ratio = 1 + d(delay)/dt."""
    if fast_c == 0 and slow_c == 0:
        return x
    rng = np.random.default_rng(seed)
    t = np.arange(len(x)) / RATE
    rate = fast_hz * (1 + 0.15 * np.sin(2 * np.pi * 0.21 * t + rng.uniform(0, 6)))  # rate drifts a little
    phase = 2 * np.pi * np.cumsum(rate) / RATE
    cents = fast_c * np.sin(phase) + slow_c * np.sin(2 * np.pi * slow_hz * t + rng.uniform(0, 6))
    ratio = 2 ** (cents / 1200)
    pos = np.cumsum(ratio) - ratio[0]
    pos = pos - (pos[-1] - (len(x) - 1)) * t / t[-1]  # keep total length (and sync) unchanged
    return np.stack([np.interp(pos, np.arange(len(x)), x[:, c]) for c in range(2)], 1)


def main(out):
    tmp = Path(out).parent / ".render_ref"
    tmp.mkdir(exist_ok=True)
    mix = None
    for i, tr in enumerate(rs.TRACKS):
        gain, *wob = getattr(rs, "MIX", MIX)[tr[0]]
        y = wobble(render(tr, tmp), *wob, seed=i) * gain
        cut = getattr(rs, "LOWPASS", {}).get(tr[0])
        if cut:  # gentle tone filter: softens edgy samples (Locked's no-high-pitch rule)
            y = sosfiltfilt(butter(2, cut, fs=RATE, output="sos"), y, axis=0)
        if mix is not None and len(y) != len(mix):  # pad the shorter one, so no track is cut off
            n = max(len(y), len(mix))
            y, mix = (np.pad(z, ((0, n - len(z)), (0, 0))) for z in (y, mix))
        mix = y if mix is None else mix + y
    mix = mix[int(0.4 * RATE):]  # drop the one-beat lead-in
    mix *= 0.7 / np.abs(mix).max()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(RATE), "-ac", "2", "-i", "-",
                    "-af", "loudnorm=I=-16:TP=-1.5", "-ar", str(RATE), str(out)],
                   input=mix.astype(np.float32).tobytes(), check=True)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()
    print(out)


if __name__ == "__main__":
    rs = importlib.import_module(sys.argv[2] if len(sys.argv) > 2 else "reference_sketch")
    main(sys.argv[1])
