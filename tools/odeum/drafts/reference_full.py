"""Full 62-bar reference of the original Balatro theme, played straight from the cleaned transcription.

Reads music/reference/bass_notes.json and other_long.json (local only: transcribed from the game's
music1 via Demucs + Basic Pitch, see music/ORIGINAL.md). Notes are [start16, key, len16, velocity, avg].
Synth notes from Bb4 up go to the lead, the rest to the pad. Drums: the measured pattern from bar 2.
Render with: python reference_render.py OUT.mp3 reference_full
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403

REF = Path(__file__).resolve().parents[3] / "music" / "reference"
BPM, BEATS_PER_BAR, BARS = 150, 7, 62
LEAD_IN = 1
LEAD_FROM = 70  # Bb4


def at(beat):
    return 0, LEAD_IN + beat


def load(name):
    return [tuple(n) for n in json.loads((REF / name).read_text())]


def clean_bass():
    ns = sorted(n for n in load("bass_notes.json") if 24 <= n[1] <= 51)
    # drop octave ghosts: a note starting with (within a 16th) a longer note 12 below
    ns = [n for n in ns if not any(m[1] == n[1] - 12 and abs(m[0] - n[0]) <= 1 and m[2] > n[2] for m in ns)]
    out = []
    for i, (s, k, l, v, _) in enumerate(ns):  # monophonic: cut each note at the next one
        nxt = next((m[0] for m in ns[i + 1:] if m[0] > s), s + l)
        out.append(note(*at(s / 4), k, min(l, nxt - s) / 4, min(115, v + 25)))
    return out


def synth(lo, hi, boost):
    return [note(*at(s / 4), k, l / 4, min(110, v + boost)) for s, k, l, v, _ in load("other_long.json")
            if lo <= k < hi]


def drums():
    out = []
    for bar in range(1, BARS):  # bar 1 has no drums
        base = bar * BEATS_PER_BAR
        soft = 0.75 if bar == 1 else 1
        out += [note(*at(base + b), KICK, .5, int(110 * soft)) for b in (0, 1.5, 4.5, 5)]
        out += [note(*at(base + b), SNARE, .5, int(100 * soft)) for b in (2, 6)]
        out += [note(*at(base + h / 2), CLOSED_HH, .25, int((85 if h % 2 == 0 else 55) * soft)) for h in range(14)]
    return out


TRACKS = [
    ("Bass", (38, 0), clean_bass),
    ("Pad", (WARM_PAD, 0), lambda: synth(55, LEAD_FROM, 20)),
    ("Lead", (80, 0), lambda: synth(LEAD_FROM, 85, 25)),
    ("Drums", (STANDARD_KIT, 128), drums),
]
