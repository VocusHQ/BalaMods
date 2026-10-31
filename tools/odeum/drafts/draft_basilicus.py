"""Basilicus v1: Las Vegas casino swing (Rat Pack lounge -> big show). Eb major, 128 BPM, 16-bar loop, swung."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403

BPM, BARS = 128, 16

CH = {  # bass root, quality, voicing
    "Eb6": (39, "maj", [55, 58, 60, 63]), "C7": (36, "dom", [52, 58, 62]), "Fm7": (41, "min", [56, 60, 63]),
    "Bb7": (46, "dom", [56, 62, 67]), "Ab6": (44, "maj", [56, 60, 63, 65]), "Adim": (45, "dim", [57, 60, 63, 66]),
    "F7": (41, "dom", [51, 57, 62]), "Gm7": (43, "min", [53, 58, 62]), "Abm6": (44, "min", [56, 59, 63, 65]),
}
FORM = [("Eb6", "C7"), ("Fm7", "Bb7"), ("Eb6", "C7"), ("Fm7", "Bb7"), "Ab6", "Adim", ("Eb6", "C7"), ("F7", "Bb7"),
        ("Eb6", "C7"), ("Fm7", "Bb7"), ("Gm7", "C7"), ("Fm7", "Bb7"), "Ab6", "Abm6", ("Eb6", "C7"), ("Fm7", "Bb7")]
MELODY = [
    [(0, 70, 1), (1, 72, .5), (1.5, 75, 1.5), (3, 72, 1)],
    [(0, 68, 1.5), (1.5, 67, .5), (2, 65, 2)],
    [(0, 70, 1), (1, 72, .5), (1.5, 75, 1), (2.5, 77, .5), (3, 75, 1)],
    [(0, 72, 1), (1, 68, 1), (2, 70, 2)],
    [(0, 72, 1.5), (1.5, 75, .5), (2, 77, 1), (3, 75, 1)],
    [(0, 75, 1), (1, 72, 1), (2, 69, 2)],
    [(0, 70, 1), (1, 67, 1), (2, 72, 1), (3, 70, 1)],
    [(0, 69, 2), (2, 65, 1), (3, 62, 1)],
    [(0, 70, 1), (1, 72, .5), (1.5, 75, 1.5), (3, 72, 1)],
    [(0, 68, 1), (1, 70, 1), (2, 72, 2)],
    [(0, 74, 1.5), (1.5, 72, .5), (2, 70, 1), (3, 67, 1)],
    [(0, 68, 1.5), (1.5, 70, .5), (2, 72, 1), (3, 74, 1)],
    [(0, 75, 2), (2, 77, 1), (3, 75, 1)],
    [(0, 71, 2), (2, 68, 1), (3, 65, 1)],
    [(0, 67, 1), (1, 70, 1), (2, 75, 1.5), (3.5, 72, .5)],
    [(0, 70, 3)],
]


def halves(bar):
    c = FORM[bar % BARS]
    return (c, c) if isinstance(c, str) else c


def ch_at(bar, beat):
    return CH[halves(bar)[0 if beat < 2 else 1]]


def sw(bar, beat, key, beats, vel=100):
    return note(bar, beat, key, beats, vel, swung=True)


def melody(shift=0, vel=95):
    return [sw(bar, b, k + shift, d, vel) for bar, ns in enumerate(MELODY) for b, k, d in ns]


def walking_bass():
    out = []
    for bar in range(BARS):
        first, second = halves(bar)
        nxt = CH[halves(bar + 1)[0]][0]
        for beat in range(4):
            root, q, _ = CH[first if beat < 2 else second]
            third = 3 if q in ("min", "dim") else 4
            if first != second:
                k = [root, root + 7, root, None][beat]
            else:
                k = [root, root + third, root + 7, None][beat]
            if k is None:
                k = nxt - 1 if nxt - 1 >= 33 else nxt + 1
            out.append(sw(bar, beat, k, .9, 95 if beat % 2 == 0 else 85))
    return out


def comp(vel=70):  # Charleston: beat 1 and the and-of-2
    return [sw(bar, b, k, .6, vel) for bar in range(BARS) for b in (0, 1.5) for k in ch_at(bar, 2 if b > 1 else 0)[2]]


def sustained(shift=0, vel=70):
    out = []
    for bar in range(BARS):
        first, second = halves(bar)
        if first == second:
            out += [sw(bar, 0, k + shift, 3.9, vel) for k in CH[first][2]]
        else:
            out += [sw(bar, 0, k + shift, 1.9, vel) for k in CH[first][2]]
            out += [sw(bar, 2, k + shift, 1.9, vel) for k in CH[second][2]]
    return out


def harp():  # glamorous upward run through the chord every bar
    out = []
    for bar in range(BARS):
        v = ch_at(bar, 0)[2]
        run = [k + o for o in (0, 12) for k in v]
        out += [note(bar, i * .25, k, 1.5, 70) for i, k in enumerate(run[:8])]
    return out


def stabs(vel=105):
    return [sw(bar, b, k + 12, .3, vel) for bar in range(BARS) for b in (1.5, 3) for k in ch_at(bar, b)[2]]


RIDE_BEATS = [0, 1, 1.5, 2, 3, 3.5]


def drum(key, beats, vel, bars=range(BARS)):
    return [sw(bar, b, key, .25, vel) for bar in bars for b in beats]


TRACKS = [
    ("Bass", (ACOUSTIC_BASS, 0), walking_bass),
    ("Ride [main shop boss]", (JAZZ_KIT, 128), lambda: drum(RIDE, RIDE_BEATS, 75)),
    ("Hi-hat foot [main shop boss]", (JAZZ_KIT, 128), lambda: drum(PEDAL_HH, [1, 3], 70)),
    ("Kick [main shop boss]", (JAZZ_KIT, 128), lambda: drum(KICK, range(4), 45)),
    ("Snaps [main shop]", (JAZZ_KIT, 128), lambda: drum(STICK, [1, 3], 80)),
    ("Muted trumpet [main]", (MUTED_TRUMPET, 0), melody),
    ("Vibes comp [main packs]", (VIBES, 0), comp),
    ("Organ [packs]", (ORGAN, 0), lambda: sustained(0, 60)),
    ("Vibes melody [packs]", (VIBES, 0), lambda: melody(0, 90)),
    ("Strings [planet boss]", (STRINGS, 0), lambda: sustained(12, 70)),
    ("Harp [planet]", (HARP, 0), harp),
    ("Organ melody [shop]", (ORGAN, 0), lambda: melody(0, 90)),
    ("Cocktail piano [shop boss]", (PIANO, 0), comp),
    ("Trumpets [boss]", (TRUMPET, 0), lambda: melody(0, 110)),
    ("Trombones [boss]", (TROMBONE, 0), lambda: melody(-12, 110)),
    ("Brass stabs [boss]", (BRASS, 0), stabs),
    ("Snare [boss]", (JAZZ_KIT, 128), lambda: drum(SNARE, [1, 3], 85)),
    ("Crash [boss]", (JAZZ_KIT, 128), lambda: drum(CRASH, [0], 95, bars=[0, 8])),
]

if __name__ == "__main__":
    main(TRACKS, BPM, BARS)
