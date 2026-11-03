"""Vesper: the Balatro theme as a spaghetti western ride (4/4 triplet shuffle, 150 BPM). All five versions.

Locked picked the "ride" sample (Ghost Riders feel) over the 7/4 riff sketch ("too similar") and a waltz.
Kept from Balatro: the chord loop and form idea (A / B / C / A), the lead anchors F, C, Bb. Own groove,
bass, riff and tunes. One "span" = one chord = two 4/4 bars (8 beats, 3.2 s).

Form (40 spans, 128 s), shared by every version so the game can crossfade them in sync:
  intro (2)  main: the band lands on Bb and rings, the gallop creeps back, tom fill into A1
  A1 (8)     the ride: shuffle on floor toms, twang riff, bass walking root-fifth, trumpet tune
  A2 (8)     + trombone an octave under, low choir, nylon guitar on 2 and 4
  B  (8)     campfire: half-time beat, twang guitar sings a new tune over Balatro's B chords,
             trombone joins halfway
  C  (6)     the stampede: Balatro's Db/F section, trumpet + trombone calls climb, drums go half-time ->
             shuffle -> rolling triplets, choir and timpani swell
  A3 (8)     everything, loudest
Versions (VERSION env), each built on what Balatro's own version for that place does (music/ORIGINAL.md):
  main    the build above
  shop    saloon: honky-tonk piano, light beat (cross-stick on 3 only), twang carries the tune, nylon
          plucks the B tune, gentle C
  packs   saddlebags: busier hand percussion (congas, toms), darker, trombone tune, nylon ripples,
          nylon plucks the C calls
  planet  desert night: no drums, everything muffled, bowed bass + slow strings + choir up front,
          soft electric-piano keys, tune on harmonica
  boss    showdown: tense the whole loop: heartbeat kick, ticking rim, low F pedal tremolo, creeping
          strings, clipped trumpet tune, dissonant low brass stabs; C strips to drums, bass, timpani
Render one: VERSION=boss python reference_render.py OUT.mp3 vesper
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403
from crescendo_main import k  # noqa: E402
from live import Live  # noqa: E402
import random  # noqa: E402

VERSION = os.environ.get("VERSION", "main")
BPM, LEAD_IN, SPAN = 150, 1, 8
BEATS_PER_BAR = SPAN  # reference_render / export work in chord spans
T = 1 / 3

CLEAN_GUITAR, CHOIR_OOHS, HARMONICA, HONKY_PIANO, CONTRABASS, TIMPANI = 27, 53, 22, 0, 43, 47  # soft piano, not honky-tonk
HORN = 60  # French horn: warm, carries the tune instead of the nasal trumpet
LOW_FLOOR_TOM, HIGH_FLOOR_TOM, LOW_TOM = 41, 43, 45

SECTIONS = [("intro", ["Bb", "Eb"]),
            ("A1", ["F", "Db", "Bb", "Eb", "F", "Bb", "Bb", "Eb"]),
            ("A2", ["F", "Db", "Bb", "Eb", "F", "Bb", "Bb", "Eb"]),
            ("B", ["Gb", "Ab", "Gb", "Fm", "Cb", "Gb", "Fm", "F"]),
            ("C", ["Db", "F", "Db", "F", "Db", "Eb"]),
            ("A3", ["F", "Db", "Bb", "Eb", "F", "Bb", "Bb", "F"])]  # A3 is a semitone up; its last span turns to F7 (V of Bb)
FORM, SEC = [], []  # chord per span, (section, index in section) per span
for _name, _chords in SECTIONS:
    for _i, _c in enumerate(_chords):
        FORM.append(_c)
        SEC.append((_name, _i))
BARS = len(FORM)  # spans

# chord: bass root, bass fifth, guitar riff root, riff 7th (semitones), strum voicing, choir voicing
CH = {
    "F": ("F1", "C2", "F2", 10, ["A2", "Eb3", "F3", "C4"], ["A2", "Eb3", "F3"]),
    "Db": ("Db2", "Ab1", "Db3", 11, ["Ab2", "C3", "F3", "Db4"], ["Ab2", "C3", "F3"]),
    "Bb": ("Bb1", "F1", "Bb2", 10, ["Bb2", "F3", "Bb3", "Db4"], ["Bb2", "Db3", "F3"]),
    "Eb": ("Eb2", "Bb1", "Eb3", 10, ["Bb2", "Eb3", "Gb3", "Db4"], ["Bb2", "Db3", "Gb3"]),
    "Gb": ("Gb1", "Db2", "Gb2", 11, ["Bb2", "Db3", "F3", "Gb3"], ["Bb2", "Db3", "F3"]),
    "Ab": ("Ab1", "Eb2", "Ab2", 10, ["Ab2", "C3", "Eb3", "Gb3"], ["Ab2", "C3", "Eb3"]),
    "Fm": ("F1", "C2", "F2", 10, ["F2", "C3", "Eb3", "Ab3"], ["Ab2", "C3", "F3"]),
    "Cb": ("B1", "Gb2", "B2", 11, ["B2", "Eb3", "Gb3", "Bb3"], ["B2", "Eb3", "Gb3"]),
}


def line(s):
    return [(float(eval(b)), k(n), float(eval(l))) for n, b, l in (x.split() for x in s.split(","))]


A_TUNE = [line(s) for s in [  # the ride sample's tune, one line per span
    "F4 0 3, Eb4 3 2/3, F4 11/3 1/3, A4 4 3, C5 7 1",
    "Db5 0 2, C5 2 2/3, Ab4 8/3 1/3, F4 3 3, Ab4 6 2/3, C5 20/3 4/3",
    "C5 0 8/3, Db5 8/3 1/3, C5 3 1, Bb4 4 3, F4 7 1",
    "Gb4 0 2, F4 2 2/3, Eb4 8/3 1/3, Db4 3 1, Eb4 4 2, F4 6 2/3, Gb4 20/3 1/3, A4 7 1",
    "F4 0 4, Eb4 4 2/3, F4 14/3 1/3, A4 5 3",
    "Bb4 0 3, A4 3 2/3, Bb4 11/3 1/3, C5 4 4",
    "Db5 0 8/3, C5 8/3 1/3, Bb4 3 1, F4 4 4",
    "Gb4 0 2, F4 2 1, Eb4 3 1, Db4 4 1, C4 5 1, A3 6 2",
]]
B_TUNE = [line(s) for s in [  # campfire tune, guitar register
    "Bb3 0 3, Ab3 3 1, Gb3 4 2, F3 6 1, Gb3 7 1",
    "Ab3 0 3, C4 3 1, Eb4 4 3, Db4 7 1",
    "Db4 0 2, C4 2 1, Bb3 3 1, Db4 4 2, F4 6 2",
    "Eb4 0 3, C4 3 1, Ab3 4 3, Bb3 7 1",
    "B3 0 2, Bb3 2 1, Gb3 3 1, Eb3 4 3, Gb3 7 1",
    "Bb3 0 3, Db4 3 1, F4 4 3, Gb4 7 1",
    "F4 0 2, Eb4 2 1, C4 3 1, Ab3 4 3, Bb3 7 1",
    "A3 0 4, C4 4 1, Eb4 5 1, F4 6 2",
]]
C_CALLS = [line(s) for s in [  # climbing calls, answered each span
    "F4 0 1, F4 1 2/3, Ab4 5/3 7/3, F4 6 2/3, Ab4 20/3 4/3",
    "A4 0 1, A4 1 2/3, C5 5/3 7/3, A4 6 2/3, C5 20/3 4/3",
    "Ab4 0 1, Ab4 1 2/3, Db5 5/3 7/3, Ab4 6 2/3, Db5 20/3 4/3",
    "A4 0 1, A4 1 2/3, C5 5/3 7/3, Eb5 6 2/3, C5 20/3 4/3",
    "Db5 0 1, Db5 1 2/3, F5 5/3 7/3, Db5 6 2/3, F5 20/3 4/3",
    "Eb5 0 2, Db5 2 1, Bb4 3 1, Gb4 4 1, Eb4 5 1, C4 6 1, A3 7 1",
]]


# The hook: "ba-da BA-da BAAA", answers the tune at the end of every 4-span A phrase (and opens the loop).
HOOK = line("Bb3 5 2/3, Eb4 17/3 1/3, Gb4 6 2/3, F4 20/3 1/3, A3 7 1")


def hook_span(span):
    sec, i = SEC[span]
    return (sec in ("A1", "A2", "A3") and i % 4 == 3) or (sec, i) == ("intro", 1)


def trim(span, lines):
    """In a hook span the tune stops at beat 5 so the hook can answer."""
    return [(b, key, min(l, 5 - b)) for b, key, l in lines if b < 5] if hook_span(span) else lines


def tune_of(span):
    sec, i = SEC[span]
    return trim(span, {"A1": A_TUNE, "A2": A_TUNE, "A3": A_TUNE, "B": B_TUNE, "C": C_CALLS}.get(sec, [[]] * 8)[i])


def at(span, beat):
    return 0, LEAD_IN + span * SPAN + beat


def sec(span):
    return SEC[span][0]


def spans(*secs):
    return [s for s in range(BARS) if sec(s) in secs]


SCALE = {"intro": .8, "A1": .84, "A2": .94, "B": .84, "C": .8, "A3": 1.12}
if VERSION != "main":  # the place versions hold one level all loop
    SCALE = {s: 1.0 for s in SCALE}


def v(span, vel, frac=0.0):
    """Velocity with section loudness; main's C ramps up through its 6 spans."""
    s, i = SEC[span]
    f = SCALE[s]
    if s == "C" and VERSION == "main":
        f = .7 + .45 * min(1, (i + frac) / 5.5)
    return max(1, min(127, int(vel * f)))


