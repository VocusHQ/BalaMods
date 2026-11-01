"""Crescendo: the shop, packs, planet and boss versions (VERSION env). Blinds/main = crescendo_garage.py.

Each version holds its place's mood for the whole loop and is built on what Balatro's own version for that
place does (measured from the game's music2-5 with Demucs, see music/ORIGINAL.md), in Crescendo's style.
All share main's 42-bar form, tune and chords, so the game can crossfade between them in sync.

  shop    original: lighter beat (snare on 3 only), steady hats, brightest; plucked layer in B
          ours: light bouncy drummer, pizzicato + harp up front, harp plucks the B tune, gentle C
  packs   original: busier percussion, darker synths; plucked layer in C
          ours: soft busy percussion (rims, toms), harp ripples, low clarinet, pizz plucks the C calls
  planet  original: no drums, heavily muffled, bass + pads loud, soft keys layer
          ours: no drums, bowed bass, slow strings + horn pads, low vibraphone, tune on horn, all soft
  boss    original: louder drums, darker, bass grows; in C the synths drop to drums + bass
          ours: tense all loop: heavy drummer, timpani, low string pulse, horns + trombone tune;
          C strips to drums, bass and timpani, A3 hits hardest
Render: VERSION=boss python reference_render.py OUT.mp3 crescendo_versions
"""
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403
import crescendo_main2 as v2  # noqa: E402
from crescendo_main2 import FORM, SEC, BARS, first_bar, at, play, k, TUNE, B_TUNE, C_CLARINET, C_BASSOON  # noqa: E402
from crescendo_main import RIFF  # noqa: E402
from crescendo_bolero import HARP, PIZZ, HARP_P, BASSOON, CLARINET  # noqa: E402
from crescendo_samples import COUNTER  # noqa: E402
from crescendo_main3 import ROOT  # noqa: E402

VERSION = os.environ.get("VERSION", "shop")
BPM, BEATS_PER_BAR, LEAD_IN = 150, 7, 1
STRINGS, SLOW_STRINGS_P, HORN, TROMBONE, TIMPANI, CONTRABASS, VIBES_P = 48, 49, 60, 57, 47, 43, 11
ROOM_KIT = 8
FLOOR_TOM, LOW_TOM, MID_TOM, HIGH_TOM, SIDE_STICK = 41, 45, 47, 50, 37
KICKS, SNARES = (0, 1.5, 4.5, 5), (2, 6)
rng = random.Random(11)
A_SECS = ("A1", "A2", "A3")


def sec_of(bar):
    return SEC[bar][0]


def bars_in(*secs):
    return [b for b in range(BARS) if sec_of(b) in secs]


def section_lines(lines_by_sec, vel, shift=0, length_scale=1.0):
    """{'A1': [...7-beat bar strings...], ...} -> notes."""
    out = []
    for sec, lines in lines_by_sec.items():
        out += play(first_bar(sec), lines, vel, shift, length_scale)
    return out


def riff(vel=110, octave_up_below="E1"):
    return [note(*at(bar, b), key + (12 if key < k(octave_up_below) else 0), min(l, 1), vel)
            for bar, r in enumerate(FORM) for b, key, l in RIFF[r]]


def chord_hits(beats, vel, length, skip=("-",), secs=None, upper_only=False):
    out = []
    for bar, r in enumerate(FORM):
        if r in skip or (secs and sec_of(bar) not in secs):
            continue
        tones = [k(n) for n in HARP[r]]
        tones = tones[1:] if upper_only else tones
        out += [note(*at(bar, b), t, length, vel) for b in beats for t in tones]
    return out


def ripple(vel, secs=None, step=.5):  # harp up-and-down through the chord
    out = []
    for bar, r in enumerate(FORM):
        if r == "-" or (secs and sec_of(bar) not in secs):
            continue
        tones = [k(n) for n in HARP[r]]
        cyc = tones + tones[::-1][1:-1]
        out += [note(*at(bar, e * step), cyc[e % len(cyc)], step * 1.8, vel) for e in range(int(7 / step))]
    return out


