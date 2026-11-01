"""Crescendo: the Balatro theme as a Bolero-style orchestral build (7/4, 150 BPM).

The build happens across versions: main is a small ensemble, boss the full orchestra; each version
stays steady so the loop is seamless. This file is the MAIN version (small ensemble):
  snare ostinato (soft)      a Bolero-like rhythm fitted to the original's 3+4 accents
  pizzicato strings          the Balatro bass riff
  harp                       chord on the 3+4 downbeats
  bassoon                    held guide tones, low, under the tune
  clarinet                   the Balatro lead notes, an octave down (no piercing highs)
Form, riffs and lead notes come from crescendo_main.py (taken from the original, music/ORIGINAL.md).
BOLERO_BARS="9-16" renders only those bars (1-based, inclusive) for a short sketch.
Render: python reference_render.py OUT.mp3 crescendo_bolero
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403
from crescendo_main import FORM, RIFF, LEAD_NOTES, k  # noqa: E402

BPM, BEATS_PER_BAR = 150, 7
LEAD_IN = 1
_first, _last = (int(x) for x in os.environ.get("BOLERO_BARS", "1-62").split("-"))
FIRST, BARS = _first - 1, _last - _first + 1  # 0-based first bar, bar count
PIZZ, HARP_P, BASSOON, CLARINET = 45, 46, 70, 71

# Snare ostinato, 16th steps in a 28-step bar: "dum da-da" cells, grouped 3 + 4 like the original's accents
SNARE_STEPS = [0, 2, 3, 4, 6, 7, 8, 10, 12, 14, 15, 16, 18, 19, 20, 22, 24, 26]
ACCENT = {0, 12}
# Held guide tone per riff (bassoon), voice-led around F3-Ab3
GUIDE = {"F": "A3", "Db": "Ab3", "Bb": "F3", "Eb": "Gb3", "Gb": "Bb3", "Ab": "C4", "Cb": "Eb3", "CbI": "Eb3",
         "Fm": "Ab3", "Fw": "Ab3", "Dl": "F3", "Fl": "Ab3", "-": "F3"}
# Harp chord per riff (3 notes, middle register)
HARP = {"F": ["F3", "C4", "Eb4", "A4"], "Db": ["Db3", "Ab3", "C4", "F4"], "Bb": ["Bb2", "F3", "Db4", "F4"],
        "Eb": ["Eb3", "Bb3", "Db4", "Gb4"], "Gb": ["Gb3", "Db4", "F4", "Bb4"], "Ab": ["Ab3", "Eb4", "C4", "Ab4"],
        "Cb": ["B2", "Gb3", "Eb4", "Gb4"], "CbI": ["B2", "Gb3", "Eb4", "Gb4"], "Fm": ["F3", "C4", "F4", "Ab4"],
        "Fw": ["F3", "C4", "F4", "Ab4"], "Dl": ["Db3", "Ab3", "Db4", "F4"], "Fl": ["F3", "C4", "F4", "Ab4"],
        "-": ["Bb2", "F3", "Db4", "F4"]}  # root included, so the chords read clearly


def bars():
    return range(FIRST, FIRST + BARS)


def at(bar, beat):  # bar 0-based in the full form; output starts at FIRST
    return 0, LEAD_IN + (bar - FIRST) * BEATS_PER_BAR + beat


def pizz():
    # notes below E1 (the C-section low riffs) go up an octave: plucked strings get rumbly down there
    return [note(*at(bar, b), key + (12 if key < k("E1") else 0), min(l, 1), 120)
            for bar in bars() for b, key, l in RIFF[FORM[bar]]]


def harp():
    out = []
    for bar in bars():
        if FORM[bar] == "-":  # bar 1 (no bass, no drums in the original): a slow rolled Bbm7
            out += [note(*at(bar, i * .5), k(n), 7 - i * .5, 62) for i, n in enumerate(["Bb2", "F3", "Bb3", "Db4", "F4", "Ab4"])]
        else:
            out += [note(*at(bar, b), k(n), 2.5, 70) for b in (0, 3) for n in HARP[FORM[bar]]]
    return out


ROOT = {"F": "F2", "Db": "Db2", "Bb": "Bb1", "Eb": "Eb2", "Gb": "Gb2", "Ab": "Ab1", "Cb": "B1", "CbI": "B1",
        "Fm": "F2", "Fw": "F2", "Dl": "Db2", "Fl": "F2", "-": "Bb1"}


def bassoon():  # holds each chord's root low, under the plucked riff (the original's bass sustains)
    return [note(*at(bar, 0), k(ROOT[FORM[bar]]) + (12 if k(ROOT[FORM[bar]]) < k("Db2") else 0), BEATS_PER_BAR - .25, 72)
            for bar in bars()]


def clarinet():  # Balatro lead notes an octave down (warm low register); long ones re-tongued each bar
    out = []
    lo, hi = FIRST * BEATS_PER_BAR, (FIRST + BARS) * BEATS_PER_BAR
    for bar1, beat, name, length in LEAD_NOTES:
        start = (bar1 - 1) * BEATS_PER_BAR + beat
        end = start + length
        t, first = start, True
        while t < end - 0.01:
            nxt = min(end, (int(t // BEATS_PER_BAR) + 1) * BEATS_PER_BAR)
            if lo <= t < hi:
                out.append(note(0, LEAD_IN + t - lo, k(name) - 12, min(nxt, hi) - t - .1, 88 if first else 76))
            t, first = nxt, False
    return out


def snare():  # never stops (Bolero); a touch lighter in the C-section breakdown, rising again in bar 46
    out = []
    for bar in bars():
        if FORM[bar] == "-":
            continue
        drop = -10 if 38 <= bar + 1 <= 45 else 0
        for i, st in enumerate(SNARE_STEPS):
            vel = (62 if st in ACCENT else 44) + drop
            if bar + 1 == 46:
                vel = 36 + i * 2
            out.append(note(*at(bar, st / 4), SNARE, .25, vel))
    return out


TRACKS = [
    ("Pizz", (PIZZ, 0), pizz),
    ("Harp", (HARP_P, 0), harp),
    ("Bassoon", (BASSOON, 0), bassoon),
    ("Clarinet", (CLARINET, 0), clarinet),
    ("Snare", (BRUSH_KIT, 128), snare),
]
MIX = {"Pizz": (1.8, 0, 0, 0, 0), "Harp": (0.9, 0, 0, 0, 0), "Bassoon": (0.25, 0, 0, 0, 0),
       "Clarinet": (0.8, 0, 0, 0, 0), "Snare": (0.6, 0, 0, 0, 0)}
# Tone filters (Hz): keep 2-4 kHz at or below the original Balatro track
LOWPASS = {"Clarinet": 2200, "Harp": 3500, "Snare": 4500}
