"""Crescendo, main version: the full 62-bar Balatro theme as modern garage rock, in the original 7/4.

Form, riffs and lead notes follow the original (music/ORIGINAL.md). Arrangement per section:
  Intro (bar 1)   guitar swell on Bbm, no drums or bass
  2-4             drums enter (bar 2 light), chugs, lead dyad C5+F5 from bar 3
  A (5-22)        riff groove; each pass adds a layer (tambourine, then a ghost clean guitar)
  B (23-36)       half-time beat on the ride, open ringing chords under the long lead notes
  C (37-46)       breakdown: bass, kick and a held F; F5 calls; drum build in 45-46
  A' (47-62)      full groove with every layer, fill in 62 back to the intro
Render: python reference_render.py OUT.mp3 crescendo_main
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403

BPM, BEATS_PER_BAR, BARS = 150, 7, 62
LEAD_IN = 1
DIST_GUITAR, OD_GUITAR, CLEAN_GUITAR, PICK_BASS, SYNTH_BASS, POWER_KIT = 30, 29, 27, 34, 38, 16
TAMBOURINE, LOW_TOM, MID_TOM, HIGH_TOM, RIDE_BELL = 54, 45, 47, 50, 53

# note names -> MIDI keys
_N = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}


def k(name):
    pc, octave = (name[:2], name[2:]) if name[:2] in _N else (name[:1], name[1:])
    return 12 * (int(octave) + 1) + _N[pc]


def riff(s):
    """'Eb2 0 1.25, F1 1.5 3' -> [(beat, key, length)]"""
    return [(float(b), k(n), float(l)) for n, b, l in (x.split() for x in s.split(","))]


# Bass riffs from the original, beats in a 7/4 bar
RIFF = {
    "F": riff("Eb2 0 1.25, F1 1.5 3, F2 4.5 .5, A2 5 .5, Eb2 5.5 .5, C2 6 .5, F2 6.5 .5"),
    "Db": riff("Db2 0 3.25, Bb1 3.5 .75, Eb2 5 1, Bb2 6.5 .5"),
    "Bb": riff("Bb1 0 4.5, Bb2 4.5 .5, Db3 5 .5, Ab2 5.5 .5, Eb2 6 .5, F2 6.5 .5"),
    "Eb": riff("Eb2 0 1.25, Bb1 1.5 1.75, Eb2 3.5 1, Db3 4.5 .5, C3 5 .5, Bb2 5.5 .5, F2 6 .5, Gb2 6.5 .5"),
    "Gb": riff("Gb1 0 4.5, Gb2 4.5 .5, Bb2 5 .5, Db2 5.5 .5, Gb2 6 1"),
    "Ab": riff("Ab1 0 4.5, Ab2 4.5 .5, C3 5 .5, Eb2 5.5 .5, Ab2 6 .5, C2 6.5 .5"),
    "Cb": riff("B1 0 4.25, Gb2 4.5 .5, B2 5 .5, Eb2 5.25 1, B1 6.25 .75"),
    "CbI": riff("B1 0 4.25, F2 4.5 .5, Bb2 5 .5, C3 5.5 .5, Db3 6 .5, F3 6.5 .5"),
    "Fm": riff("F1 0 4.5, Eb2 5.25 1, Ab2 6.5 .5"),
    "Fw": riff("Ab1 0 1.25, Bb1 1.5 1.75, C2 3.5 .75, Ab2 4.5 .5, C3 5.25 .5, F2 5.5 .5, Ab2 6 .5, C2 6.5 .5"),
    "Dl": riff("Db1 0 1, Db1 1.5 1.25, Db1 3.5 1, C3 4.5 .5, Db3 5 .5, Ab2 5.5 .5, Db2 6 .5, Eb2 6.5 .5"),
    "Fl": riff("F1 0 1.25, C1 1.75 1.25, F1 3.25 2.25, Ab1 6 1"),
    "-": [],
}
# Power chord (drop-tuned root, 5th, octave) for each riff
ROOT = {"F": "F2", "Db": "Db2", "Bb": "Bb1", "Eb": "Eb2", "Gb": "Gb2", "Ab": "Ab1", "Cb": "B1", "CbI": "B1",
        "Fm": "F2", "Fw": "F2", "Dl": "Db2", "Fl": "F2", "-": "Bb1"}


def power(r, extra=()):
    root = k(ROOT[r]) + (12 if k(ROOT[r]) < k("Db2") else 0)
    return [root, root + 7, root + 12, *extra]


A1 = ["F", "Db", "Bb", "Eb"] * 2 + ["F", "Bb", "Bb", "Eb"] + ["F", "Db", "Bb", "Eb"]
FORM = (["-", "CbI", "Bb", "Eb"] + A1 + ["F", "Bb"]
        + ["Gb", "Gb", "Ab", "Ab", "Gb", "Gb", "Ab", "Fm", "Cb", "Gb", "Fw", "Fw", "Cb", "Gb"]
        + ["Ab", "Fm"] + ["Dl", "Fl"] * 4
        + ["Bb", "Eb", "F", "Db"] * 3 + ["Bb", "Eb", "F", "Bb"])
assert len(FORM) == BARS


def section(bar):  # bar is 0-based
    b = bar + 1
    if b == 1:
        return "intro"
    if b <= 4:
        return "pre"
    if b <= 22:
        return "A"
    if b <= 36:
        return "B"
    if b <= 46:
        return "C"
    return "A2"


# Lead notes: (bar 1-based, beat, key, beats). Long notes are re-picked each bar, like a held guitar note.
LEAD_NOTES = [(3, 2.5, "C5", 24.5), (3, 2.5, "F5", 24.5)]
for start in (9, 13, 17):  # A cycles 2-4 (cycle 1 carries the intro dyad)
    LEAD_NOTES += [(start, 0, "F5", 14)]
for start in (5, 9, 13, 17):
    LEAD_NOTES += [(start + 2, 0, "C5", 7), (start + 3, .5, "Bb4", 6), (start + 3, 6.5, "Db5", .5)]
LEAD_NOTES += [(21, 1.5, "F5", 3.5), (22, 2.5, "F5", 4.5)]
LEAD_NOTES += [  # B section
    (24, .75, "Db5", 1.5), (24, 3.5, "Bb4", 1.5), (24, 4.75, "Db5", 1.5), (25, 4.5, "Ab5", 2.5),
    (26, 4.25, "F5", 7), (27, 1.5, "Db5", 1.75), (28, 2.75, "Db5", 1.5), (28, 4.5, "Bb4", 1.5),
    (29, 0, "C5", 7), (30, 0, "F5", 3), (30, 3.5, "F5", 15.5), (32, .75, "Ab5", 3), (33, 5.75, "Ab5", 1.25),
    (34, 5.25, "C5", .5), (34, 5.75, "Ab5", 1.25), (35, .25, "Db5", 10.5), (36, 4.5, "Db5", 2.5)]
LEAD_NOTES += [(37, 0, "C5", 7), (38, 2.75, "F4", 59)]  # C section: held F (re-picked)
LEAD_NOTES += [(b, 4.5, "F5", 2.5) for b in range(40, 47)]  # F5 calls
for start in (47, 51, 55):  # A' cycles: Bb, Eb, F, Db
    LEAD_NOTES += [(start + 1, .5, "Bb4", 6), (start + 2, .5, "C5", 5), (start + 3, 6, "F5", 1)]
LEAD_NOTES += [(59, 4.25, "C5", 2.75), (60, .5, "Bb4", 6), (61, .5, "C5", 6)]


def at(bar, beat):  # bar 0-based
    return 0, LEAD_IN + bar * BEATS_PER_BAR + beat


def bass():  # quieter in the breakdown, so the build has room to rise
    return [note(*at(bar, b), key, l, 80 if 38 <= bar + 1 <= 44 else 108)
            for bar, r in enumerate(FORM) for b, key, l in RIFF[r]]


def rhythm_guitar():
    out = []
    for bar, r in enumerate(FORM):
        sec = section(bar)
        if sec == "intro":  # swell: tremolo-picked Bb chord, getting louder
            out += [note(*at(bar, i / 4), key, .25, 15 + i * 2) for i in range(28) for key in power("Bb")]
        elif sec in ("pre", "A", "A2") or (sec == "C" and bar + 1 == 46):
            for e in range(14):
                beat = e / 2
                vel = 100 if beat in KICKS_A else 72
                if sec == "C":  # bar 46: chugs come back in, rising
                    vel = 45 + e * 4
                out += [note(*at(bar, beat), key, .4, vel) for key in power(r)]
        elif sec == "B":  # open, ringing chords on the half-time hits
            for beat, l in ((0, 4.5), (4.5, 2.5)):
                out += [note(*at(bar, beat), key, l, 95 if beat == 0 else 80) for key in power(r)]
        elif sec == "C" and bar + 1 == 37:  # one big ringing hit into the breakdown
            out += [note(*at(bar, 0), key, 7, 105) for key in power(r)]
    return out


def lead():
    out = []
    for bar1, beat, name, length in LEAD_NOTES:
        start = (bar1 - 1) * BEATS_PER_BAR + beat
        end = start + length
        t, first = start, True
        while t < end - 0.01:  # re-pick at each bar line
            nxt = min(end, (int(t // BEATS_PER_BAR) + 1) * BEATS_PER_BAR)
            out.append(note(0, LEAD_IN + t, k(name), nxt - t, 92 if first else 74))
            t, first = nxt, False
    return out


def ghost_guitar():  # clean picked chord tones, from A cycle 3 on and through A'
    # intro: the original's Bbm7 (Bb3 Db4 F4 Ab4) tremolo-picked on clean guitar, swelling under the power chord
    out = [note(*at(0, i / 4), key, .25, 30 + i * 3) for i in range(28) for key in (k("Bb3"), k("Db4"), k("F4"), k("Ab4"))]
    for bar, r in enumerate(FORM):
        if (13 <= bar + 1 <= 22) or section(bar) == "A2":
            tones = power(r, ())
            pattern = [tones[2] + 12, tones[1] + 12, tones[2] + 7 + 12, tones[1] + 12]
            out += [note(*at(bar, e / 2), pattern[e % 4], .45, 60 + (10 if e % 4 == 0 else 0)) for e in range(14)]
    return out


KICKS_A, SNARES_A = (0, 1.5, 3, 4.5, 5), (2, 6)


def drums():
    out = []

    def hit(bar, beat, key, vel, length=.5):
        out.append(note(*at(bar, beat), key, length, vel))

    for bar, r in enumerate(FORM):
        sec, b1 = section(bar), bar + 1
        if sec == "intro":
            continue
        if sec in ("pre", "A", "A2"):
            light = b1 == 2
            for b in (KICKS_A if not light else (0, 4.5)):
                hit(bar, b, KICK, 112)
            if not light:
                for b in SNARES_A:
                    hit(bar, b, SNARE, 105)
            for h in range(14):
                hit(bar, h / 2, CLOSED_HH, 80 if h % 2 == 0 else 55, .25)
            if b1 in (3, 5, 9, 13, 17, 21, 47, 51, 55, 59):
                hit(bar, 0, CRASH, 95, 2)
            if sec == "A2" and b1 % 2 == 0:
                hit(bar, 6.5, OPEN_HH, 70)
            if b1 in (22, 62):  # fill on the last two beats
                out[:] = [n for n in out if not (n[0] >= at(bar, 5)[1] * BEAT and n[0] < at(bar, 7)[1] * BEAT)]
                for i, tom in enumerate([SNARE, SNARE, HIGH_TOM, HIGH_TOM, MID_TOM, MID_TOM, LOW_TOM, LOW_TOM]):
                    hit(bar, 5 + i / 4, tom, 85 + i * 3, .25)
        elif sec == "B":  # half-time on the ride
            for b in (0, 4.5):
                hit(bar, b, KICK, 110)
            hit(bar, 3, SNARE, 108)
            for q in range(7):
                hit(bar, q, RIDE, 78 if q % 2 == 0 else 62)
            if b1 in (23, 29):
                hit(bar, 0, CRASH, 95, 2)
            if b1 == 36:
                for i in range(4):
                    hit(bar, 5 + i / 2, SNARE, 80 + i * 8)
        elif sec == "C":
            if b1 == 37:
                hit(bar, 0, KICK, 115)
                hit(bar, 0, CRASH, 105, 4)
            elif b1 <= 44:  # kick follows the low bass notes
                for b, key, _ in RIFF[r]:
                    if key < k("C2"):
                        hit(bar, b, KICK, 100)
            elif b1 == 45:  # build: snare 8ths, rising
                for e in range(14):
                    hit(bar, e / 2, SNARE, 50 + e * 3)
                hit(bar, 0, KICK, 105)
            elif b1 == 46:  # build: snare 16ths, rising
                for s in range(28):
                    hit(bar, s / 4, SNARE, 60 + s)
                for b in (0, 3.5):
                    hit(bar, b, KICK, 110)
    return out


def tambourine():  # from A cycle 2 on and through A'
    return [note(*at(bar, e / 2), TAMBOURINE, .25, 70 if e % 2 else 50)
            for bar in range(BARS) if (9 <= bar + 1 <= 22) or section(bar) == "A2" for e in range(14)]


def kick_sub():  # standard-kit kick under the Power kit, for low end
    return [n for n in drums() if n[1] == KICK]


TRACKS = [
    ("Bass", (PICK_BASS, 0), bass),
    ("Sub", (SYNTH_BASS, 0), bass),
    ("Guitar", (DIST_GUITAR, 0), rhythm_guitar),
    ("Lead", (OD_GUITAR, 0), lead),
    ("Ghost", (CLEAN_GUITAR, 0), ghost_guitar),
    ("Drums", (POWER_KIT, 128), drums),
    ("Kick", (STANDARD_KIT, 128), kick_sub),
    ("Tamb", (STANDARD_KIT, 128), tambourine),
]
MIX = {"Bass": (1.0, 0, 0, 0, 0), "Sub": (1.5, 0, 0, 0, 0), "Guitar": (0.4, 0, 0, 0, 0), "Lead": (0.55, 0, 0, 0, 0),
       "Ghost": (0.3, 0, 0, 0, 0), "Drums": (0.85, 0, 0, 0, 0), "Kick": (1.4, 0, 0, 0, 0), "Tamb": (0.35, 0, 0, 0, 0)}
