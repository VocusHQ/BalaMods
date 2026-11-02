"""Basilicus samples: the Balatro theme as medieval tavern / royal court dance music. Two dance feels.

Kept from Balatro: the chord loop (F7, Dbmaj7, Bbm, Ebm7 / F7, Bbm, Bbm, Ebm7) and the lead anchors
(F, C, Bb). Own tune, own groove. Straight eighths (Vesper owns the triplet shuffle).
  SAMPLE=estampie  4/4, two bars per chord: frame drum "DUM tek-tek DUM-DUM tek", stomps, claps
  SAMPLE=dance7    7/4 grouped 2+2+3 (Balkan court dance, the original's meter), one bar per chord
Band: lute (plucked nylon + harp) picking eighths, hurdy-gurdy drone (low accordion on root + fifth),
English horn (crumhorn-like reed) on the tune, a fiddle joins in unison in the second half, bassoon bass.
All low and warm (no-highs rule). Render: SAMPLE=dance7 python reference_render.py OUT.mp3 basilicus_samples
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403
from crescendo_main import k  # noqa: E402

SAMPLE = os.environ.get("SAMPLE", "estampie")
BPM, LEAD_IN = 150, 1
FORM = ["F", "Db", "Bb", "Eb", "F", "Bb", "Bb", "Eb"]
SPAN = 8 if SAMPLE == "estampie" else 7
BEATS_PER_BAR, BARS = SPAN, len(FORM)
HALF = 4
ACCORDION, ENGLISH_HORN, FIDDLE, BASSOON_P = 21, 69, 110, 70
LOW_FLOOR_TOM, LOW_TOM = 41, 45

# root (bass), fifth, lute chord (low to high)
CH = {"F": ("F2", "C3", ["F3", "A3", "C4", "Eb4"]), "Db": ("Db2", "Ab2", ["Db3", "Ab3", "C4", "F4"]),
      "Bb": ("Bb1", "F2", ["Bb2", "F3", "Bb3", "Db4"]), "Eb": ("Eb2", "Bb2", ["Eb3", "Bb3", "Db4", "Gb4"])}


def line(s):
    return [(float(b), k(n), float(l)) for n, b, l in (x.split() for x in s.split(","))]


TUNES = {
    "estampie": [
        "F4 0 1, Eb4 1 .5, F4 1.5 .5, A4 2 1, F4 3 1, C4 4 1, Eb4 5 .5, F4 5.5 .5, A3 6 2",
        "Ab4 0 1, F4 1 .5, Ab4 1.5 .5, C5 2 2, Bb4 4 .5, Ab4 4.5 .5, F4 5 1, Db4 6 2",
        "C5 0 1.5, Bb4 1.5 .5, Ab4 2 .5, Bb4 2.5 .5, F4 3 1, Db4 4 1, F4 5 1, Bb4 6 2",
        "Gb4 0 1, F4 1 .5, Eb4 1.5 .5, Db4 2 1, Eb4 3 1, Bb3 4 1, Db4 5 .5, Eb4 5.5 .5, F4 6 1, A3 7 1",
        "F4 0 .5, G4 .5 .5, A4 1 1, C5 2 1, A4 3 1, F4 4 2, Eb4 6 1, C4 7 1",
        "Db4 0 1, F4 1 1, Bb4 2 2, Ab4 4 .5, Bb4 4.5 .5, C5 5 1, Bb4 6 2",
        "Db5 0 1, C5 1 .5, Bb4 1.5 .5, Ab4 2 1, F4 3 1, Db4 4 1, C4 5 .5, Db4 5.5 .5, Bb3 6 2",
        "Eb4 0 1, Gb4 1 1, Bb4 2 1, Ab4 3 .5, Gb4 3.5 .5, F4 4 1, Eb4 5 1, Db4 6 .5, C4 6.5 .5, A3 7 1",
    ],
    "dance7": [
        "F4 0 1, A4 1 1, C5 2 1, A4 3 1, F4 4 1.5, Eb4 5.5 .5, C4 6 1",
        "Db4 0 .5, F4 .5 .5, Ab4 1 1, C5 2 1, Bb4 3 1, Ab4 4 3",
        "C5 0 1, Bb4 1 .5, Ab4 1.5 .5, Bb4 2 1, F4 3 1, Db4 4 1.5, F4 5.5 .5, Bb4 6 1",
        "Gb4 0 1, F4 1 1, Eb4 2 .5, Db4 2.5 .5, Eb4 3 1, Bb3 4 2, A3 6 1",
        "C4 0 .5, F4 .5 .5, A4 1 1, F4 2 .5, A4 2.5 .5, C5 3 1, A4 4 1.5, G4 5.5 .5, F4 6 1",
        "Bb4 0 2, Ab4 2 .5, Bb4 2.5 .5, C5 3 1, Db5 4 2, C5 6 1",
        "Bb4 0 1, F4 1 1, Db4 2 .5, F4 2.5 .5, Bb4 3 1, Ab4 4 1.5, F4 5.5 .5, Db4 6 1",
        "Eb4 0 .5, F4 .5 .5, Gb4 1 1, Bb4 2 1, Ab4 3 .5, Gb4 3.5 .5, F4 4 1, Eb4 5 1, A3 6 1",
    ],
}
TUNE = [line(s) for s in TUNES[SAMPLE]]
# accents: DUM (low frame drum + stomp) and tek (rim) per span
if SAMPLE == "estampie":
    DUMS = [0, 2, 2.5, 4, 6, 6.5]
    TEKS = [1, 1.5, 3, 5, 5.5, 7]
    CLAPS = [1, 3, 5, 7]
    PLUCK = [0, .5, 1, 1.5, 2, 2.5, 3, 3.5] * 2
else:  # 2 + 2 + 3
    DUMS = [0, 2, 4]
    TEKS = [1, 1.5, 3, 3.5, 5, 6, 6.5]
    CLAPS = [1, 3, 5, 6]
    PLUCK = [0, .5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5]


def at(c, beat):
    return 0, LEAD_IN + c * SPAN + beat


def tune(first, last, shift=0, vel=96):
    return [note(*at(c, b), key + shift, l - .08, vel) for c in range(first, last) for b, key, l in TUNE[c]]


def lute():  # picked eighths: root, fifth, octave, chord tones; accent on the dance's long beats
    out = []
    for c in range(BARS):
        root, fifth, chord = k(CH[FORM[c]][0]) + 12, k(CH[FORM[c]][1]) + 12, [k(n) for n in CH[FORM[c]][2]]
        seq = [root, chord[1], fifth, chord[2], root + 12, chord[3], fifth, chord[2]]
        for i, b in enumerate(PLUCK[:SPAN * 2] if SAMPLE == "estampie" else PLUCK):
            b = b + (4 if SAMPLE == "estampie" and i >= 8 else 0)
            out.append(note(*at(c, b), seq[i % len(seq)], .45, 92 if b in DUMS else 66))
    return out


def harp():  # chord on each DUM
    return [note(*at(c, b), k(n), 1, 70) for c in range(BARS) for b in DUMS[::2] for n in CH[FORM[c]][2]]


def drone():  # hurdy-gurdy: root + fifth held, re-bowed each chord
    return [note(*at(c, 0), k(n), SPAN - .1, 70) for c in range(BARS) for n in CH[FORM[c]][:2]]


def bassoon():
    return [note(*at(c, b), k(CH[FORM[c]][0]) - (12 if b else 0), 1, 90) for c in range(BARS) for b in DUMS[:2]]


def drums():
    out = []
    for c in range(BARS):
        out += [note(*at(c, b), LOW_FLOOR_TOM, .3, 100 if b == 0 else 86) for b in DUMS]
        out += [note(*at(c, b), KICK, .3, 104) for b in DUMS[::2]]  # stomps
        out += [note(*at(c, b), STICK, .2, 66) for b in TEKS]
    return out


def claps():
    return [note(*at(c, b), CLAP, .2, 70) for c in range(HALF, BARS) for b in CLAPS]


TRACKS = [
    ("Lute", (NYLON_GUITAR, 0), lute),
    ("Harp", (HARP, 0), harp),
    ("Drone", (ACCORDION, 0), drone),
    ("Bassoon", (BASSOON_P, 0), bassoon),
    ("Reed", (ENGLISH_HORN, 0), lambda: tune(0, BARS)),
    ("Fiddle", (FIDDLE, 0), lambda: tune(HALF, BARS, 0, 80)),
    ("Drums", (STANDARD_KIT, 128), drums),
    ("Claps", (STANDARD_KIT, 128), claps),
]
MIX = {"Lute": (0.9, 0, 0, 0, 0), "Harp": (0.5, 0, 0, 0, 0), "Drone": (0.35, 6, 5, 4, 0.3), "Bassoon": (0.7, 0, 0, 0, 0),
       "Reed": (0.7, 0, 0, 0, 0), "Fiddle": (0.55, 10, 5.5, 0, 0), "Drums": (0.8, 0, 0, 0, 0), "Claps": (0.4, 0, 0, 0, 0)}
LOWPASS = {"Lute": 3000, "Harp": 3000, "Drone": 1600, "Reed": 2000, "Fiddle": 1800, "Drums": 1800, "Claps": 1500}