def last_in_phrase(span):
    s, i = SEC[span]
    return s != "intro" and (i % 4 == 3 or (s == "C" and i == 5))


# ---- parts ----------------------------------------------------------------------------------------
def tune(secs, shift=0, vel=96, clip=1.0):
    return [note(*at(s, b), key + shift, max(.2, l * clip - .1), v(s, vel, b / SPAN))
            for s in spans(*secs) for b, key, l in tune_of(s)]


def hook(vel, shift=0, clip=1.0):
    return [note(*at(s, b), key + shift, max(.2, l * clip - .1), v(s, vel)) for s in range(BARS) if hook_span(s)
            for b, key, l in HOOK]


def landing(shift, vel, beats=4):
    """The A tune ends on A3, the leading tone: land on Bb at the top of the loop so the wrap resolves."""
    return [note(*at(0, 0), k("Bb3") + shift, beats - .1, vel)]


def walking_bass(secs, vel=112):
    out = []
    for s in spans(*secs):
        root, fifth = k(CH[FORM[s]][0]), k(CH[FORM[s]][1])
        for b in (0, 2, 4, 6):
            out.append(note(*at(s, b), root if b in (0, 4) else fifth, 1.8, v(s, vel)))
        nxt = k(CH[FORM[(s + 1) % BARS]][0])
        out += [note(*at(s, 7 + i * T), nxt - 3 + i, T, v(s, vel - 20)) for i in range(3)]
    return out