def held_chords(vel, secs=None, shift=0, upper_only=True):
    out = []
    for bar, r in enumerate(FORM):
        if secs and sec_of(bar) not in secs:
            continue
        tones = [k(n) + shift for n in HARP[r]]
        out += [note(*at(bar, 0), t, BEATS_PER_BAR - .1, vel) for t in (tones[1:] if upper_only else tones)]
    return out


def roots(vel, shift=0, step=None, secs=None):
    """Chord roots: held per bar, or repeated every `step` beats (a pulse)."""
    out = []
    for bar, r in enumerate(FORM):
        if secs and sec_of(bar) not in secs:
            continue
        root = k(ROOT[r]) + shift
        if step:
            out += [note(*at(bar, i * step), root, step * .8, vel + (12 if i * step in (0, 3) else 0))
                    for i in range(int(7 / step))]
        else:
            out.append(note(*at(bar, 0), root, BEATS_PER_BAR - .1, vel))
    return out


class Drummer:
    """Live-feel drum helper (Room kit), like the approved main version's drummer."""

    def __init__(self):
        self.out = []

    def hit(self, bar, beat, key, v, length=.25):
        jitter = rng.uniform(-0.02, 0.02) if beat > 0 else 0
        v = int(v + rng.uniform(-6, 6))
        self.out.append(note(*at(bar, max(0, beat + jitter)), key, length, max(1, min(127, v))))

    def fill(self, bar, start, seq, v):
        for j, key in enumerate(seq):
            self.hit(bar, start + j / 4, key, v + j * 2)


SHORT_FILL = [SNARE, SNARE, HIGH_TOM, MID_TOM]
LONG_FILL = [SNARE, SNARE, HIGH_TOM, HIGH_TOM, MID_TOM, MID_TOM, FLOOR_TOM, FLOOR_TOM]
TOM_KEYS = {FLOOR_TOM, LOW_TOM, MID_TOM, HIGH_TOM, SIDE_STICK}


# ---------------------------------------------------------------- shop
def shop_drums():
    d = Drummer()
    for bar, r in enumerate(FORM):
        sec, i = SEC[bar]
        if r == "-":
            continue
        soft = .8 if sec == "intro" else 1
        if sec == "C":  # a gentle swell, not a build
            soft = .8 + .05 * i
        fill = (i % 8 == 7) and sec != "intro"
        cut = 6 if fill else 7
        for b in KICKS:
            if b < cut:
                d.hit(bar, b, KICK, 95 * soft)
        if 2 < cut:
            d.hit(bar, 2, SNARE, 95 * soft)       # snare on 3 only, like the original shop
        if 6 < cut:
            d.hit(bar, 6, SIDE_STICK, 80 * soft)  # a rim click on 7
        for e in range(14):
            if e / 2 < cut:
                d.hit(bar, e / 2, CLOSED_HH, (42 if e % 2 == 0 else 30) * soft)
        if fill:
            d.fill(bar, 6, SHORT_FILL, 85)
    return d.out


def shop_tracks():
    melody = {"A1": TUNE, "A2": TUNE, "A3": TUNE}
    return [
        ("Pizz", (PIZZ, 0), lambda: riff(115)),
        ("Ostinato", (PIZZ, 0), lambda: chord_hits([e / 2 for e in range(14)], 70, .4, upper_only=True,
                                                   secs=("A1", "A2", "A3", "C"))),
        ("Harp", (HARP_P, 0), lambda: chord_hits((0, 3), 66, 2.5, secs=("intro", "A1", "A3", "C"))
         + section_lines({"A2": TUNE, "B": B_TUNE}, 96)),  # harp plucks the tune in A2 and the B melody
        ("Clarinet", (CLARINET, 0), lambda: section_lines(melody, 86) + section_lines({"C": C_CLARINET}, 76)),
        ("Bassoon", (BASSOON, 0), lambda: section_lines({"intro": v2.INTRO_BASSOON, "A1": COUNTER, "A2": COUNTER,
                                                         "A3": COUNTER, "C": C_BASSOON}, 68)),
        ("Strings", (STRINGS, 0), lambda: held_chords(58, secs=("B",))),
        ("Drums", (ROOM_KIT, 128), lambda: [n for n in shop_drums() if n[1] not in TOM_KEYS]),
        ("Toms", (ROOM_KIT, 128), lambda: [n for n in shop_drums() if n[1] in TOM_KEYS]),
    ]


