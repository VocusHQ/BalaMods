"""Crescendo main v3 with a live, playful "teenage garage band" drummer (Room kit) instead of the Bolero snare.

The drummer keeps Balatro's beat (kick 1, &2, &5, 6; snare 3 and 7) but plays like a person:
fills into every 4-bar phrase, ghost notes, kick variations, tom grooves in B, a build that piles up
(toms -> snare 8ths -> 16ths -> fill), small timing/velocity wobble. No cymbal crashes (no-highs rule):
section starts get a big kick + floor tom + snare hit instead; hi-hats stay soft.
Render: python reference_render.py OUT.mp3 crescendo_garage
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403
import crescendo_main3 as v3  # noqa: E402
from crescendo_main3 import FORM, SEC, at, build_ramp, vel_of, first_bar  # noqa: E402

BPM, BEATS_PER_BAR, LEAD_IN, BARS = v3.BPM, v3.BEATS_PER_BAR, v3.LEAD_IN, v3.BARS
ROOM_KIT = 8
FLOOR_TOM, LOW_TOM, MID_TOM, HIGH_TOM, SIDE_STICK = 41, 45, 47, 50, 37
KICKS, SNARES = (0, 1.5, 4.5, 5), (2, 6)
rng = random.Random(7)

FILLS = {  # (start beat, [drum per 16th])
    "short": (6, [SNARE, SNARE, HIGH_TOM, MID_TOM]),
    "long": (5, [SNARE, SNARE, HIGH_TOM, HIGH_TOM, MID_TOM, MID_TOM, FLOOR_TOM, FLOOR_TOM]),
    "toms": (4, [HIGH_TOM, HIGH_TOM, HIGH_TOM, MID_TOM, MID_TOM, MID_TOM, LOW_TOM, LOW_TOM, LOW_TOM, FLOOR_TOM,
                 FLOOR_TOM, FLOOR_TOM]),
}


def drums():
    out = []

    def hit(bar, beat, key, v, length=.25):
        jitter = rng.uniform(-0.02, 0.02) if beat > 0 else 0  # a human, not a grid
        v = int(v + rng.uniform(-7, 7))
        out.append(note(*at(bar, max(0, beat + jitter)), key, length, max(1, min(127, v))))

    def accent(bar, v=120):  # instead of a crash: everything hits at once
        for key in (KICK, FLOOR_TOM, SNARE):
            hit(bar, 0, key, v, .5)

    def fill(bar, kind, v=100, upto=7):
        start, seq = FILLS[kind]
        for j, key in enumerate(seq):
            hit(bar, start + j / 4, key, v + j * 2)
        return start

    def groove(bar, sec, i, busy):
        fill_kind = None
        phrase_end = (i % 4 == 3)
        if phrase_end:
            fill_kind = "long" if (i == 7 or sec == "A3") else "short"
        cut = FILLS[fill_kind][0] if fill_kind else 7
        kicks = KICKS + ((3.5, 6.5) if busy and i % 2 == 1 else ())
        for b in kicks:
            if b < cut:
                hit(bar, b, KICK, vel_of(bar, 110))
        for b in SNARES:
            if b < cut:
                hit(bar, b, SNARE, vel_of(bar, 108))
        for e in range(14):  # soft 8th hats, accented on the beat
            b = e / 2
            if b < cut and not (busy and b in (2, 6)):
                hit(bar, b, CLOSED_HH, vel_of(bar, 46 if e % 2 == 0 else 30))
        if busy:  # ghost notes: the drummer's hands never stop
            for b in (2.75, 3.25, 5.75):
                if b < cut:
                    hit(bar, b, SNARE, 32)
        if fill_kind:
            fill(bar, fill_kind, vel_of(bar, 98))

    for bar, (r, (sec, i)) in enumerate(zip(FORM, SEC)):
        if r == "-":
            continue
        if sec == "intro":
            if i in (1, 2):  # kick and hats, getting in
                for b in KICKS:
                    hit(bar, b, KICK, 70 + 15 * i)
                for e in range(14):
                    hit(bar, e / 2, CLOSED_HH, 26 + 6 * i)
            else:  # bar 4: count-in fill
                for b in KICKS[:2]:
                    hit(bar, b, KICK, 95)
                fill(bar, "toms", 90)
        elif sec in ("A1", "A2", "A3"):
            if i == 0:
                accent(bar, vel_of(bar, 115))
            groove(bar, sec, i, busy=(sec != "A1" or i >= 4))
        elif sec == "B":  # tom groove: the fun, rolling part
            if i == 0:
                accent(bar, vel_of(bar, 110))
            for b in KICKS:
                hit(bar, b, KICK, vel_of(bar, 100))
                hit(bar, b, FLOOR_TOM, vel_of(bar, 88))
            for e in range(14):
                b = e / 2
                if b not in KICKS and b not in (6,):
                    hit(bar, b, (LOW_TOM, MID_TOM)[e % 2], vel_of(bar, 62 if e % 2 == 0 else 50))
            hit(bar, 6, SNARE, vel_of(bar, 110))
            hit(bar, 2, SIDE_STICK, vel_of(bar, 70))
            if i in (3, 7):
                fill(bar, "short" if i == 3 else "long", vel_of(bar, 100))
        elif sec == "C":  # the build: piles up bar by bar
            ramp = lambda b: build_ramp(bar, b / 7)  # noqa: E731
            if i <= 1:  # floor tom heartbeat + kicks
                for b in KICKS:
                    hit(bar, b, KICK, 70 + 40 * ramp(b))
                    hit(bar, b, FLOOR_TOM, 60 + 40 * ramp(b))
                if i == 1:
                    for b in SNARES:
                        hit(bar, b, SNARE, 80)
            elif i <= 3:  # snare 8ths, kick every beat in bar 4
                for e in range(14):
                    hit(bar, e / 2, SNARE, (50 + 60 * ramp(e / 2)) * (1.2 if e / 2 in SNARES else 1))
                for b in (KICKS if i == 2 else range(7)):
                    hit(bar, b, KICK, 85 + 35 * ramp(b))
                if i == 3:
                    for b in (.5, 2.5, 4.5, 6.5):
                        hit(bar, b, LOW_TOM, 70 + 40 * ramp(b))
            elif i == 4:  # snare 16ths
                for s in range(28):
                    hit(bar, s / 4, SNARE, (55 + 55 * ramp(s / 4)) * (1.2 if s % 4 == 0 else 1))
                for b in range(7):
                    hit(bar, b, KICK, 110)
            else:  # last bar: 16ths, then the big tom fill
                for s in range(28):  # snare keeps rolling under the fill, peaking at the very end
                    hit(bar, s / 4, SNARE, (88 + s * 1.4) * (1 if s < 16 else .8))
                for b in range(7):
                    hit(bar, b, KICK, 118)
                fill(bar, "toms", 115)
    a3 = first_bar("A3")
    accent(a3, 127)
    return out


TOM_KEYS = {FLOOR_TOM, LOW_TOM, MID_TOM, HIGH_TOM, SIDE_STICK}
_ALL = None


def _all():
    global _ALL
    if _ALL is None:
        _ALL = drums()
    return _ALL


def kit():  # kick, snare, hats
    return [n for n in _all() if n[1] not in TOM_KEYS]


def toms():  # toms and rim: own track, softer tone (their stick click is bright)
    return [n for n in _all() if n[1] in TOM_KEYS]


TRACKS = [t for t in v3.TRACKS if t[0] != "Drums"] + [("Drums", (ROOM_KIT, 128), kit), ("Toms", (ROOM_KIT, 128), toms)]
MIX = dict(v3.MIX, Drums=(1.0, 0, 0, 0, 0), Toms=(1.7, 0, 0, 0, 0))
LOWPASS = dict(v3.LOWPASS, Drums=5000, Toms=1200)
