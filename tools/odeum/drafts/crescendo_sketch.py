"""Crescendo sketch: the Balatro theme's A section as modern garage rock (main variant, holding back).

Two cycles of the A loop (F7, Dbmaj7/Bbm, Bbm, Ebm7), same notes as the original (music/ORIGINAL.md).
METER env var: "7" keeps the original 7/4; "4" stretches each 7-beat bar to 8 beats (two 4/4 bars)
by holding the riff's long root note one beat longer, so the riff and lead stay intact.
Render: CRESCENDO_METER=7 python reference_render.py OUT.mp3 crescendo_sketch
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403

METER = int(os.environ.get("CRESCENDO_METER", "7"))
BPM, CYCLES = 150, 2
BEATS_PER_BAR = 7 if METER == 7 else 8  # "bar" = one chord span
BARS = 4 * CYCLES
LEAD_IN = 1
DIST_GUITAR, OD_GUITAR, PICK_BASS, POWER_KIT = 30, 29, 34, 16

F1, Bb1, C2, Db2, Eb2, F2, Ab2, A2, Bb2, C3, Db3 = 29, 34, 36, 37, 39, 41, 44, 45, 46, 48, 49
Bb4, C5, Db5, F5 = 70, 72, 73, 77

# Bass riffs from the original, (beat, key, length) in 7/4; the first long note is the one stretched for 4/4
RIFF = {
    "F": [(0, Eb2, 1.25), (1.5, F1, 3), (4.5, F2, .5), (5, A2, .5), (5.5, Eb2, .5), (6, C2, .5), (6.5, F2, .5)],
    "Db": [(0, Db2, 3.25), (3.5, Bb1, .75), (5, Eb2, 1), (6.5, Bb2, .5)],
    "Bb": [(0, Bb1, 4.5), (4.5, Bb2, .5), (5, Db3, .5), (5.5, Ab2, .5), (6, Eb2, .5), (6.5, F2, .5)],
    "Eb": [(0, Eb2, 1.25), (1.5, Bb1, 1.75), (3.5, Eb2, 1), (4.5, Db3, .5), (5, C3, .5), (5.5, Bb2, .5),
           (6, F2, .5), (6.5, Ab2, .5)],
}
STRETCH_AT = {"F": 1.5, "Db": 0, "Bb": 0, "Eb": 1.5}  # 4/4: notes after this start one beat later
FORM = [["F", "Db", "Bb", "Eb"], ["F", "Bb", "Bb", "Eb"]]  # 2nd cycle: the original's Bbm variation
POWER = {"F": [41, 48, 53], "Db": [37, 44, 49], "Bb": [46, 53, 58], "Eb": [39, 46, 51]}  # drop-tuned root-5-8
LEAD = [[(0, F5, 14)], [], [(0, C5, 7)], [(.5, Bb4, 6), (6.5, Db5, .5)]]  # per bar of the cycle (7/4 beats)


def stretch(beat, length, at):
    """Map a 7/4 beat to the 8-beat bar: everything after `at` moves one beat later; the note at `at` grows."""
    if METER == 7:
        return beat, length
    if beat > at:
        return beat + 1, length
    if beat == at:
        return beat, length + 1
    return beat, length


def at(bar, beat):
    return 0, LEAD_IN + bar * BEATS_PER_BAR + beat


def chord_of(bar):
    return FORM[bar // 4][bar % 4]


def bass():
    out = []
    for bar in range(BARS):
        c = chord_of(bar)
        for b, k, l in RIFF[c]:
            b, l = stretch(b, l, STRETCH_AT[c])
            out.append(note(*at(bar, b), k, l, 110))
    return out


def guitar():  # palm-muted 8th-note power-chord chugs, accented with the kick
    out = []
    for bar in range(BARS):
        for e in range(BEATS_PER_BAR * 2):
            beat = e / 2
            vel = 100 if beat in KICKS else 72
            out += [note(*at(bar, beat), k, .4, vel) for k in POWER[chord_of(bar)]]
    return out


def lead():
    out = []
    for bar in range(BARS):
        for b, k, l in LEAD[bar % 4]:
            if METER == 4:
                b, l = (b + 1, l) if b > 6 else (b, l + (2 if l > 8 else 1))
            out.append(note(*at(bar, b), k, l, 92))
    return out


if METER == 7:  # the original's 3+4 accents, filled out for drive
    KICKS, SNARES = (0, 1.5, 3, 4.5, 5), (2, 6)
else:           # straight rock beat over two 4/4 bars
    KICKS, SNARES = (0, 1.5, 2, 4, 5.5, 6), (1, 3, 5, 7)


def drums():
    out = []
    for bar in range(BARS):
        out += [note(*at(bar, b), KICK, .5, 112) for b in KICKS]
        out += [note(*at(bar, b), SNARE, .5, 105) for b in SNARES]
        out += [note(*at(bar, h / 2), CLOSED_HH, .25, 80 if h % 2 == 0 else 55) for h in range(BEATS_PER_BAR * 2)]
        if bar % 4 == 0:
            out.append(note(*at(bar, 0), CRASH, 2, 95))
    return out


def kick_sub():  # standard-kit kick layered under the Power kit for low end
    return [note(*at(bar, b), KICK, .5, 115) for bar in range(BARS) for b in KICKS]


TRACKS = [
    ("Bass", (PICK_BASS, 0), bass),
    ("Sub", (38, 0), bass),  # synth bass doubling the riff underneath, for weight
    ("Kick", (STANDARD_KIT, 128), kick_sub),
    ("Guitar", (DIST_GUITAR, 0), guitar),
    ("Lead", (OD_GUITAR, 0), lead),
    ("Drums", (POWER_KIT, 128), drums),
]
# gain, then wobble (none: this is a live band)
MIX = {"Bass": (1.0, 0, 0, 0, 0), "Sub": (1.5, 0, 0, 0, 0), "Kick": (1.4, 0, 0, 0, 0), "Guitar": (0.4, 0, 0, 0, 0), "Lead": (0.55, 0, 0, 0, 0), "Drums": (0.85, 0, 0, 0, 0)}