# ---------------------------------------------------------------- packs
def packs_drums():
    d = Drummer()
    for bar, r in enumerate(FORM):
        sec, i = SEC[bar]
        if r == "-":
            continue
        soft = .75 if sec == "intro" else 1
        for b in KICKS + (6,):
            d.hit(bar, b, KICK, 88 * soft)
        for b in (0, 1.5, 4, 4.5):  # the original packs' extra hits, on soft toms
            d.hit(bar, b, LOW_TOM if b in (0, 4) else FLOOR_TOM, 70 * soft)
        for b in SNARES:
            d.hit(bar, b, SNARE, 72 * soft)
        for e in range(14):  # busy, but rim clicks instead of hats
            if e / 2 not in SNARES:
                d.hit(bar, e / 2, SIDE_STICK, (52 if e % 2 == 0 else 38) * soft)
    return d.out


def packs_tracks():
    return [
        ("Pizz", (PIZZ, 0), lambda: riff(108) + section_lines({"C": C_CLARINET}, 100)),  # pizz plucks the C calls
        ("Harp", (HARP_P, 0), lambda: ripple(56) + [note(*at(0, j * .5), k(n), 7 - j * .5, 62)
                                                     for j, n in enumerate(["Bb2", "F3", "Bb3", "Db4", "F4", "Ab4"])]),
        ("Clarinet", (CLARINET, 0), lambda: section_lines({"A1": TUNE, "A2": TUNE, "B": B_TUNE, "A3": TUNE}, 84, shift=-12)),
        ("Bassoon", (BASSOON, 0), lambda: section_lines({"intro": v2.INTRO_BASSOON, "A1": COUNTER, "A2": COUNTER,
                                                         "A3": COUNTER, "C": C_BASSOON}, 66)),
        ("Strings", (STRINGS, 0), lambda: held_chords(52)),
        ("Drums", (ROOM_KIT, 128), lambda: [n for n in packs_drums() if n[1] not in TOM_KEYS]),
        ("Toms", (ROOM_KIT, 128), lambda: [n for n in packs_drums() if n[1] in TOM_KEYS]),
    ]


# ---------------------------------------------------------------- planet
def planet_tracks():
    return [
        ("Bass", (CONTRABASS, 0), lambda: roots(78, shift=-12)),  # bowed, held: the loud soft bass
        ("Pizz", (PIZZ, 0), lambda: riff(70)),
        ("Strings", (SLOW_STRINGS_P, 0), lambda: held_chords(70, upper_only=False)),
        ("HornPad", (HORN, 0), lambda: held_chords(48, secs=("B", "C", "A3"))),
        ("Vibes", (VIBES_P, 0), lambda: chord_hits((0, 3), 58, 3, upper_only=True)),
        ("Horn", (HORN, 0), lambda: section_lines({"A1": TUNE, "A2": TUNE, "B": B_TUNE, "A3": TUNE}, 72,
                                                  shift=-12, length_scale=1.6)),  # tune stretched, legato
        ("Harp", (HARP_P, 0), lambda: ripple(46, step=1)),
    ]


# ---------------------------------------------------------------- boss
def boss_drums():
    """Heartbeat: a double kick (ba-bum) on each half of the 3+4 bar; snare hard on 7 only (like the original
    boss); a ticking rim click instead of hats; floor-tom fills every 4 bars."""
    d = Drummer()
    for bar, r in enumerate(FORM):
        sec, i = SEC[bar]
        for b in (0, .5, 3, 3.5):
            d.hit(bar, b, KICK, 118 if b in (0, 3) else 96)
            d.hit(bar, b, FLOOR_TOM, 100 if b in (0, 3) else 80)
        if r == "-":
            continue
        fill = i % 4 == 3
        if not fill or sec == "intro":
            d.hit(bar, 6, SNARE, 122)
        else:
            d.fill(bar, 5, LONG_FILL, 106)
        if sec == "C":
            d.hit(bar, 2, SNARE, 90)
        for e in range(14):  # the clock
            if e / 2 < (5 if fill and sec != "intro" else 7):
                d.hit(bar, e / 2, SIDE_STICK, 64 if e % 2 == 0 else 46)
    return d.out


