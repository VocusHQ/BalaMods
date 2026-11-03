"""Basilicus: the Balatro theme as a medieval estampie (tavern / royal court dance, 4/4, 150 BPM). All five versions.

Locked picked the estampie sample over the 7/4 court dance. Kept from Balatro: the chord loop and form
(A / B / C / A), the lead anchors F, C, Bb. Own groove (straight eighths, frame drum "DUM tek-tek DUM-DUM
tek", stomps, claps), own tunes. No brass. One "span" = one chord = two 4/4 bars (8 beats, 3.2 s).
Band: lute (plucked nylon + harp), hurdy-gurdy drone (low accordion on root + fifth), English horn on
the tune, fiddle, bassoon bass, cello counter-melody, frame drum, nakers (timpani).

Form (40 spans, 128 s), shared by every version so the game can crossfade them in sync:
  intro (2)  main: the band lands on Bb and rings, the dance creeps back, frame drum roll into A1
  A1 (8)     a: the dance, reed tune          b: stomp-and-clap break, fiddle takes the tune
  A2 (8)     a: the lute plays the tune over busy frame drum    b: reed tune + cello counter-melody
  B  (8)     the court: stately half-time, harp ripples, reed sings a new tune, fiddle joins halfway
  C  (6)     the dance whips up: drums pile up span by span, calls climb, nakers roll into A3
  A3 (8)     everything: reed + fiddle tune, cello counter, claps, nakers
Versions (VERSION env), each built on what Balatro's own version for that place does (music/ORIGINAL.md):
  main    the dance above, changes every 4-span phrase
  shop    tavern table: 3+3+2 lilt on accordion musette chords + bassoon, hammered dulcimer tune,
          frame drum backbeat on 3 only, harp plucks the B tune
  packs   the minstrel's satchel: darker, busy hand drums, pizzicato ripples, viola tune, cello drone,
          pizzicato plucks the C calls
  planet  the chapel at night: no drums, muffled, held bass + choir + slow strings up front, slow
          harp arpeggio, recorder tune
  boss    the king's judgment: tense all loop: limping 3+3+2 procession drums, F/Gb drone grind,
          bassoon ostinato, low monk chant, a cello line creeping up each span, clipped reed tune;
          C strips to drums, bassoon and nakers
Render one: VERSION=boss python reference_render.py OUT.mp3 basilicus
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

DULCIMER, ACCORDION, VIOLA, CELLO, PIZZ, CONTRABASS, TIMPANI = 15, 21, 41, 42, 45, 43, 47
CHOIR_AAHS, ENGLISH_HORN, BASSOON_P, RECORDER, FIDDLE = 52, 74, 70, 74, 41  # soft recorder tune, viola for the fiddle part (GM reed + fiddle were nasal)
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

# chord: bass root, fifth, lute voicing (low to high)
CH = {"F": ("F2", "C3", ["F3", "A3", "C4", "Eb4"]), "Db": ("Db2", "Ab2", ["Db3", "Ab3", "C4", "F4"]),
      "Bb": ("Bb1", "F2", ["Bb2", "F3", "Bb3", "Db4"]), "Eb": ("Eb2", "Bb2", ["Eb3", "Bb3", "Db4", "Gb4"]),
      "Gb": ("Gb2", "Db3", ["Gb3", "Bb3", "Db4", "F4"]), "Ab": ("Ab1", "Eb2", ["Ab2", "Eb3", "Gb3", "C4"]),
      "Fm": ("F2", "C3", ["F3", "Ab3", "C4", "Eb4"]), "Cb": ("B1", "Gb2", ["B2", "Gb3", "Bb3", "Eb4"])}


def line(s):
    return [(float(eval(b)), k(n), float(eval(l))) for n, b, l in (x.split() for x in s.split(","))]


A_TUNE = [line(s) for s in [  # the estampie sample's tune, one line per span
    "F4 0 1, Eb4 1 .5, F4 1.5 .5, A4 2 1, F4 3 1, C4 4 1, Eb4 5 .5, F4 5.5 .5, A3 6 2",
    "Ab4 0 1, F4 1 .5, Ab4 1.5 .5, C5 2 2, Bb4 4 .5, Ab4 4.5 .5, F4 5 1, Db4 6 2",
    "C5 0 1.5, Bb4 1.5 .5, Ab4 2 .5, Bb4 2.5 .5, F4 3 1, Db4 4 1, F4 5 1, Bb4 6 2",
    "Gb4 0 1, F4 1 .5, Eb4 1.5 .5, Db4 2 1, Eb4 3 1, Bb3 4 1, Db4 5 .5, Eb4 5.5 .5, F4 6 1, A3 7 1",
    "F4 0 .5, G4 .5 .5, A4 1 1, C5 2 1, A4 3 1, F4 4 2, Eb4 6 1, C4 7 1",
    "Db4 0 1, F4 1 1, Bb4 2 2, Ab4 4 .5, Bb4 4.5 .5, C5 5 1, Bb4 6 2",
    "Db5 0 1, C5 1 .5, Bb4 1.5 .5, Ab4 2 1, F4 3 1, Db4 4 1, C4 5 .5, Db4 5.5 .5, Bb3 6 2",
    "Eb4 0 1, Gb4 1 1, Bb4 2 1, Ab4 3 .5, Gb4 3.5 .5, F4 4 1, Eb4 5 1, Db4 6 .5, C4 6.5 .5, A3 7 1",
]]
B_TUNE = [line(s) for s in [  # the court: a slow, stately tune over Balatro's B chords
    "Bb3 0 2, Db4 2 1, F4 3 1, Eb4 4 2, Db4 6 2",
    "C4 0 2, Eb4 2 1, Ab4 3 1, Gb4 4 2, Eb4 6 2",
    "Db4 0 1, Eb4 1 1, F4 2 2, Gb4 4 1, F4 5 1, Db4 6 2",
    "C4 0 2, Ab3 2 1, C4 3 1, Eb4 4 3, F4 7 1",
    "Gb4 0 2, Eb4 2 1, B3 3 1, Bb3 4 2, Gb3 6 2",
    "Bb3 0 1, Db4 1 1, F4 2 2, Eb4 4 1, Db4 5 1, Bb3 6 2",
    "Ab3 0 1, C4 1 1, F4 2 2, Eb4 4 1, C4 5 1, Ab3 6 2",
    "A3 0 2, C4 2 1, Eb4 3 1, F4 4 2, Eb4 6 1, C4 7 1",
]]
C_CALLS = [line(s) for s in [  # the dance whips up: running eighths, climbing
    "F4 0 .5, Ab4 .5 .5, F4 1 .5, Db4 1.5 .5, F4 2 1, Ab4 3 1, F4 4 .5, Ab4 4.5 .5, Db5 5 1, C5 6 2",
    "A4 0 .5, C5 .5 .5, A4 1 .5, F4 1.5 .5, A4 2 1, C5 3 1, A4 4 .5, C5 4.5 .5, Eb5 5 1, C5 6 2",
    "Ab4 0 .5, Db5 .5 .5, Ab4 1 .5, F4 1.5 .5, Ab4 2 1, Db5 3 1, C5 4 .5, Db5 4.5 .5, F5 5 1, Db5 6 2",
    "C5 0 .5, A4 .5 .5, C5 1 .5, Eb5 1.5 .5, C5 2 1, A4 3 1, C5 4 .5, Eb5 4.5 .5, F5 5 1, C5 6 2",
    "Db5 0 1, C5 1 .5, Db5 1.5 .5, F5 2 2, Eb5 4 .5, Db5 4.5 .5, C5 5 .5, Ab4 5.5 .5, F4 6 1, Ab4 7 1",
    "Gb4 0 1, F4 1 .5, Eb4 1.5 .5, Db4 2 1, Eb4 3 1, Gb4 4 .5, F4 4.5 .5, Eb4 5 .5, Db4 5.5 .5, C4 6 1, A3 7 1",
]]
COUNTER = [line(s) for s in [  # cello counter-melody against A_TUNE (written low, played an octave up)
    "F2 0 1, A2 1 1, C3 2 1, Eb3 3 1, F3 4 2, C3 6 1, A2 7 1",
    "Db3 0 1, C3 1 1, Ab2 2 1, F2 3 1, Ab2 4 2, C3 6 2",
    "Bb2 0 1, Db3 1 1, F3 2 2, Db3 4 1, Bb2 5 1, F2 6 2",
    "Eb3 0 1, Db3 1 1, Bb2 2 1, Gb2 3 1, Bb2 4 2, C3 6 1, A2 7 1",
    "F2 0 2, A2 2 1, C3 3 1, Eb3 4 1, C3 5 1, A2 6 2",
    "Bb2 0 1, F3 1 1, Db3 2 2, C3 4 1, Bb2 5 1, A2 6 2",
    "Bb2 0 2, Db3 2 1, F3 3 1, Gb3 4 1, F3 5 1, Db3 6 2",
    "Eb3 0 1, Gb3 1 1, Bb3 2 1, Gb3 3 1, Eb3 4 1, Db3 5 1, C3 6 1, A2 7 1",
]]

DUMS = (0, 2, 2.5, 4, 6, 6.5)  # the estampie beat, per span
TEKS = (1, 1.5, 3, 5, 5.5, 7)


def tune_of(span):
    sec, i = SEC[span]
    return {"A1": A_TUNE, "A2": A_TUNE, "A3": A_TUNE, "B": B_TUNE, "C": C_CALLS}.get(sec, [[]] * 8)[i]


def at(span, beat):
    return 0, LEAD_IN + span * SPAN + beat


def sec(span):
    return SEC[span][0]


def spans(*secs):
    return [s for s in range(BARS) if sec(s) in secs]


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


SCALE = {"intro": .8, "A1": .9, "A2": .96, "B": .86, "C": .8, "A3": 1.1}
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


def beat_of(n):
    b = n[0] / BEAT - LEAD_IN
    s = int(b // SPAN)
    return s, b - s * SPAN


def after_landing(notes, beat=4):
    """Drop everything in the first intro span before `beat`, so the landing chord rings alone."""
    return [n for n in notes if not (beat_of(n)[0] == 0 and beat_of(n)[1] < beat - .01)]


# ---- parts ----------------------------------------------------------------------------------------
def tune(secs, shift=0, vel=96, clip=1.0):
    return [note(*at(s, b), key + shift, max(.2, l * clip - .08), v(s, vel, b / SPAN))
            for s in spans(*secs) for b, key, l in tune_of(s)]


def span_tune(span_list, lines, shift=0, vel=96, clip=1.0):
    return [note(*at(s, b), key + shift, max(.2, l * clip - .08), v(s, vel, b / SPAN))
            for s in span_list for b, key, l in lines[SEC[s][1]]]


def landing(shift, vel, beats=4):
    """The A tune ends on A3, the leading tone: land on Bb at the top of the loop so the wrap resolves."""
    return [note(*at(0, 0), k("Bb3") + shift, beats - .1, vel)]


def lute(span_list, vel=66, accent=92):  # picked eighths: root, chord tones, octave; accents on the DUMs
    out = []
    for s in span_list:
        root, fifth, chord = k(CH[FORM[s]][0]) + 12, k(CH[FORM[s]][1]) + 12, [k(n) for n in CH[FORM[s]][2]]
        seq = [root, chord[1], fifth, chord[2], root + 12, chord[3], fifth, chord[2]]
        for i in range(16):
            b = i / 2
            out.append(note(*at(s, b), seq[i % 8], .45, v(s, accent if b in DUMS else vel)))
    return out


def strum(span_list, beats=(0, 4), vel=84, length=1.8):
    return [note(*at(s, b + i / 48), k(n), length, v(s, vel - 3 * i)) for s in span_list for b in beats
            for i, n in enumerate(CH[FORM[s]][2])]


def harp_chords(span_list, vel=70):
    return [note(*at(s, b), k(n), 1, v(s, vel)) for s in span_list for b in (0, 2.5, 4, 6.5)
            for n in CH[FORM[s]][2]]


def harp_ripple(span_list, vel=64):  # rising and falling eighths through the chord
    out = []
    for s in span_list:
        vo = [k(n) for n in CH[FORM[s]][2]]
        seq = vo + [vo[0] + 12] + vo[-1:0:-1]
        out += [note(*at(s, i / 2), seq[i % len(seq)], 1.2, v(s, vel - (6 if i % 2 else 0))) for i in range(16)]
    return out


def drone(span_list, vel=70):  # hurdy-gurdy: root + fifth held, re-bowed each chord
    return [note(*at(s, 0), k(n), SPAN - .1, v(s, vel)) for s in span_list for n in CH[FORM[s]][:2]]


def bassoon(span_list, vel=90):  # root on the DUM, octave below on the DUM-DUM
    return [note(*at(s, b), k(CH[FORM[s]][0]) - (12 if b in (2, 6) else 0), .9, v(s, vel))
            for s in span_list for b in (0, 2, 4, 6)]


def plucked_bass(span_list, beats=(0, 2.5, 4, 6.5), vel=104):  # the low end: root, fifth on the DUM-DUM
    return [note(*at(s, b), k(CH[FORM[s]][0 if b in (0, 4) else 1]) - (12 if CH[FORM[s]][0][-1] != "1" else 0), 1.2, v(s, vel))
            for s in span_list for b in beats]


def fill(s, vel):  # frame drum: DUM-DUM-DUM-DUM-ta-ta-ta-ta over the last two beats of a phrase
    hits = [(6, LOW_FLOOR_TOM), (6.5, LOW_FLOOR_TOM), (7, HIGH_FLOOR_TOM), (7.25, HIGH_FLOOR_TOM),
            (7.5, LOW_TOM), (7.75, LOW_TOM)]
    return [note(*at(s, b), t, .25, v(s, vel - (6 if b % 1 else 0))) for b, t in hits]


def estampie(s, vel=100, fills=True, tek=66):
    """One span of the dance beat: frame drum DUMs + stomps, rim teks."""
    out = []
    cut = 6 if fills and last_in_phrase(s) else SPAN
    out += [note(*at(s, b), LOW_FLOOR_TOM, .3, v(s, vel if b in (0, 4) else vel - 14)) for b in DUMS if b < cut]
    out += [note(*at(s, b), KICK, .3, v(s, vel + 4)) for b in DUMS[::2] if b < cut]  # stomps
    out += [note(*at(s, b), STICK, .2, v(s, tek)) for b in TEKS if b < cut]
    if cut < SPAN:
        out += fill(s, vel + 8)
    return out


def claps(span_list, beats=(1, 3, 5, 7), vel=70):
    return [note(*at(s, b), CLAP, .2, v(s, vel)) for s in span_list for b in beats]


def nakers(span_list, vel=96):  # timpani on the downbeat
    return [note(*at(s, 0), k(CH[FORM[s]][0]) + 12, 2, v(s, vel)) for s in span_list]


# ---- main -----------------------------------------------------------------------------------------
# The loop wrap works like Crescendo's: A3 ends, the whole band lands on Bb at the top of the loop and
# lets it ring, the dance creeps back over the second half, the second intro span builds into a frame
# drum roll and A1 opens with an accent. Main changes something every 4-span phrase (about 13 s).
def main_drums():
    out = []
    for s in range(BARS):
        name, i = SEC[s]
        if name == "intro" and i == 0:
            out += [note(*at(s, 0), LOW_FLOOR_TOM, .3, 112), note(*at(s, 0), KICK, .5, 118)]
            out += [note(*at(s, b), STICK, .2, 50) for b in (5, 5.5, 7)] + [note(*at(s, 6), LOW_FLOOR_TOM, .3, 70)]
        elif name == "intro":
            out += [n for n in estampie(s, 88, fills=False) if beat_of(n)[1] < 6 - .01] + fill(s, 112)
        elif s in where("A1b"):  # stomp-and-clap break: no frame drum, the crowd keeps the beat
            out += [note(*at(s, b), KICK, .3, v(s, 108)) for b in DUMS]
            if last_in_phrase(s):
                out += fill(s, 104)
        elif s in where("A2a"):  # busy frame drum under the lute tune: teks on every off-beat
            out += estampie(s, 92, tek=72) + [note(*at(s, b + .5), STICK, .2, v(s, 50)) for b in (0, 2, 4, 6)]
        elif name == "B":  # stately half-time
            out += [note(*at(s, b), LOW_FLOOR_TOM, .3, v(s, 92)) for b in (0, 4)]
            out += [note(*at(s, b), STICK, .2, v(s, 64)) for b in (2, 6)]
            if last_in_phrase(s):
                out += fill(s, 92)
        elif name == "C":  # piles up: DUMs on the beat -> the dance -> DUMs on every eighth
            if i < 2:
                out += [note(*at(s, b), LOW_FLOOR_TOM, .3, v(s, 96, b / SPAN)) for b in (0, 2, 4, 6)]
                out += [note(*at(s, b), KICK, .3, v(s, 100, b / SPAN)) for b in (0, 4)]
            elif i < 4:
                out += estampie(s, 100)
            else:
                cut = 6 if i == 5 else SPAN
                out += [note(*at(s, e / 2), LOW_FLOOR_TOM, .25, v(s, 100 if e % 2 == 0 else 76, e / 16))
                        for e in range(16) if e / 2 < cut]
                out += [note(*at(s, b), KICK, .3, v(s, 106)) for b in range(cut)]
                if i == 5:
                    out += fill(s, 116)
        else:
            out += estampie(s, 104 if name == "A3" else 98)
    return out


def main_claps():
    return claps(where("A1b", "A2b", "A3")) + claps([s for s in spans("C") if SEC[s][1] >= 2])


def main_timpani():  # A3 downbeats, the C build, a roll over the last C span, the loop landing, A1's accent
    c_last = spans("C")[-1]
    roll = [note(*at(c_last, 4 + i / 6), k("F2"), .2, int(50 + 70 * i / 24)) for i in range(24)]
    land = [note(*at(0, 0), k("Bb2"), 3, 112), note(*at(spans("A1")[0], 0), k("F2"), 2, 104)]
    return nakers(spans("A3")) + nakers(spans("C")[2:5], 84) + roll + land


def main_tracks():
    every = ("intro", "A1", "A2", "B", "C", "A3")
    return [
        ("Bassoon", (BASSOON_P, 0), lambda: after_landing(bassoon(spans(*every))) + [note(*at(0, 0), k("Bb1"), 3.9, 110)]),
        ("Drone", (ACCORDION, 0), lambda: drone(spans(*every))),
        ("Bass", (ACOUSTIC_BASS, 0), lambda: after_landing(plucked_bass(spans(*every))) + [note(*at(0, 0), k("Bb1"), 3.9, 108)]),
        ("Lute", (NYLON_GUITAR, 0), lambda: after_landing(lute(spans("intro", "A1", "A2b", "C", "A3")))
         + strum([0], (0,), 100, 3.5) + span_tune(where("A2a"), A_TUNE, 0, 104) + strum(spans("B"))),
        ("Harp", (HARP, 0), lambda: harp_chords(where("A1a", "A2", "A3")) + harp_ripple(spans("B"))
         + [note(*at(0, 0), k(n), 3.5, 84) for n in CH["Bb"][2]]),
        ("Reed", (ENGLISH_HORN, 0), lambda: tune(("A3", "B", "C")) + span_tune(where("A1a"), A_TUNE)
         + landing(0, 100)),
        ("Fiddle", (FIDDLE, 0), lambda: span_tune(where("A1b"), A_TUNE, 0, 96) + tune(("A3",), 0, 80)
         + span_tune(where("Bb"), B_TUNE, 0, 74) + tune(("C",), -12, 78) + landing(-12, 84)),
        ("Cello", (CELLO, 0), lambda: span_tune(where("A2b", "A3"), COUNTER, 12, 84)),
        ("Nakers", (TIMPANI, 0), main_timpani),
        ("Drums", (STANDARD_KIT, 128), main_drums),
        ("Claps", (STANDARD_KIT, 128), main_claps),
    ]


# ---- shop -----------------------------------------------------------------------------------------
# Tavern table: no estampie beat. A 3+3+2 lilt (eighths grouped 3+3+2, accents on 1, the and of 2,
# and 4): accordion musette chords and bassoon on the lilt, the tune on a hammered dulcimer, frame drum
# backbeat on 3 only (like Balatro's shop), harp plucks the B tune (Balatro's shop adds a pluck layer in B).
LILT = (0, 1.5, 3)  # per bar


def musette():
    return [note(*at(s, bar + b), k(n), .9 if b < 3 else .6, 66 if b == 0 else 58) for s in range(BARS)
            for bar in (0, 4) for b in LILT for n in CH[FORM[s]][2][1:]]


def shop_bassoon():
    out = []
    for s in range(BARS):
        root, fifth = k(CH[FORM[s]][0]), k(CH[FORM[s]][1])
        for bar in (0, 4):
            out += [note(*at(s, bar), root - 12, 1.3, 100), note(*at(s, bar + 1.5), fifth - 12, 1.3, 84),
                    note(*at(s, bar + 3), root, .8, 88)]
    return out


def shop_tracks():
    return [
        ("Bassoon", (BASSOON_P, 0), shop_bassoon),
        ("Accordion", (ACCORDION, 0), musette),
        ("Bass", (ACOUSTIC_BASS, 0), lambda: plucked_bass(range(BARS), (0, 1.5, 4, 5.5), 96)),
        ("Dulcimer", (DULCIMER, 0), lambda: tune(("A1", "A2", "A3"), 0, 92) + tune(("C",), -12, 80) + landing(0, 88)),
        ("Harp", (HARP, 0), lambda: tune(("B",), 0, 92, clip=.5)),
        ("Drums", (STANDARD_KIT, 128), lambda: [note(*at(s, b), LOW_FLOOR_TOM, .3, 84) for s in range(BARS) for b in (2, 6)]
         + [note(*at(s, bar + b), KICK, .3, 74 if b == 0 else 58) for s in range(BARS) for bar in (0, 4) for b in (0, 1.5)]),
    ]


# ---- packs ----------------------------------------------------------------------------------------
# The minstrel's satchel, by candlelight: darker, no stomps. Busy hand drums, pizzicato ripples, cello
# drone, a viola tune; pizzicato plucks the C calls (like Balatro's packs).
def hand_drums():
    pat = [(0, LOW_TOM, 92), (.5, MUTE_CONGA, 56), (.75, MUTE_CONGA, 44), (1, OPEN_CONGA, 70), (1.5, MUTE_CONGA, 54),
           (2, LOW_CONGA, 84), (2.5, LOW_TOM, 76), (3, OPEN_CONGA, 72), (3.25, MUTE_CONGA, 46), (3.5, MUTE_CONGA, 58),
           (3.75, MUTE_CONGA, 44)]
    return [note(*at(s, half + b), key, .25, vel) for s in range(BARS) for half in (0, 4) for b, key, vel in pat]


def pizz_ripple(span_list, vel=68):
    out = []
    for s in span_list:
        vo = [k(n) for n in CH[FORM[s]][2]]
        seq = [vo[0], vo[2], vo[1], vo[3], vo[2], vo[1]]
        out += [note(*at(s, i / 2), seq[i % len(seq)], .4, vel - (8 if i % 2 else 0)) for i in range(16)]
    return out


def packs_tracks():
    every = ("intro", "A1", "A2", "B", "C", "A3")
    return [
        ("Bassoon", (BASSOON_P, 0), lambda: [note(*at(s, b), k(CH[FORM[s]][0]), 1.8, 92) for s in range(BARS) for b in (0, 2.5, 4, 6.5)]),
        ("Drone", (CELLO, 0), lambda: [note(*at(s, 0), k(CH[FORM[s]][0]) + 12, SPAN - .2, 66) for s in range(BARS)]),
        ("Bass", (CONTRABASS, 0), lambda: [note(*at(s, b), k(CH[FORM[s]][0]) - (12 if CH[FORM[s]][0][-1] != "1" else 0), 3.8, 100)
                                           for s in range(BARS) for b in (0, 4)]),
        ("Pizz", (PIZZ, 0), lambda: pizz_ripple(spans("intro", "A1", "A2", "B", "A3")) + tune(("C",), -12, 100, clip=.5)),
        ("Viola", (VIOLA, 0), lambda: tune(("A1", "A2", "A3", "B"), -12, 98) + landing(-12, 90)),
        ("Hands", (STANDARD_KIT, 128), hand_drums),
        ("Drums", (STANDARD_KIT, 128), lambda: [note(*at(s, b), LOW_FLOOR_TOM, .3, 82) for s in spans(*every) for b in (0, 4)]),
    ]


# ---- planet ---------------------------------------------------------------------------------------
# The chapel at night: no drums, heavily muffled, held bass and pads loud, a slow harp arpeggio (the
# keys layer in Balatro's planet version), a recorder tune.
def held(span_list, notes_of, shift, vel):
    out = []
    for s in span_list:
        notes = notes_of(s)
        out += [note(*at(s, 0), k(n) + shift, SPAN - .2, vel) for n in (notes if isinstance(notes, list) else [notes])]
    return out


def slow_harp():
    out = []
    for s in range(BARS):
        vo = [k(n) for n in CH[FORM[s]][2]]
        out += [note(*at(s, b), vo[i % 4], 2.5, 58) for i, b in enumerate((0, 1.5, 3, 4, 5.5, 7))]
    return out


def planet_tracks():
    every = list(range(BARS))
    return [
        ("Bass", (CONTRABASS, 0), lambda: held(every, lambda s: CH[FORM[s]][0], 12, 96)),
        ("Strings", (SLOW_STRINGS, 0), lambda: held(every, lambda s: CH[FORM[s]][2], 0, 70)),
        ("Choir", (CHOIR_AAHS, 0), lambda: held(every, lambda s: CH[FORM[s]][2][:3], 0, 66)),
        ("Harp", (HARP, 0), slow_harp),
        ("Recorder", (RECORDER, 0), lambda: tune(("A1", "A2", "A3"), -12, 86) + tune(("B",), 0, 80) + tune(("C",), -12, 74)
         + landing(-12, 80)),
    ]


# ---- boss -----------------------------------------------------------------------------------------
# The king's judgment, tense from the first beat to the last. The harmony freezes on an F drone
# grinding against Gb; the dance turns into a heavy march (stomp on every beat, frame drum DUMs);
# a cello line creeps up a semitone every span and resets each phrase; monks chant low; nakers roll
# into every phrase. C strips to drums, bassoon and nakers (like Balatro's boss version).
def wave(s, vel):  # each 4-span phrase leans harder
    return max(1, min(127, int(vel * (.86 + .07 * (SEC[s][1] % 4)))))


def boss_bassoon():  # eighth ostinato: F F F' F Gb F F' F
    keys = ["F1", "F1", "F2", "F1", "Gb1", "F1", "F2", "F1"]
    return [note(*at(s, e / 2), k(keys[e % 8]), .45, wave(s, 112 if e % 4 == 0 else 92)) for s in range(BARS)
            for e in range(16)]


def march():  # a limping procession: heavy drum on 1, 4 and 7 of each span (3+3+2), stomps on 1 and 5
    out = []
    for s in range(BARS):
        last = last_in_phrase(s)
        cut = 6 if last else SPAN
        out += [note(*at(s, b), LOW_FLOOR_TOM, .4, wave(s, 116)) for b in (0, 3, 6) if b < cut]
        out += [note(*at(s, b), KICK, .4, wave(s, 120)) for b in (0, 4) if b < cut]
        if last:
            out += fill(s, 116)
    return out


def tick():  # a dry rim on the off-beats of the procession, never stops
    return [note(*at(s, b), STICK, .15, 70) for s in range(BARS) for b in (1.5, 4.5, 7)]


def boss_timpani():
    out = []
    for s in range(BARS):
        if last_in_phrase(s):
            out += [note(*at(s, 4 + i / 6), k("F2"), .2, int(60 + 60 * i / 24)) for i in range(24)]
            out += [note(*at(s, b), k("F2"), 1, 100) for b in (0, 2)]
        else:
            out += [note(*at(s, b), k("F2"), 1.5, wave(s, 104)) for b in (0, 4)]
    return out


def boss_tracks():
    not_c = [s for s in range(BARS) if sec(s) != "C"]
    return [
        ("Bassoon", (BASSOON_P, 0), boss_bassoon),
        ("Bass", (ACOUSTIC_BASS, 0), lambda: [note(*at(s, b), k("F1"), 1.5, wave(s, 110)) for s in range(BARS) for b in (0, 3, 6)]),
        ("Drone", (ACCORDION, 0), lambda: [note(*at(s, 0), k(n), SPAN - .1, 72) for s in range(BARS) for n in ("F2", "Gb2", "C3")]),
        ("Cello", (CELLO, 0), lambda: [note(*at(s, 0), k("F3") + SEC[s][1] % 4, SPAN - .2, wave(s, 90)) for s in not_c]),
        ("Choir", (CHOIR_AAHS, 0), lambda: [note(*at(s, 0), k(n), SPAN - .2, wave(s, 74)) for s in not_c
                                            for n in ("F2", "C3", "Db3")]),
        ("Reed", (ENGLISH_HORN, 0), lambda: tune(("A1", "A2", "A3"), 0, 100, clip=.45) + landing(0, 96, 1)),
        ("Fiddle", (FIDDLE, 0), lambda: tune(("B",), -12, 96, clip=.6)
         + [note(*at(s, b), key, .4, wave(s, 88)) for s in not_c for b in (2.5, 6.5) for key in (k("F3"), k("Gb3"))]),
        ("Nakers", (TIMPANI, 0), boss_timpani),
        ("Drums", (STANDARD_KIT, 128), march),
        ("Ticks", (STANDARD_KIT, 128), tick),
    ]


TRACKS = {"main": main_tracks, "shop": shop_tracks, "packs": packs_tracks, "planet": planet_tracks,
          "boss": boss_tracks}[VERSION]()

# gain, wobble (fast cents, Hz, slow cents, Hz)
MIX = {"Bassoon": (0.55, 0, 0, 0, 0), "Drone": (0.22, 4, 5, 4, 0.3), "Lute": (0.75, 0, 0, 0, 0), "Harp": (0.5, 0, 0, 0, 0),
       "Reed": (0.65, 0, 0, 0, 0), "Fiddle": (0.5, 0, 0, 0, 0), "Cello": (0.6, 0, 0, 0, 0), "Nakers": (0.8, 0, 0, 0, 0),
       "Drums": (0.65, 0, 0, 0, 0), "Claps": (0.22, 0, 0, 0, 0), "Accordion": (0.3, 4, 5, 4, 0.3),
       "Dulcimer": (0.6, 0, 0, 0, 0), "Ticks": (0.35, 0, 0, 0, 0), "Pizz": (0.7, 0, 0, 0, 0), "Viola": (0.7, 8, 5, 0, 0),
       "Hands": (0.55, 0, 0, 0, 0), "Bass": (1.1, 0, 0, 0, 0), "Strings": (0.8, 0, 0, 8, 0.3), "Choir": (0.55, 0, 0, 6, 0.3),
       "Recorder": (0.6, 6, 5, 0, 0)}
LOWPASS = {"Lute": 2400, "Harp": 2400, "Drone": 1200, "Reed": 1600, "Fiddle": 1500, "Cello": 1600, "Drums": 1500,
           "Claps": 1200, "Nakers": 2000, "Accordion": 1400, "Dulcimer": 1600, "Ticks": 2000, "Pizz": 2400,
           "Viola": 1800, "Hands": 1500, "Choir": 2200, "Recorder": 1600}
if VERSION == "planet":  # heavily muffled, like Balatro's planet version
    LOWPASS = {name: 1200 for name in MIX}
if VERSION == "packs":  # darker than main
    LOWPASS = {name: min(LOWPASS.get(name, 1800), 1800) for name in MIX}
if VERSION == "boss":
    MIX["Bass"] = (1.4, 0, 0, 0, 0)  # bass grows, like Balatro's boss version
