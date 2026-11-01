"""Crescendo main v2: Bolero-style small ensemble, new tune ("free" sample), tighter 42-bar form (~1:58).

Form (bars): intro 1-4 | A1 5-12 | A2 13-20 | B 21-28 | C 29-34 (build) | A3 35-42 -> back to bar 1.
Chords and bass riffs come from the original Balatro theme; the tune is new (Locked picked it over the
close-to-original one). Every note sits on the 8th grid, phrased 3+4 like the original's accents.
Render: python reference_render.py OUT.mp3 crescendo_main2
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403
from crescendo_main import RIFF, k  # noqa: E402
from crescendo_bolero import HARP, SNARE_STEPS, ACCENT, PIZZ, HARP_P, BASSOON, CLARINET  # noqa: E402
from crescendo_samples import MELODY, COUNTER  # noqa: E402

BPM, BEATS_PER_BAR = 150, 7
LEAD_IN = 1
A = ["F", "Db", "Bb", "Eb"] * 2
SECTIONS = [  # (name, riffs)
    ("intro", ["-", "CbI", "Bb", "Eb"]),
    ("A1", A),
    ("A2", A),
    ("B", ["Gb", "Gb", "Ab", "Ab", "Gb", "Gb", "Cb", "Fw"]),
    ("C", ["Ab", "Fm", "Dl", "Fl", "Dl", "Fl"]),
    ("A3", A),
]
FORM, SEC = [], []
for name, riffs in SECTIONS:
    FORM += riffs
    SEC += [(name, i) for i in range(len(riffs))]
BARS = len(FORM)
TUNE = MELODY["free"]
ANCHORS = ["F4 7", "F4 7", "C4 7", "Bb3 6.5, Db4 .5"]  # Balatro's own melody notes, an octave down

B_TUNE = [
    "Db5 2, Bb4 1, F5 3, Eb5 1",
    "Db5 3, Bb4 1, Db5 1, F4 2",
    "C5 2, Eb5 1, Ab4 3, Bb4 1",
    "C5 3, Eb5 2, C5 1, Bb4 1",
    "Db5 2, F5 1, Eb5 2, Db5 1, Bb4 1",
    "F5 3, Db5 1, Bb4 1, Db5 2",
    "Eb5 2, Db5 1, B4 3, Db5 1",
    "C5 2, Ab4 1, F4 3, - 1",
]
C_CLARINET = [
    "- 3, Ab4 .5, C5 .5, Eb5 1, C5 2",
    "- 3, F4 .5, Ab4 .5, C5 1, Ab4 2",
    "- 3, Ab4 .5, Db5 .5, F5 1, Eb5 1, Db5 1",
    "Ab4 .5, C5 .5, F5 2, Eb5 1, C5 1, Ab4 1, C5 1",
    "Ab4 .5, Db5 .5, F5 2, Eb5 .5, Db5 .5, C5 1, Db5 1, Eb5 1",
    "C5 1, Eb5 1, F5 1, Eb5 1, C5 1, A4 1, C5 1",
]
C_BASSOON = [
    "Ab2 .5, C3 .5, Eb3 1, C3 1, - 4",
    "F2 .5, Ab2 .5, C3 1, Ab2 1, - 4",
    "Db3 .5, F3 .5, Ab3 1, F3 1, Db3 4",
    "F2 3, C3 2, F3 2",
    "Db3 3, Ab2 2, Db3 2",
    "F2 3, A2 2, C3 2",
]
INTRO_BASSOON = ["- 7", "B2 3, Eb3 2, Gb3 2", "Bb2 3, Db3 2, F3 2", "Eb3 3, Db3 2, C3 2"]
# Snare level per section (velocity offset), and crescendos
SNARE_OFFSET = {"intro": -8, "A1": 0, "A2": 0, "B": -6, "C": 0, "A3": 6}


def first_bar(section):
    return next(i for i, (n, j) in enumerate(SEC) if n == section and j == 0)


def at(bar, beat):
    return 0, LEAD_IN + bar * BEATS_PER_BAR + beat


def play(start_bar, bars, vel, shift=0, length_scale=1.0):
    out = []
    for i, s in enumerate(bars):
        beat = 0
        for item in s.split(","):
            n, l = item.split()
            l = float(l)
            if n != "-":
                out.append(note(*at(start_bar + i, beat), k(n) + shift, l * length_scale - .08, vel))
            beat += l
        assert abs(beat - BEATS_PER_BAR) < 1e-6, (start_bar + i, s, beat)
    return out


def clarinet():
    return (play(first_bar("A1"), TUNE, 90)
            + play(first_bar("A2"), ANCHORS * 2, 70)  # Balatro's notes under the harp's tune
            + play(first_bar("B"), B_TUNE, 88)
            + play(first_bar("C"), C_CLARINET, 84)
            + play(first_bar("A3"), TUNE, 96))


def bassoon():
    return (play(first_bar("intro"), INTRO_BASSOON, 70)
            + play(first_bar("A1"), COUNTER, 74)
            + play(first_bar("A2"), COUNTER, 70)
            + play(first_bar("B"), ["Gb2 7", "Db3 7", "Ab2 7", "Eb3 7", "Gb2 7", "Bb2 7", "B2 7", "F2 7"], 64)
            + play(first_bar("C"), C_BASSOON, 80)
            + play(first_bar("A3"), COUNTER, 80))


def harp():
    out = []
    for bar, (r, (sec, i)) in enumerate(zip(FORM, SEC)):
        if r == "-":  # bar 1: slow rolled Bbm7
            out += [note(*at(bar, j * .5), k(n), 7 - j * .5, 62) for j, n in enumerate(["Bb2", "F3", "Bb3", "Db4", "F4", "Ab4"])]
        elif sec == "B":  # rippling 8ths through the chord
            tones = [k(n) for n in HARP[r]]
            cycle = tones + tones[::-1][1:-1]  # up and back down
            out += [note(*at(bar, e / 2), cycle[e % len(cycle)], .9, 58) for e in range(14)]
        elif sec == "C":
            out += [note(*at(bar, 0), k(n), 6, 64 + i * 4) for n in HARP[r]]
        elif sec != "A2":
            out += [note(*at(bar, b), k(n), 2.5, 66) for b in (0, 3) for n in HARP[r]]
    out += play(first_bar("A2"), TUNE, 92)  # the hand-off: harp takes the tune
    out += play(first_bar("A3"), TUNE, 70, shift=-12)  # and doubles it an octave down at the end
    return out


def pizz():
    return [note(*at(bar, b), key + (12 if key < k("E1") else 0), min(l, 1), 120)
            for bar, r in enumerate(FORM) for b, key, l in RIFF[r]]


def snare():
    out = []
    for bar, (r, (sec, i)) in enumerate(zip(FORM, SEC)):
        if r == "-":
            continue
        for j, st in enumerate(SNARE_STEPS):
            vel = (62 if st in ACCENT else 44) + SNARE_OFFSET[sec]
            if sec == "intro":  # come in from nothing over bars 2-4
                vel = int(vel * (0.55 + 0.15 * i + 0.1 * j / len(SNARE_STEPS)))
            if sec == "C":  # the build: whisper to full over six bars
                vel = int(28 + (i * len(SNARE_STEPS) + j) * 50 / (6 * len(SNARE_STEPS)))
            out.append(note(*at(bar, st / 4), SNARE, .25, vel))
    return out


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