def creep():
    """Low strings crawling by semitones (F Gb F E) in 8ths: the sinister engine."""
    cell = [k("F2"), k("Gb2"), k("F2"), k("E2")]
    return [note(*at(bar, e / 2), cell[e % 4], .45, 96 if e % 4 == 0 else 80) for bar in range(BARS) for e in range(14)]


def pedal():
    """A low F held under every chord: it never resolves."""
    return [note(*at(bar, 0), k("F1"), BEATS_PER_BAR - .05, 92) for bar in range(BARS)]


def stabs():
    """Short low brass chords on the off-beats (&2, &5), each with a clashing half-step on top of the root."""
    out = []
    for bar, r in enumerate(FORM):
        if r == "-" or sec_of(bar) == "C":
            continue
        root = k(ROOT[r]) + 12
        out += [note(*at(bar, b), t, .4, 104) for b in (1.5, 4.5) for t in (root, root + 1, root + 7)]
    return out


def choir():
    return held_chords(70, secs=("B", "C"), shift=-12)


def boss_tracks():
    menace = {"A1": TUNE, "A2": TUNE, "B": B_TUNE, "A3": TUNE}
    return [
        ("Pedal", (CONTRABASS, 0), pedal),
        ("Pizz", (PIZZ, 0), lambda: riff(124)),
        ("Creep", (STRINGS, 0), creep),
        ("Horns", (HORN, 0), lambda: section_lines(menace, 100, shift=-12, length_scale=.55)
         + section_lines({"C": C_CLARINET}, 96, shift=-12, length_scale=.55)),
        ("Trombone", (TROMBONE, 0), lambda: section_lines(menace, 94, shift=-24, length_scale=.55)),
        ("Stabs", (TROMBONE, 0), stabs),
        ("Choir", (52, 0), choir),
        ("Timpani", (TIMPANI, 0), lambda: [note(*at(bar, b), k("F2"), .5, 110 if b in (0, 3) else 88)
                                           for bar in range(BARS) for b in (0, .5, 3, 3.5)]),
        ("Drums", (ROOM_KIT, 128), lambda: [n for n in boss_drums() if n[1] not in TOM_KEYS]),
        ("Toms", (ROOM_KIT, 128), lambda: [n for n in boss_drums() if n[1] in TOM_KEYS]),
    ]


TRACKS = {"shop": shop_tracks, "packs": packs_tracks, "planet": planet_tracks, "boss": boss_tracks}[VERSION]()
_GAIN = {
    "shop": {"Pizz": 1.5, "Ostinato": .6, "Harp": .9, "Clarinet": .75, "Bassoon": .4, "Strings": .5, "Drums": .9, "Toms": 1.5},
    "packs": {"Pizz": 1.4, "Harp": .8, "Clarinet": .8, "Bassoon": .45, "Strings": .45, "Drums": 1.4, "Toms": 1.8},
    "planet": {"Bass": .9, "Pizz": .6, "Strings": .7, "HornPad": .4, "Vibes": .5, "Horn": .6, "Harp": .5},
    "boss": {"Pedal": .7, "Pizz": 1.5, "Creep": .8, "Horns": .65, "Trombone": .55, "Stabs": .5, "Choir": .45,
             "Timpani": .9, "Drums": 1.0, "Toms": 1.6},
}[VERSION]
MIX = {name: (g, 0, 0, 0, 0) for name, g in _GAIN.items()}
LOWPASS = {
    "shop": {"Clarinet": 2000, "Harp": 4500, "Ostinato": 4000, "Strings": 2500, "Bassoon": 3000, "Drums": 5000, "Toms": 1200},
    "packs": {"Clarinet": 1500, "Harp": 3000, "Strings": 1500, "Bassoon": 2500, "Pizz": 3000, "Drums": 4000, "Toms": 1500},
    "planet": {"Bass": 1000, "Pizz": 1200, "Strings": 1400, "HornPad": 1200, "Vibes": 1500, "Horn": 1400, "Harp": 1500},
    "boss": {"Pedal": 800, "Creep": 1500, "Horns": 2200, "Trombone": 2000, "Stabs": 2000, "Choir": 1500,
             "Drums": 3500, "Toms": 1200},
}[VERSION]
