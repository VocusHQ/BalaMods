"""Exports a pack's five versions into Odeum (mods/Odeum/packs/<pack>/music/music1-5.ogg).

Same per-track rendering as reference_render.py (LMMS, wobble, per-track gain and lowpass), then:
  - every version is cut to exactly the loop length (BARS x BEATS_PER_BAR beats), so all five stay in sync
  - whatever rings past the loop end is folded back onto the start, so the loop has no click or gap
  - each version is matched to the loudness of its Balatro counterpart (music1-5.ogg), so the
    game's crossfades between places stay level, like the original's; a short look-ahead limiter
    catches the few hits (the A3 landing) that would peak above PEAK
Usage: python export_pack.py PACK [--only main,boss] [--out DIR]   (PACK: crescendo, vesper)
Set BALATRO_MUSIC to a folder with the game's own music1-5.ogg for the loudness match.
"""
import argparse
import importlib
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import maximum_filter1d, uniform_filter1d
from scipy.signal import butter, sosfiltfilt

sys.path.insert(0, str(Path(__file__).parent))
import reference_render as rr  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
RATE = rr.RATE
PEAK = 0.89  # -1 dBFS before vorbis encoding
# pack: {slot: (module, VERSION env)}
PACKS = {
    "crescendo": {1: ("crescendo_garage", None), 2: ("crescendo_versions", "packs"), 3: ("crescendo_versions", "planet"),
                  4: ("crescendo_versions", "shop"), 5: ("crescendo_versions", "boss")},
    "vesper": {1: ("vesper", "main"), 2: ("vesper", "packs"), 3: ("vesper", "planet"), 4: ("vesper", "shop"),
               5: ("vesper", "boss")},
}
NAMES = {1: "main", 2: "packs", 3: "planet", 4: "shop", 5: "boss"}


def load(module, version):
    if version:
        os.environ["VERSION"] = version
    mod = importlib.import_module(module)
    return importlib.reload(mod)


def mixdown(mod, tmp):
    rr.rs = mod  # reference_render.render reads tempo and length from this module
    mix = None
    for i, tr in enumerate(mod.TRACKS):
        gain, *wob = mod.MIX[tr[0]]
        y = rr.wobble(rr.render(tr, tmp), *wob, seed=i) * gain
        cut = getattr(mod, "LOWPASS", {}).get(tr[0])
        if cut:
            y = sosfiltfilt(butter(2, cut, fs=RATE, output="sos"), y, axis=0)
        if mix is not None and len(y) != len(mix):
            n = max(len(y), len(mix))
            y, mix = (np.pad(z, ((0, n - len(z)), (0, 0))) for z in (y, mix))
        mix = y if mix is None else mix + y
    beat = 60 / mod.BPM
    mix = mix[round(mod.LEAD_IN * beat * RATE):]
    loop = round(mod.BARS * mod.BEATS_PER_BAR * beat * RATE)
    out = mix[:loop].copy()
    tail = mix[loop:]
    while len(tail):  # fold the ring-out back onto the start
        n = min(len(tail), loop)
        out[:n] += tail[:n]
        tail = tail[n:]
    return out


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)


def limit(x, ceiling=PEAK, ms=8):
    """Look-ahead peak limiter: the gain dips smoothly around a peak instead of clipping it."""
    w = max(1, int(RATE * ms / 1000))
    env = maximum_filter1d(np.abs(x).max(1), 2 * w + 1)
    g = np.minimum(1.0, ceiling / np.maximum(env, 1e-9))
    g = uniform_filter1d(maximum_filter1d(1 - g, 2 * w + 1), 2 * w + 1)  # widen, then smooth the dip
    return x * (1 - g)[:, None]


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(RATE), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pack", choices=sorted(PACKS))
    ap.add_argument("--only", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--reference", default=os.environ.get("BALATRO_MUSIC", ""),
                    help="folder with the game's music1-5.ogg (local only, never in the repo)")
    a = ap.parse_args()
    slots = [s for s, n in NAMES.items() if not a.only or n in a.only.split(",")]
    out_dir = Path(a.out or ROOT / "mods" / "Odeum" / "packs" / a.pack / "music")
    tmp = out_dir / ".export_tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    mixes = {}
    for s in slots:
        module, version = PACKS[a.pack][s]
        print(f"rendering {NAMES[s]} ...", flush=True)
        mixes[s] = mixdown(load(module, version), tmp)
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()

    for s in slots:
        ref = Path(a.reference) / f"music{s}.ogg"
        target = rms_db(decode(ref)) if ref.is_file() else -19.0
        y = limit(mixes[s] * 10 ** ((target - rms_db(mixes[s])) / 20))
        path = out_dir / f"music{s}.ogg"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(RATE), "-ac", "2", "-i", "-",
                        "-c:a", "libvorbis", "-q:a", "6", str(path)], input=y.astype(np.float32).tobytes(), check=True)
        print(f"{path.name} {NAMES[s]:7s} {len(y) / RATE:.2f}s  target {target:.1f}  rms {rms_db(y):.1f} dB  "
              f"peak {np.abs(y).max():.2f}")


if __name__ == "__main__":
    main()
