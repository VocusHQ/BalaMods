"""Vesper: the Balatro theme as a spaghetti western ride (4/4 triplet shuffle, 150 BPM). All five versions.

Locked picked the "ride" sample (Ghost Riders feel) over the 7/4 riff sketch ("too similar") and a waltz.
Kept from Balatro: the chord loop and form idea (A / B / C / A), the lead anchors F, C, Bb. Own groove,
bass, riff and tunes. One "span" = one chord = two 4/4 bars (8 beats, 3.2 s).

Form (40 spans, 128 s), shared by every version so the game can crossfade them in sync:
  intro (2)  twang riff alone, the gallop comes in
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

VERSION = os.environ.get("VERSION", "main")
BPM, LEAD_IN, SPAN = 150, 1, 8
BEATS_PER_BAR = SPAN  # reference_render / export work in chord spans
T = 1 / 3

CLEAN_GUITAR, CHOIR_OOHS, HARMONICA, HONKY_PIANO, CONTRABASS, TIMPANI = 27, 53, 22, 3, 43, 47
LOW_FLOOR_TOM, HIGH_FLOOR_TOM, LOW_TOM = 41, 43, 45

SECTIONS = [("intro", ["Bb", "Eb"]),
            ("A1", ["F", "Db", "Bb", "Eb", "F", "Bb", "Bb", "Eb"]),
            ("A2", ["F", "Db", "Bb", "Eb", "F", "Bb", "Bb", "Eb"]),
            ("B", ["Gb", "Ab", "Gb", "Fm", "Cb", "Gb", "Fm", "F"]),
            ("C", ["Db", "F", "Db", "F", "Db", "Eb"]),
            ("A3", ["F", "Db", "Bb", "Eb", "F", "Bb", "Bb", "Eb"])]
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


def tune_of(span):
    sec, i = SEC[span]
    return {"A1": A_TUNE, "A2": A_TUNE, "A3": A_TUNE, "B": B_TUNE, "C": C_CALLS}.get(sec, [[]] * 8)[i]


def at(span, beat):
    return 0, LEAD_IN + span * SPAN + beat


def sec(span):
    return SEC[span][0]


def spans(*secs):
    return [s for s in range(BARS) if sec(s) in secs]


SCALE = {"intro": .8, "A1": .9, "A2": .96, "B": .88, "C": .8, "A3": 1.1}
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


def fill(s, vel):  # triplet tom run down over the last two beats of a phrase
    toms = [LOW_TOM, LOW_TOM, HIGH_FLOOR_TOM, HIGH_FLOOR_TOM, LOW_FLOOR_TOM, LOW_FLOOR_TOM]
    return [note(*at(s, 6 + i * T), t, .25, v(s, vel - 4 * (i % 2))) for i, t in enumerate(toms)]


def shuffle(s, vel=92, fills=True, triplets=False):
    out = []
    for beat in range(SPAN):
        if fills and last_in_phrase(s) and beat >= 6:
            out += fill(s, vel)
            break
        out.append(note(*at(s, beat), LOW_FLOOR_TOM, .25, v(s, vel if beat % 2 == 0 else vel - 18, beat / SPAN)))
        if triplets:
            out.append(note(*at(s, beat + T), HIGH_FLOOR_TOM, .25, v(s, vel - 40, beat / SPAN)))
        out.append(note(*at(s, beat + 2 * T), HIGH_FLOOR_TOM, .25, v(s, vel - 34, beat / SPAN)))
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


# ---- main -----------------------------------------------------------------------------------------
def main_drums():
    out = []
    for s in range(BARS):
        name, i = SEC[s]
        if name == "intro":
            out += shuffle(s, 70, fills=False) if i == 1 else []
        elif name == "B":
            out += halftime(s)
        elif name == "C":
            out += halftime(s, 84) if i < 2 else shuffle(s, 96, triplets=i >= 4)
        else:
            out += shuffle(s, 92 if name != "A3" else 100)
    out += kicks(spans("A1", "A2", "A3"))
    out += kicks(spans("B"), (0, 4)) + kicks([s for s in spans("C") if SEC[s][1] < 2], (0, 4))
    out += kicks([s for s in spans("C") if SEC[s][1] >= 2])
    return out


def main_rims():
    return (rims(spans("A1", "A2", "A3")) + rims(spans("B"), (2, 6), 76)
            + rims([s for s in spans("C") if SEC[s][1] < 2], (2, 6)) + rims([s for s in spans("C") if SEC[s][1] >= 2]))


def main_timpani():  # A3 downbeats; a growing triplet roll over the last C span into A3
    c_last = spans("C")[-1]
    roll = [note(*at(c_last, 4 + i * T / 2), k("F2"), .2, int(50 + 70 * i / 24)) for i in range(24)]
    return timpani(spans("A3")) + timpani(spans("C")[2:5], 84) + roll


def main_tracks():
    return [
        ("Bass", (ACOUSTIC_BASS, 0), lambda: walking_bass(("A1", "A2", "B", "C", "A3"))
         + [note(*at(s, 0), k(CH[FORM[s]][0]), 3.5, 90) for s in spans("intro")]),
        ("Twang", (CLEAN_GUITAR, 0), lambda: twang_riff(("intro", "A1", "A2", "C", "A3"))
         + tune(("B",), 0, 100)),
        ("Trumpet", (TRUMPET, 0), lambda: tune(("A1", "A2", "C", "A3"))),
        ("Trombone", (TROMBONE, 0), lambda: tune(("A2", "A3", "C"), -12, 84)
         + [n for n in tune(("B",), 0, 70) if SEC[(n[0] // BEAT - LEAD_IN) // SPAN][1] >= 4]),
        ("Nylon", (NYLON_GUITAR, 0), lambda: strums(("A2", "B", "C", "A3"))),
        ("Choir", (CHOIR_OOHS, 0), lambda: choir(("A2", "B", "C", "A3"))),
        ("Timpani", (TIMPANI, 0), main_timpani),
        ("Drums", (STANDARD_KIT, 128), main_drums),
        ("Sticks", (STANDARD_KIT, 128), main_rims),
    ]


# ---- shop -----------------------------------------------------------------------------------------
def piano_comp():  # saloon piano: chords on 2 and 4 with a triplet push before 3
    out = []
    for s in range(BARS):
        voicing = [key + 12 for key in map(k, CH[FORM[s]][4])]
        for b, vel in ((1, 74), (3, 70), (5, 74), (7, 70), (2 - T, 54), (6 - T, 54)):
            out += [note(*at(s, b), key, .55, v(s, vel)) for key in voicing]
    return out


def shop_drums():
    out = []
    for s in range(BARS):
        out += [note(*at(s, b), LOW_FLOOR_TOM, .25, 62 if b % 2 == 0 else 48) for b in range(SPAN)]
        out += [note(*at(s, b + 2 * T), HIGH_FLOOR_TOM, .25, 38) for b in range(SPAN)]
        if last_in_phrase(s):
            out += fill(s, 70)
    return out + kicks(range(BARS), (0, 4), 96)


def shop_tracks():
    every = ("intro", "A1", "A2", "B", "C", "A3")
    return [
        ("Bass", (ACOUSTIC_BASS, 0), lambda: walking_bass(every, 100)),
        ("Piano", (HONKY_PIANO, 0), piano_comp),
        ("Twang", (CLEAN_GUITAR, 0), lambda: tune(("A1", "A2", "A3"), -12, 100) + tune(("C",), -12, 80)),
        ("Nylon", (NYLON_GUITAR, 0), lambda: tune(("B",), 0, 96, clip=.5)),
        ("Drums", (STANDARD_KIT, 128), shop_drums),
        ("Sticks", (STANDARD_KIT, 128), lambda: rims(range(BARS), (2, 6), 84)),
    ]


# ---- packs ----------------------------------------------------------------------------------------
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


def packs_tracks():
    every = ("intro", "A1", "A2", "B", "C", "A3")
    return [
        ("Bass", (ACOUSTIC_BASS, 0), lambda: walking_bass(every, 110)),
        ("Twang", (CLEAN_GUITAR, 0), lambda: twang_riff(every, 84)),
        ("Trombone", (TROMBONE, 0), lambda: tune(("A1", "A2", "A3"), -12, 92) + tune(("B",), 0, 84)),
        ("Nylon", (NYLON_GUITAR, 0), lambda: nylon_ripple(("intro", "A1", "A2", "B", "A3"))
         + tune(("C",), -12, 100, clip=.5)),
        ("Choir", (CHOIR_OOHS, 0), lambda: choir(every, 54)),
        ("Congas", (STANDARD_KIT, 128), conga_pattern),
        ("Drums", (STANDARD_KIT, 128), lambda: [n for s in range(BARS) for n in shuffle(s, 80)]
         + kicks(range(BARS), (0, 4), 100)),
        ("Sticks", (STANDARD_KIT, 128), lambda: rims(range(BARS), (2, 6), 70)),
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
        ("Harmonica", (HARMONICA, 0), lambda: tune(("A1", "A2", "A3"), -12, 84) + tune(("B",), 0, 78) + tune(("C",), -12, 72)),
    ]


# ---- boss -----------------------------------------------------------------------------------------
def heartbeat():  # ba-bum, twice per bar; C keeps it, louder
    return [note(*at(s, b + d), KICK, .4, 118 if d == 0 else 96) for s in range(BARS) for b in (0, 2, 4, 6)
            for d in (0, T)]


def clock():  # ticking rim on every beat, steady, never stops
    return [note(*at(s, b), STICK, .2, 84 if b % 2 else 70) for s in range(BARS) for b in range(SPAN)]


def boss_toms():  # rolling low toms under the C section, a fill each phrase elsewhere
    out = []
    for s in range(BARS):
        if sec(s) == "C":
            out += shuffle(s, 104, triplets=True)
        elif last_in_phrase(s):
            out += fill(s, 100)
    return out


def pedal():  # low F tremolo under everything (triplet 8ths)
    return [note(*at(s, i * T), k("F2"), T, 64 + (12 if i % 3 == 0 else 0)) for s in range(BARS) for i in range(SPAN * 3)]


CREEP = ["F3", "Gb3", "F3", "E3"]


def creep():  # low strings creeping F-Gb-F-E, one note per bar
    return [note(*at(s, half * 4), k(CREEP[(2 * s + half) % 4]), 3.9, 82) for s in range(BARS) for half in (0, 1)]


def stabs():  # dissonant low brass: Gb against F, on the triplet push before 3 and 7
    return [note(*at(s, b), key, .5, 96) for s in spans("intro", "A1", "A2", "B", "A3") for b in (2 - T, 6 - T)
            for key in (k(CH[FORM[s]][0]) + 24, k(CH[FORM[s]][0]) + 25)]


def boss_tracks():
    every = ("intro", "A1", "A2", "B", "C", "A3")
    return [
        ("Bass", (ACOUSTIC_BASS, 0), lambda: walking_bass(every, 118)),
        ("Pedal", (STRINGS, 0), pedal),
        ("Creep", (CONTRABASS, 0), creep),
        ("Trumpet", (TRUMPET, 0), lambda: tune(("A1", "A2", "A3"), 0, 100, clip=.45)),
        ("Trombone", (TROMBONE, 0), lambda: tune(("B",), -12, 96, clip=.6) + stabs()),
        ("Choir", (CHOIR_OOHS, 0), lambda: choir(("B", "C"), 74)),
        ("Timpani", (TIMPANI, 0), lambda: timpani(range(BARS), 104)),
        ("Drums", (STANDARD_KIT, 128), lambda: heartbeat() + boss_toms()),
        ("Sticks", (STANDARD_KIT, 128), clock),
    ]


TRACKS = {"main": main_tracks, "shop": shop_tracks, "packs": packs_tracks, "planet": planet_tracks,
          "boss": boss_tracks}[VERSION]()

# gain, wobble (fast cents, Hz, slow cents, Hz): Balatro-style tremolo-arm wobble on the twang guitar
MIX = {"Bass": (1.6, 0, 0, 0, 0), "Twang": (0.9, 10, 5.5, 6, 0.4), "Trumpet": (0.75, 0, 0, 0, 0),
       "Trombone": (0.6, 0, 0, 0, 0), "Choir": (0.55, 0, 0, 6, 0.3), "Drums": (0.8, 0, 0, 0, 0),
       "Sticks": (0.45, 0, 0, 0, 0), "Nylon": (0.7, 0, 0, 0, 0), "Timpani": (0.9, 0, 0, 0, 0),
       "Piano": (0.5, 0, 0, 8, 0.35), "Congas": (0.6, 0, 0, 0, 0), "Strings": (0.8, 0, 0, 8, 0.3),
       "Keys": (0.5, 6, 4.5, 10, 0.3), "Harmonica": (0.6, 8, 5, 0, 0), "Pedal": (0.6, 0, 0, 0, 0),
       "Creep": (0.9, 0, 0, 0, 0)}
LOWPASS = {"Trumpet": 2000, "Trombone": 2000, "Twang": 1900, "Nylon": 3000, "Drums": 1600, "Sticks": 2500,
           "Choir": 2500, "Harmonica": 1800, "Piano": 2400, "Congas": 1500, "Timpani": 2000, "Pedal": 1500}
if VERSION == "planet":  # heavily muffled, like Balatro's planet version
    LOWPASS = {name: 1400 for name in MIX}
if VERSION == "packs":  # darker than main
    LOWPASS = {name: min(cut, 1800) for name, cut in LOWPASS.items()}
if VERSION == "boss":
    MIX["Bass"] = (2.0, 0, 0, 0, 0)  # bass grows, like Balatro's boss version
