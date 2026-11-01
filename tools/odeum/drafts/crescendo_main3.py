"""Crescendo main v3: v2's tune and form (crescendo_main2.py) with more energy and a real build.

Added over v2:
  orchestra kit       concert snare ostinato (punchier than brushes) + bass drum on the 3+4 downbeats
  pizz ostinato       mid-register chord 8ths: the engine
  strings, horns      sustained body; horns join in B, the build and A3
  timpani             roots in A3, a growing roll in the build
  C build             layers enter bar by bar, rhythm speeds up (4ths -> 8ths -> 16ths), everything
                      rises in volume, a harp sweep and a big downbeat land on A3
Every section has a loudness scale; A3 is the loudest, the intro the softest.
Render: python reference_render.py OUT.mp3 crescendo_main3
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403
import crescendo_main2 as v2  # noqa: E402
from crescendo_main2 import FORM, SEC, BARS, first_bar, at, play, k  # noqa: E402
from crescendo_bolero import HARP, SNARE_STEPS, ACCENT, PIZZ, HARP_P, BASSOON, CLARINET  # noqa: E402

BPM, BEATS_PER_BAR, LEAD_IN = 150, 7, 1
STRINGS, HORN, TIMPANI, ORCH_KIT = 48, 60, 47, 48
CONCERT_BD = 36
SCALE = {"intro": .8, "A1": .92, "A2": .97, "B": .95, "C": 1.0, "A3": 1.2}
ROOT = {"F": "F2", "Db": "Db3", "Bb": "Bb2", "Eb": "Eb3", "Gb": "Gb2", "Ab": "Ab2", "Cb": "B2", "CbI": "B2",
        "Fw": "F2", "Fm": "F2", "Dl": "Db3", "Fl": "F2", "-": "Bb2"}
C0 = first_bar("C")


def build_ramp(bar, frac=0.0):
    """0..1 position through the C build (bar + fraction of the bar)."""
    return min(1.0, max(0.0, (bar - C0 + frac) / 6))


def vel_of(bar, v):
    sec, _ = SEC[bar]
    if sec == "C":
        return max(1, min(127, int(v * (0.6 + 0.48 * build_ramp(bar)))))
    return max(1, min(127, int(v * SCALE[sec])))


def scaled(notes):
    """Apply section loudness to notes made by v2 (ticks -> bar)."""
    out = []
    for p, key, l, v in notes:
        bar = min(BARS - 1, max(0, int((p / BEAT - LEAD_IN) // BEATS_PER_BAR)))
        out.append((p, key, l, vel_of(bar, v)))
    return out


def clarinet():
    return scaled(v2.clarinet())


def bassoon():
    return scaled(v2.bassoon())


def harp():
    out = scaled(v2.harp())
    last = C0 + 5  # sweep up the Bb minor scale over the last two beats of the build
    scale = ["Bb2", "C3", "Db3", "Eb3", "F3", "Gb3", "Ab3", "Bb3", "C4", "Db4", "Eb4", "F4", "Gb4", "Ab4", "Bb4", "C5"]
    out += [note(*at(last, 5 + i / 8), k(n), .5, 70 + i * 3) for i, n in enumerate(scale)]
    return out


def pizz():
    return scaled(v2.pizz())


def ostinato():  # pizzicato chords in 8ths, accents on the 3+4 downbeats
    out = []
    for bar, (r, (sec, i)) in enumerate(zip(FORM, SEC)):
        if r == "-" or (sec == "intro" and i < 2):
            continue
        tones = [k(n) for n in HARP[r]][1:]  # upper three
        if sec == "C":  # the build speeds up: quarters, quarters, 8ths, 8ths, 16ths, 16ths
            step = (1, 1, .5, .5, .25, .25)[i]
        elif sec in ("intro", "B"):
            step = 1
        else:
            step = .5
        n_hits = int(BEATS_PER_BAR / step)
        for h in range(n_hits):
            beat = h * step
            acc = 100 if beat in (0, 3) else 78
            v = vel_of(bar, acc) if sec != "C" else max(1, min(127, int(acc * (0.55 + 0.48 * build_ramp(bar, beat / 7)))))
            out += [note(*at(bar, beat), t, min(step, .5) * .8, v) for t in tones]
    return out


def strings():  # sustained body: B, the build, A3
    out = []
    for bar, (r, (sec, i)) in enumerate(zip(FORM, SEC)):
        if sec in ("B", "A3") or (sec == "C" and i >= 1):
            v = vel_of(bar, 80)
            out += [note(*at(bar, 0), k(n), BEATS_PER_BAR - .1, v) for n in HARP[r][1:]]  # mid register: no edge
    return out


def horns():  # B: two-note pads; build: rising held notes; A3: the tune an octave down
    out = []
    for bar, (r, (sec, i)) in enumerate(zip(FORM, SEC)):
        tones = [k(n) for n in HARP[r]]
        if sec == "B":
            out += [note(*at(bar, 0), t, BEATS_PER_BAR - .1, vel_of(bar, 72)) for t in tones[1:3]]
        elif sec == "C" and i >= 2:
            out += [note(*at(bar, 0), t, BEATS_PER_BAR - .1, vel_of(bar, 90)) for t in tones[1:3]]
    out += scaled(play(first_bar("A3"), v2.TUNE, 88, shift=-12))
    return out


def timpani():
    out = []
    for bar, (r, (sec, i)) in enumerate(zip(FORM, SEC)):
        root = k(ROOT[r])
        if sec == "A3":
            out += [note(*at(bar, b), root, 1, vel_of(bar, v)) for b, v in ((0, 105), (3, 85))]
        elif sec == "C" and i >= 2:  # roll: 16ths on the root, growing to the end of the build
            for s in range(28):
                out.append(note(*at(bar, s / 4), root, .25, int(35 + 85 * build_ramp(bar, s / 28))))
    a3 = first_bar("A3")
    out.append(note(*at(a3, 0), k("F2"), 2, 127))  # the landing
    return out


def drums():
    out = []
    for bar, (r, (sec, i)) in enumerate(zip(FORM, SEC)):
        if r == "-":
            continue
        for j, st in enumerate(SNARE_STEPS):
            base = 92 if st in ACCENT else 66
            if sec == "C":
                v = int(base * (0.45 + 0.6 * build_ramp(bar, st / 28)))
            elif sec == "intro":
                v = int(base * (0.45 + 0.15 * i))
            else:
                v = vel_of(bar, base)
            out.append(note(*at(bar, st / 4), SNARE, .25, min(127, v)))
        if sec == "C" and i >= 4:  # snare 16ths in the last two bars of the build
            out += [note(*at(bar, s / 4), SNARE, .25, int(45 + 55 * build_ramp(bar, s / 28))) for s in range(28)
                    if s not in SNARE_STEPS]
        if sec in ("A1", "A2", "A3", "B"):
            beats = (0, 3, 5) if sec == "A3" else (0, 3)
            out += [note(*at(bar, b), CONCERT_BD, .5, vel_of(bar, 110)) for b in beats]
        elif sec == "C" and i >= 3:  # bass drum on every beat as the build peaks
            out += [note(*at(bar, b), CONCERT_BD, .5, int(70 + 50 * build_ramp(bar, b / 7))) for b in range(7)]
    a3 = first_bar("A3")
    out.append(note(*at(a3, 0), CONCERT_BD, 1, 127))
    return out


TRACKS = [
    ("Pizz", (PIZZ, 0), pizz),
    ("Ostinato", (PIZZ, 0), ostinato),
    ("Harp", (HARP_P, 0), harp),
    ("Strings", (STRINGS, 0), strings),
    ("Horns", (HORN, 0), horns),
    ("Bassoon", (BASSOON, 0), bassoon),
    ("Clarinet", (CLARINET, 0), clarinet),
    ("Timpani", (TIMPANI, 0), timpani),
    ("Drums", (ORCH_KIT, 128), drums),
]
MIX = {"Pizz": (1.6, 0, 0, 0, 0), "Ostinato": (0.7, 0, 0, 0, 0), "Harp": (0.65, 0, 0, 0, 0),
       "Strings": (0.7, 0, 0, 0, 0), "Horns": (0.45, 0, 0, 0, 0), "Bassoon": (0.45, 0, 0, 0, 0),
       "Clarinet": (0.8, 0, 0, 0, 0), "Timpani": (0.9, 0, 0, 0, 0), "Drums": (0.9, 0, 0, 0, 0)}
LOWPASS = {"Clarinet": 2000, "Harp": 5000, "Ostinato": 4000, "Strings": 2500, "Horns": 3000, "Bassoon": 3000,
           "Drums": 6000}
