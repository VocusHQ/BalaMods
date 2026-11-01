"""Crescendo melody samples: two 8-bar A sections, same ensemble and accompaniment, different tune.

SAMPLE=close  Balatro's lead notes (F5 -> C5 -> Bb4) stay as anchors; the clarinet flows between them.
SAMPLE=free   a new, catchier tune over the same chords and bass riff (max F5, phrased 3+4).
Both: bassoon countermelody, pizzicato riff, harp chords, brushed snare ostinato (from crescendo_bolero.py).
Render: SAMPLE=close python reference_render.py OUT.mp3 crescendo_samples
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403
from crescendo_main import RIFF, k  # noqa: E402
from crescendo_bolero import HARP, ROOT, SNARE_STEPS, ACCENT, PIZZ, HARP_P, BASSOON, CLARINET  # noqa: E402

SAMPLE = os.environ.get("SAMPLE", "close")
BPM, BEATS_PER_BAR = 150, 7
LEAD_IN = 1
FORM = ["F", "Db", "Bb", "Eb"] * 2
BARS = len(FORM)


def line(s):
    """'F5 1.5, Eb5 .5, - 1' -> [(key or None, beats)]; each bar must add up to 7 beats."""
    return [(None if n == "-" else k(n), float(l)) for n, l in (x.split() for x in s.split(","))]


MELODY = {
    "close": [  # anchors: F5 (bars 1-2), C5 (bar 3), Bb4 (bar 4), Db5 pickup
        "F5 1.5, Eb5 .5, C5 1, A4 1, C5 1, F5 2",
        "F5 2, Eb5 .5, Db5 .5, C5 1, Ab4 1, Db5 1, Eb5 1",
        "C5 2.5, Db5 .5, C5 1, Bb4 1, F4 1, Ab4 1",
        "Bb4 3, Gb4 1, Ab4 1, Bb4 1.5, Db5 .5",
        "F5 1, C5 .5, Eb5 .5, F5 1, Eb5 .5, C5 .5, A4 1, C5 2",
        "Db5 1.5, C5 .5, Ab4 1, F4 1, Ab4 1, C5 1, Db5 1",
        "C5 1.5, Bb4 .5, Db5 1, C5 2, Bb4 1, F4 1",
        "Gb4 1.5, Ab4 .5, Bb4 1, Bb4 3.5, Db5 .5",
    ],
    "free": [  # motif: "da-da DAH dah" (3) + answer (4), sequenced down the chords
        "C5 .5, Eb5 .5, F5 1, Eb5 1, C5 1, A4 .5, C5 .5, F4 2",
        "Ab4 .5, C5 .5, Db5 1, C5 1, Ab4 1, F4 .5, Ab4 .5, Db4 2",
        "Bb4 .5, Db5 .5, F5 1, Eb5 1, Db5 1, C5 .5, Bb4 .5, F4 2",
        "Gb4 .5, Bb4 .5, Db5 1, C5 1, Bb4 1.5, Ab4 .5, Gb4 1, F4 1",
        "C5 .5, Eb5 .5, F5 1, Eb5 1, C5 1, Eb5 .5, F5 .5, C5 2",
        "Db5 .5, C5 .5, Ab4 1, F4 1, Ab4 1, C5 .5, Db5 .5, Eb5 2",
        "F5 1.5, Eb5 .5, Db5 1, C5 1, Bb4 .5, C5 .5, Db5 1, F4 1",
        "Gb4 .5, Bb4 .5, Db5 1, C5 1, Bb4 3, - 1",
    ],
}
# Bassoon countermelody (both samples): moves when the tune holds, rests under busy bars
COUNTER = [
    "F2 3, A2 2, C3 2",
    "Db3 3, C3 2, Bb2 2",
    "Bb2 1, Db3 1, F3 1, Eb3 2, Db3 2",
    "Eb3 3, Db3 2, Bb2 1, C3 1",
    "F2 3, Eb3 2, C3 2",
    "Db3 3, F3 2, Eb3 2",
    "Db3 1, C3 1, Bb2 1, F2 2, Ab2 2",
    "Gb2 3, Bb2 2, Db3 1, C3 1",
]


def at(bar, beat):
    return 0, LEAD_IN + bar * BEATS_PER_BAR + beat


def play(bars, vel, shift=0):
    out = []
    for bar, s in enumerate(bars):
        beat = 0
        for key, l in line(s):
            if key is not None:
                out.append(note(*at(bar, beat), key + shift, l - .08, vel))
            beat += l
        assert abs(beat - BEATS_PER_BAR) < 1e-6, (bar, s, beat)
    return out


def clarinet():
    return play(MELODY[SAMPLE], 90)


def bassoon():
    return play(COUNTER, 74)


def pizz():
    return [note(*at(bar, b), key, min(l, 1), 120) for bar, r in enumerate(FORM) for b, key, l in RIFF[r]]


def harp():
    return [note(*at(bar, b), k(n), 2.5, 66) for bar, r in enumerate(FORM) for b in (0, 3) for n in HARP[r]]


def snare():
    return [note(*at(bar, s / 4), SNARE, .25, 62 if s in ACCENT else 44) for bar in range(BARS) for s in SNARE_STEPS]


TRACKS = [
    ("Pizz", (PIZZ, 0), pizz),
    ("Harp", (HARP_P, 0), harp),
    ("Bassoon", (BASSOON, 0), bassoon),
    ("Clarinet", (CLARINET, 0), clarinet),
    ("Snare", (BRUSH_KIT, 128), snare),
]
MIX = {"Pizz": (1.6, 0, 0, 0, 0), "Harp": (0.7, 0, 0, 0, 0), "Bassoon": (0.45, 0, 0, 0, 0),
       "Clarinet": (0.75, 0, 0, 0, 0), "Snare": (0.6, 0, 0, 0, 0)}
LOWPASS = {"Clarinet": 2000, "Harp": 3500, "Snare": 4500, "Bassoon": 3000}