def twang_riff(secs, vel=100):
    out = []
    for s in spans(*secs):
        r, sev = k(CH[FORM[s]][2]), CH[FORM[s]][3]
        for half in (0, 4):
            for b, iv, l, vv in [(0, 0, .6, 0), (2 * T, 0, .3, -30), (1, 7, .9, -12), (2, 12, .6, -8),
                                 (2 + 2 * T, sev, .3, -28), (3, 7, .9, -16)]:
                out.append(note(*at(s, half + b), r + iv, l, v(s, vel + vv)))
    return out


def strums(secs, vel=80, beats=(1, 3, 5, 7)):  # "chick" on 2 and 4, lightly rolled
    return [note(*at(s, b + i / 64), k(n), .6, v(s, vel - 3 * i)) for s in spans(*secs) for b in beats
            for i, n in enumerate(CH[FORM[s]][4])]


def choir(secs, vel=62):
    return [note(*at(s, 0), k(n), SPAN - .2, v(s, vel)) for s in spans(*secs) for n in CH[FORM[s]][5]]


def timpani(span_list, vel=96):
    return [note(*at(s, 0), k(CH[FORM[s]][0]) + 12, 2, v(s, vel)) for s in span_list]


FILLS = [  # a live drummer never plays the same fill twice in a row
    [(6, LOW_TOM), (6 + T, LOW_TOM), (6 + 2 * T, HIGH_FLOOR_TOM), (7, HIGH_FLOOR_TOM), (7 + T, LOW_FLOOR_TOM),
     (7 + 2 * T, LOW_FLOOR_TOM)],
    [(6, LOW_FLOOR_TOM), (6 + T, LOW_FLOOR_TOM), (6 + 2 * T, HIGH_FLOOR_TOM), (7, LOW_TOM), (7 + T, HIGH_FLOOR_TOM),
     (7 + 2 * T, LOW_FLOOR_TOM), (6, KICK), (7, KICK)],
    [(6, LOW_TOM), (6 + 2 * T, HIGH_FLOOR_TOM), (7, LOW_FLOOR_TOM), (7 + T, LOW_FLOOR_TOM), (7 + 2 * T, LOW_FLOOR_TOM)],
]


def fill(s, vel):  # tom run over the last two beats of a phrase, one of three
    hits = FILLS[s % 3]
    return [note(*at(s, b), t, .25, v(s, vel - 4 * i % 8 + int(6 * (b - 6)))) for i, (b, t) in enumerate(hits)]


def shuffle(s, vel=92, fills=True, triplets=False):
    out = []
    rng = random.Random(s)
    for beat in range(SPAN):
        if fills and last_in_phrase(s) and beat >= 6:
            out += fill(s, vel)
            break
        out.append(note(*at(s, beat), LOW_FLOOR_TOM, .25, v(s, vel if beat % 2 == 0 else vel - 18, beat / SPAN)))
        if triplets:
            out.append(note(*at(s, beat + T), HIGH_FLOOR_TOM, .25, v(s, vel - 40, beat / SPAN)))
        out.append(note(*at(s, beat + 2 * T), HIGH_FLOOR_TOM, .25, v(s, vel - 34, beat / SPAN)))
        if not triplets and rng.random() < .3:  # ghost note: the drummer's hands never quite stop
            out.append(note(*at(s, beat + T), HIGH_FLOOR_TOM, .2, 30 + rng.randrange(12)))
    return out


def halftime(s, vel=80):
    out = [note(*at(s, b + 2 * T), HIGH_FLOOR_TOM, .25, v(s, vel - 40)) for b in range(SPAN)]
    if last_in_phrase(s):
        out += fill(s, vel)
    return out


def kicks(span_list, beats=(0, 2, 4, 6), vel=108):
    return [note(*at(s, b), KICK, .5, v(s, vel)) for s in span_list for b in beats]


def rims(span_list, beats=(1, 3, 5, 7), vel=88):
    return [note(*at(s, b), STICK, .25, v(s, vel)) for s in span_list for b in beats]


def train(span_list, accents=(1, 3, 5, 7), vel=100, ghost=40, fills=True):
    """The western train beat: snare on every triplet, backbeats hard, the rest ghosted. The engine of the ride."""
    out = []
    for s in span_list:
        rng = random.Random(1000 + s)
        stop = 6 if fills and last_in_phrase(s) else SPAN
        for beat in range(stop):
            for j in range(3):
                b = beat + j * T
                if j == 0 and beat in accents:
                    out.append(note(*at(s, b), SNARE, .25, v(s, vel, beat / SPAN)))
                elif ghost:
                    out.append(note(*at(s, b), SNARE, .2, ghost + rng.randrange(12) + (8 if j == 2 else 0)))
    return out


# ---- main -----------------------------------------------------------------------------------------
# Main changes something every 4-span phrase (about 13 s), so it never sits still:
#   A1a ride + trumpet       A1b stop-time: band hits only, trumpet carries on, rims keep time
#   A2a "train": guitar takes the tune, rolling triplet toms, no riff, no trumpet
#   A2b + trombone counter-melody       A3 trumpet tune + trombone counter + riff + everything
COUNTER = [line(s) for s in [  # trombone counter-melody against A_TUNE: moves where the tune holds
    "C4 0 1, A3 1 2, C4 3 1, Eb4 4 3, F4 7 1",
    "F3 0 2, Ab3 2 1, C4 3 1, Db4 4 2, C4 6 2",
    "F3 0 1, Bb3 1 2, Db4 3 1, F4 4 2, Db4 6 1, Bb3 7 1",
    "Bb3 0 2, Db4 2 1, Bb3 3 1, Gb3 4 2, A3 6 1, C4 7 1",
    "A3 0 1, C4 1 1, Eb4 2 2, C4 4 1, A3 5 3",
    "Db4 0 1, F4 1 1, Db4 2 1, Bb3 3 1, F3 4 2, Ab3 6 1, Bb3 7 1",
    "F3 0 2, Bb3 2 1, Db4 3 1, Db4 4 1, C4 5 1, Bb3 6 1, Ab3 7 1",
    "Eb3 0 2, Bb3 2 2, Gb3 4 1, Eb3 5 1, F3 6 2",
]]
STOP_HITS = (0, 3 + 2 * T, 4)


def phrase(s):
    name, i = SEC[s]
    return name, i // 4


def where(*keys):
    """Spans matching section names ('A1') or phrases ('A1b' = second half of A1)."""
    out = []
    for s in range(BARS):
        name, half = phrase(s)
        if name in keys or (half < 2 and f"{name}{'ab'[half]}" in keys):
            out.append(s)
    return out


STOPS = [s for s in where("A1b") if SEC[s][1] < 7]  # the phrase's last span plays a fill back in


def beat_of(n):
    b = n[0] / BEAT - LEAD_IN
    s = int(b // SPAN)
    return s, b - s * SPAN


def stop_time(notes):
    out = []
    for n in notes:
        s, b = beat_of(n)
        if s in STOPS and not any(abs(b - h) < .05 for h in STOP_HITS):
            continue
        out.append(n)
    return out


def span_tune(span_list, lines, shift=0, vel=96, clip=1.0):
    return [note(*at(s, b), key + shift, max(.2, l * clip - .1), v(s, vel, b / SPAN))
            for s in span_list for b, key, l in trim(s, lines[SEC[s][1]])]


# The loop wrap works like Crescendo's: A3 ends, the whole band lands on Bb at the top of the loop
# and lets it ring (a real ending, not a dead stop), the gallop creeps back in over the second half,
# the second intro span builds and plays a tom fill into A1, and A1 opens with an accent.
def after_landing(notes, beat=4):
    """Drop everything in the first intro span before `beat`, so the landing chord rings alone."""
    return [n for n in notes if not (beat_of(n)[0] == 0 and beat_of(n)[1] < beat - .01)]


def main_bass():
    walk = after_landing(walking_bass(("intro", "A1", "A2", "B", "C", "A3")))
    hits = [note(*at(s, 3 + 2 * T), k(CH[FORM[s]][0]), .3, v(s, 110)) for s in STOPS]
    land = [note(*at(0, 0), k("Bb1"), 3.9, 116)]
    return stop_time(walk) + hits + land


def main_drums():
    out = []
    for s in range(BARS):
        name, i = SEC[s]
        if name == "intro" and i == 0:  # landing hit, then the gallop creeps back in
            out.append(note(*at(s, 0), LOW_FLOOR_TOM, .3, 112))
            out += after_landing(shuffle(s, 72, fills=False))
        elif name == "intro":  # building, tom fill into A1 (the count-in)
            out += [n for n in shuffle(s, 88, fills=False) if beat_of(n)[1] < 6 - .01] + fill(s, 112)
        elif name == "B":
            out += halftime(s)
        elif name == "C":
            out += halftime(s, 84) if i < 2 else shuffle(s, 96, triplets=i >= 4)
        elif s in where("A2a"):
            out += shuffle(s, 84, triplets=True)  # the train
        elif s in STOPS:
            out += [note(*at(s, h), LOW_FLOOR_TOM, .3, v(s, 104)) for h in STOP_HITS]
        else:
            out += shuffle(s, 100 if name == "A3" else 92, triplets=name == "A3")
    out += stop_time(kicks(where("A1", "A2b", "A3")) + [note(*at(s, 3 + 2 * T), KICK, .3, v(s, 104)) for s in STOPS])
    out += [note(*at(0, 0), KICK, .5, 118), note(*at(0, 4), KICK, .5, 70), note(*at(1, 0), KICK, .5, 90),
            note(*at(1, 4), KICK, .5, 96)]
    out += kicks(where("A2a", "B"), (0, 4)) + kicks([s for s in spans("C") if SEC[s][1] < 2], (0, 4))
    out += kicks([s for s in spans("C") if SEC[s][1] >= 2])
    return out


def main_rims():  # only where the snare rests: the stop-time phrase and the campfire
    return rims(STOPS) + rims(spans("B"), (2, 6), 76) + rims([s for s in spans("C") if SEC[s][1] < 2], (2, 6))


def main_snare():  # the train: light in A1a, full in A2 and A3, piling up through C
    c_hi = [s for s in spans("C") if SEC[s][1] >= 2]
    return (train([1], vel=84, ghost=34, fills=False) + train(where("A1a"), vel=92, ghost=32)
            + train([s for s in where("A1b") if s not in STOPS]) + train(spans("A2"), vel=100, ghost=40)
            + train(c_hi, vel=104, ghost=46) + train(spans("A3"), vel=108, ghost=46))


def main_timpani():  # A3 downbeats; stop-time hits; a growing triplet roll over the last C span into A3
    c_last = spans("C")[-1]
    roll = [note(*at(c_last, 4 + i * T / 2), k("F2"), .2, int(50 + 70 * i / 24)) for i in range(24)]
    hits = [note(*at(s, h), k(CH[FORM[s]][0]) + 12, .5, 96) for s in STOPS for h in STOP_HITS]
    land = [note(*at(0, 0), k("Bb2"), 3, 112), note(*at(spans("A1")[0], 0), k("F2"), 2, 104)]
    return timpani(spans("A3")) + timpani(spans("C")[2:5], 84) + roll + hits + land


def main_tracks():
    return [
        ("Bass", (ACOUSTIC_BASS, 0), main_bass),
        ("Twang", (CLEAN_GUITAR, 0), lambda: stop_time(after_landing(twang_riff(("intro", "A1", "C", "A3"))))
         + span_tune(where("A2a"), A_TUNE, -12, 104) + tune(("B",), 0, 100)),
        ("Trumpet", (HORN, 0), lambda: tune(("A1", "C", "A3")) + landing(0, 100) + hook(104)),
        ("Trombone", (TROMBONE, 0), lambda: span_tune(where("A2b", "A3"), COUNTER, 0, 88) + landing(-12, 92) + hook(96, -12)
         + tune(("C",), -12, 84) + span_tune(where("Bb"), B_TUNE, 0, 70)),
        ("Nylon", (NYLON_GUITAR, 0), lambda: after_landing(strums(("intro", "A2", "B", "C", "A3")))
         + [note(*at(0, i / 24), k(n), 3.5, 96 - 4 * i) for i, n in enumerate(CH["Bb"][4])]),
        ("Choir", (CHOIR_OOHS, 0), lambda: choir(("intro", "A2", "B", "C", "A3"))),
        ("Timpani", (TIMPANI, 0), main_timpani),
        ("Drums", (STANDARD_KIT, 128), main_drums),
        ("Sticks", (STANDARD_KIT, 128), main_rims),
        ("Snare", (STANDARD_KIT, 128), main_snare),
    ]


# ---- shop -----------------------------------------------------------------------------------------
# Saloon: no gallop, no walking bass. Honky-tonk stride piano carries the groove and the tune,
# brushes with the backbeat on 3 only (like Balatro's shop), banjo plucks the B tune.
BANJO = 105


def stride():  # left hand: bass note on 1 and 3, chord on 2 and 4
    out = []
    for s in range(BARS):
        root, fifth = k(CH[FORM[s]][0]) + 12, k(CH[FORM[s]][1]) + 12
        for b in (0, 2, 4, 6):
            out.append(note(*at(s, b), root if b in (0, 4) else fifth, .9, 84))
        for b in (1, 3, 5, 7):
            out += [note(*at(s, b), key, .5, 66) for key in map(k, CH[FORM[s]][4][1:])]
    return out


def shop_tracks():
    return [
        ("Bass", (ACOUSTIC_BASS, 0), lambda: [note(*at(s, b), k(CH[FORM[s]][0] if b == 0 else CH[FORM[s]][1]), 3.6, 96)
                                              for s in range(BARS) for b in (0, 4)]),
        ("Piano", (HONKY_PIANO, 0), stride),
        ("PianoTune", (HONKY_PIANO, 0), lambda: tune(("A1", "A2", "A3"), 0, 92) + tune(("C",), -12, 78) + landing(0, 84) + hook(90)),
        ("Banjo", (BANJO, 0), lambda: tune(("B",), 0, 90, clip=.5)),
        ("Brushes", (BRUSH_KIT, 128), lambda: train(range(BARS), (2, 6), 96, 44, fills=False)
         + [note(*at(s, b), KICK, .4, 84) for s in range(BARS) for b in (0, 4)]),
    ]


# ---- packs ----------------------------------------------------------------------------------------
# Saddlebags, by lamplight: no gallop, no riff. Habanera-like bass, hand drums, rippling nylon
# guitar, low vibraphone swells, a muted trumpet; nylon plucks the C calls (like Balatro's packs).
def conga_pattern():  # busier hand percussion, triplet based
    pat = [(0, LOW_CONGA, 90), (2 * T, MUTE_CONGA, 60), (1, OPEN_CONGA, 70), (1 + T, MUTE_CONGA, 50),
           (1 + 2 * T, LOW_CONGA, 66), (2, LOW_CONGA, 84), (2 + 2 * T, MUTE_CONGA, 56), (3, OPEN_CONGA, 72),
           (3 + T, OPEN_CONGA, 52), (3 + 2 * T, MUTE_CONGA, 58)]
    return [note(*at(s, half + b), key, .25, vel) for s in range(BARS) for half in (0, 4) for b, key, vel in pat]


def nylon_ripple(secs, vel=70):  # rolling triplet arpeggio
    out = []
    for s in spans(*secs):
        vo = list(map(k, CH[FORM[s]][4]))
        seq = vo + vo[-2:0:-1]
        for i in range(SPAN * 3):
            out.append(note(*at(s, i * T), seq[i % len(seq)], T * 1.5, vel - (8 if i % 3 else 0)))
    return out


def habanera():  # dum . . da-dum per bar
    out = []
    for s in range(BARS):
        root, fifth = k(CH[FORM[s]][0]), k(CH[FORM[s]][1])
        for bar in (0, 4):
            out += [note(*at(s, bar), root, 1.4, 112), note(*at(s, bar + 1 + 2 * T), fifth, .3, 90),
                    note(*at(s, bar + 2), root + 12, 1.8, 100)]
    return out


def packs_tracks():
    every = ("intro", "A1", "A2", "B", "C", "A3")
    return [
        ("Bass", (ACOUSTIC_BASS, 0), habanera),
        ("Drone", (CONTRABASS, 0), lambda: held(every, 0, 12, 70)),
        ("Nylon", (NYLON_GUITAR, 0), lambda: nylon_ripple(("intro", "A1", "A2", "B", "A3"))
         + tune(("C",), -12, 100, clip=.5)),
        ("Vibes", (VIBES, 0), lambda: [note(*at(s, b), k(n) + 12, 3.8, 60) for s in range(BARS) for b in (0, 4)
                                       for n in CH[FORM[s]][5]]),
        ("Muted", (HORN, 0), lambda: tune(("A1", "A2", "A3"), 0, 92) + hook(92) + tune(("B",), 0, 88) + landing(-12, 88)),
        ("Congas", (STANDARD_KIT, 128), conga_pattern),
        ("Snare", (STANDARD_KIT, 128), lambda: [note(*at(s, b), STICK, .2, 84) for s in range(BARS) for b in (2, 6)]),
        ("Drums", (STANDARD_KIT, 128), lambda: [note(*at(s, b), LOW_TOM, .3, 80) for s in range(BARS) for b in (0, 4)]
         + kicks(range(BARS), (0, 4), 92)),
    ]


# ---- planet ---------------------------------------------------------------------------------------
def held(secs, idx, shift, vel, patch_len=SPAN - .2):
    out = []
    for s in spans(*secs):
        notes = CH[FORM[s]][idx]
        for n in (notes if isinstance(notes, list) else [notes]):
            out.append(note(*at(s, 0), k(n) + shift, patch_len, vel))
    return out


def keys():  # soft electric piano: chord broken slowly in triplet-quarters
    out = []
    for s in range(BARS):
        vo = list(map(k, CH[FORM[s]][4]))
        for i, b in enumerate((0, 1 + T, 2 + 2 * T, 4, 5 + T, 6 + 2 * T)):
            out.append(note(*at(s, b), vo[i % len(vo)] + 12, 2, 54))
    return out


def planet_tracks():
    every = ("intro", "A1", "A2", "B", "C", "A3")
    return [
        ("Bass", (CONTRABASS, 0), lambda: held(every, 0, 12, 96)),
        ("Strings", (SLOW_STRINGS, 0), lambda: held(every, 4, 0, 70)),
        ("Choir", (CHOIR_OOHS, 0), lambda: choir(every, 70)),
        ("Keys", (EPIANO, 0), keys),
        ("Harmonica", (HARMONICA, 0), lambda: tune(("A1", "A2", "A3"), -12, 84) + tune(("B",), 0, 78) + landing(-12, 78) + hook(80, -12)
         + tune(("C",), -12, 72)),
    ]


# ---- boss -----------------------------------------------------------------------------------------
# Showdown, tense from the first beat to the last. The harmony freezes on a low F pedal grinding
# against Gb; war toms roll in triplets everywhere; a line creeps up a semitone every span and resets
# each phrase, so the pressure rises in waves; timpani roll into every phrase.
def wave(s, vel):  # each 4-span phrase leans harder
    return max(1, min(127, int(vel * (.86 + .07 * (SEC[s][1] % 4)))))


def boss_bass():  # triplet ostinato F F F', Gb on beats 4 and 8
    out = []
    for s in range(BARS):
        for b in range(SPAN):
            r = k("Gb1") if b in (3, 7) else k("F1")
            out += [note(*at(s, b + i * T), key, T, wave(s, vel))
                    for i, (key, vel) in enumerate([(r, 118), (r, 92), (r + 12, 100)])]
    return out


def war_toms():
    out = []
    for s in range(BARS):
        last = last_in_phrase(s)
        for b in range(6 if last else SPAN):
            out += [note(*at(s, b), LOW_FLOOR_TOM, .25, wave(s, 104 if b % 2 == 0 else 84))]  # on the beat only
        if last:
            out += fill(s, 112)
    return out


def heartbeat():  # ba-bum, twice per bar
    return [note(*at(s, b + d), KICK, .4, 120 if d == 0 else 100) for s in range(BARS) for b in (0, 2, 4, 6)
            for d in (0, T)]


def clock():  # ticking rim on every beat, steady, never stops
    return [note(*at(s, b), STICK, .2, 84 if b % 2 else 70) for s in range(BARS) for b in range(SPAN)]


def boss_timpani():  # F on 1 and 3 of each bar, a rising roll into every phrase
    out = []
    for s in range(BARS):
        if last_in_phrase(s):
            out += [note(*at(s, 4 + i * T / 2), k("F2"), .2, int(60 + 60 * i / 24)) for i in range(24)]
            out += [note(*at(s, b), k("F2"), 1, 100) for b in (0, 2)]
        else:
            out += [note(*at(s, b), k("F2"), 1.5, wave(s, 104)) for b in (0, 4)]
    return out


def pedal():  # low string tremolo on F against Gb: a semitone grind under everything
    return [note(*at(s, i * T), key, T, 62 + (12 if i % 3 == 0 else 0)) for s in range(BARS)
            for i in range(SPAN * 3) for key in (k("F2"), k("Gb2"))]


def creep():  # one semitone higher every span, back down each phrase: F, Gb, G, Ab
    return [note(*at(s, 0), k("F3") + SEC[s][1] % 4, SPAN - .2, wave(s, 90)) for s in range(BARS)]


def stabs():  # dissonant low brass: F + Gb, on the triplet pushes
    return [note(*at(s, b), key, .5, wave(s, 100)) for s in range(BARS) for b in (2 - T, 6 - T)
            for key in (k("F3"), k("Gb3"))]


def boss_tracks():
    return [
        ("Bass", (ACOUSTIC_BASS, 0), boss_bass),
        ("Pedal", (STRINGS, 0), pedal),
        ("Creep", (SLOW_STRINGS, 0), creep),
        ("Trumpet", (HORN, 0), lambda: tune(("A1", "A2", "A3", "C"), 0, 100, clip=.45) + landing(0, 96, 1)
         + hook(100, 0, .5)),
        ("Trombone", (TROMBONE, 0), lambda: tune(("B",), -12, 100, clip=.6) + stabs() + hook(96, -12, .5)),
        ("Choir", (CHOIR_OOHS, 0), lambda: [note(*at(s, 0), k(n), SPAN - .2, wave(s, 76)) for s in range(BARS)
                                            for n in ("F2", "C3", "Db3")]),
        ("Timpani", (TIMPANI, 0), boss_timpani),
        ("Drums", (STANDARD_KIT, 128), lambda: heartbeat() + war_toms()),
        ("Snare", (STANDARD_KIT, 128), lambda: train(range(BARS), (2, 6), 100, 0, fills=False)
         + [note(*at(s, 7 + j / 6), SNARE, .15, 50 + 10 * j) for s in range(BARS) if last_in_phrase(s) for j in range(6)]),
    ]


TRACKS = {"main": main_tracks, "shop": shop_tracks, "packs": packs_tracks, "planet": planet_tracks,
          "boss": boss_tracks}[VERSION]()

# ---- the live band --------------------------------------------------------------------------------
# Every version: A3 a semitone up (all versions, so crossfades stay in tune), timing/velocity wobble.
# Main only: the break. The last C span hits once on beat 5, stops dead, and the pickup brings A3 in.
LIVE = Live(LEAD_IN, SPAN)
UP = spans("A3")[:-1]
C_LAST = spans("C")[-1]
HIT = {  # the unison hit before the break (C's last chord, Eb minor)
    "Bass": [note(*at(C_LAST, 4), k("Eb2"), 1, 124)],
    "Timpani": [note(*at(C_LAST, 4), k("Eb2"), 1.5, 124)],
    "Drums": [note(*at(C_LAST, 4), KICK, .5, 124), note(*at(C_LAST, 4), LOW_FLOOR_TOM, .5, 120)],
    "Snare": [note(*at(C_LAST, 4), SNARE, .5, 120)],
    "Trumpet": [note(*at(C_LAST, 4), k(n), .9, 112) for n in ("Bb3", "Eb4")],
    "Trombone": [note(*at(C_LAST, 4), k(n), .9, 108) for n in ("Eb3", "Gb3")],
    "Nylon": [note(*at(C_LAST, 4 + i / 48), k(n), .9, 110) for i, n in enumerate(CH["Eb"][4])],
}


def _post(name, prog, fn):
    drums = prog[1] == 128

    def run():
        notes = fn()
        if VERSION == "main":
            notes = LIVE.cut(notes + HIT.get(name, []), C_LAST)
        if not drums:
            notes = LIVE.shift(notes, UP)
        return LIVE.humanize(notes, f"{VERSION}-{name}", 2 if drums else 1, 8 if drums else 5)
    return run


TRACKS = [(n, p, _post(n, p, f)) for n, p, f in TRACKS]

# gain, wobble (fast cents, Hz, slow cents, Hz): Balatro-style tremolo-arm wobble on the twang guitar
MIX = {"Bass": (1.2, 0, 0, 0, 0), "Twang": (0.65, 6, 5.5, 4, 0.4), "Trumpet": (0.75, 0, 0, 0, 0),
       "Trombone": (0.6, 0, 0, 0, 0), "Choir": (0.55, 0, 0, 6, 0.3), "Drums": (1.6, 0, 0, 0, 0),
       "Sticks": (0.5, 0, 0, 0, 0), "Snare": (1.3, 0, 0, 0, 0), "Nylon": (0.7, 0, 0, 0, 0), "Timpani": (0.9, 0, 0, 0, 0),
       "Piano": (0.5, 0, 0, 8, 0.35), "Congas": (0.9, 0, 0, 0, 0), "Strings": (0.8, 0, 0, 8, 0.3),
       "Keys": (0.5, 6, 4.5, 10, 0.3), "Harmonica": (0.6, 8, 5, 0, 0), "Pedal": (0.6, 0, 0, 0, 0),
       "Creep": (0.9, 0, 0, 0, 0), "PianoTune": (0.6, 0, 0, 8, 0.35), "Banjo": (0.6, 0, 0, 0, 0),
       "Brushes": (1.5, 0, 0, 0, 0), "Drone": (0.7, 0, 0, 0, 0), "Vibes": (0.5, 6, 4.5, 0, 0),
       "Muted": (0.8, 0, 0, 0, 0)}
LOWPASS = {"Trumpet": 1800, "Trombone": 1800, "Twang": 1500, "Nylon": 3000, "Drums": 3500, "Sticks": 3500, "Snare": 4000,
           "Choir": 2500, "Harmonica": 1800, "Piano": 1800, "Congas": 3000, "Timpani": 2000, "Pedal": 1500,
           "PianoTune": 1800, "Banjo": 1800, "Brushes": 4000, "Vibes": 1800, "Muted": 1700, "Creep": 1800}
if VERSION == "planet":  # heavily muffled, like Balatro's planet version
    LOWPASS = {name: 1400 for name in MIX}
if VERSION == "packs":  # darker than main
    LOWPASS = {name: min(cut, 1800) for name, cut in LOWPASS.items()}
if VERSION == "boss":
    MIX["Bass"] = (1.5, 0, 0, 0, 0)  # bass grows, like Balatro's boss version
