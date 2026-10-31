"""Vesper v1: bossa nova + late-night lounge blend. C major, 108 BPM, 16-bar loop, straight eighths."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403

BPM, BARS = 108, 16

CH = {  # bass root, voicing
    "Dm9": (38, [53, 57, 60, 64]), "G13": (43, [53, 59, 64]), "Cmaj9": (36, [52, 55, 59, 62]),
    "Am7": (45, [55, 60, 64]), "G7b9": (43, [53, 56, 59]), "C6": (36, [52, 55, 57, 60]),
    "Fmaj7": (41, [53, 57, 60, 64]), "Fm6": (41, [53, 56, 60, 62]), "Em7": (40, [55, 59, 62]),
    "A7b9": (45, [55, 58, 61]),
}
FORM = ["Dm9", "G13", "Cmaj9", "Am7", "Dm9", "G7b9", "Cmaj9", "C6",
        "Fmaj7", "Fm6", "Em7", "A7b9", "Dm9", "G13", "Cmaj9", "A7b9"]
MELODY = [
    [(0, 69, 1.5), (1.5, 72, .5), (2, 76, 2)],
    [(0, 74, 1.5), (1.5, 71, .5), (2, 69, 2)],
    [(0, 71, 3), (3, 67, 1)],
    [(0, 69, 1), (1, 72, 1), (2, 76, 2)],
    [(0, 76, 1.5), (1.5, 74, .5), (2, 72, 1), (3, 69, 1)],
    [(0, 68, 2), (2, 71, 1), (3, 74, 1)],
    [(0, 72, 1.5), (1.5, 71, .5), (2, 67, 2)],
    [(0, 69, 3.5)],
    [(0, 72, 1.5), (1.5, 76, .5), (2, 72, 1), (3, 69, 1)],
    [(0, 68, 2), (2, 72, 1), (3, 74, 1)],
    [(0, 74, 1.5), (1.5, 71, .5), (2, 67, 2)],
    [(0, 70, 1), (1, 73, 1), (2, 76, 1.5), (3.5, 73, .5)],
    [(0, 74, 1.5), (1.5, 72, .5), (2, 69, 2)],
    [(0, 71, 1), (1, 74, 1), (2, 76, 2)],
    [(0, 74, 1), (1, 72, 1), (2, 71, 2)],
    [(0, 67, 1), (1, 70, 1), (2, 73, 2)],
]


def ch(bar):
    return CH[FORM[bar % BARS]]


def melody(shift=0, vel=95):
    return [note(bar, b, k + shift, d, vel) for bar, ns in enumerate(MELODY) for b, k, d in ns]


def guitar():  # bossa comping: thumb on 1 and 3, chords on a 3-3-2 pattern over two bars
    out = []
    for bar in range(BARS):
        root, voicing = ch(bar)
        out += [note(bar, 0, root + 12, 1, 80), note(bar, 2, root + 19, 1, 75)]
        hits = (0, 1.5, 3) if bar % 2 == 0 else (1, 2.5)
        out += [note(bar, b, k, .5, 70) for b in hits for k in voicing]
    return out


def bass():  # two-beat bossa bass: root (and its pickup), fifth (and its pickup)
    out = []
    for bar in range(BARS):
        r = ch(bar)[0]
        out += [note(bar, 0, r, 1.5, 100), note(bar, 1.5, r, .5, 80), note(bar, 2, r + 7, 1.5, 95),
                note(bar, 3.5, r + 7, .5, 80)]
    return out


def rhodes(vel=65):
    return [note(bar, 0, k, 3.8, vel) for bar in range(BARS) for k in ch(bar)[1]]


def pad(shift=12, vel=70):
    return [note(bar, 0, k + shift, 3.9, vel) for bar in range(BARS) for k in ch(bar)[1][:3]]


def drum(key, beats, vel, bars=range(BARS)):
    return [note(bar, b, key, .25, vel) for bar in bars for b in beats]


def clave():  # rim click on a 3-2 bossa clave
    return [note(bar, b, STICK, .25, 85) for bar in range(BARS) for b in ((0, 1.5, 3) if bar % 2 == 0 else (1, 2.5))]


def congas():  # boss: busier percussion
    pattern = [(0, LOW_CONGA), (1, MUTE_CONGA), (1.5, OPEN_CONGA), (2, LOW_CONGA), (2.5, MUTE_CONGA),
               (3, OPEN_CONGA), (3.5, OPEN_CONGA)]
    return [note(bar, b, k, .25, 90) for bar in range(BARS) for b, k in pattern]


TRACKS = [
    ("Guitar", (NYLON_GUITAR, 0), guitar),
    ("Bass", (ACOUSTIC_BASS, 0), bass),
    ("Rim clave [main shop boss]", (BRUSH_KIT, 128), clave),
    ("Shaker [main shop boss]", (STANDARD_KIT, 128), lambda: drum(MARACAS, [b / 2 for b in range(8)], 70)),
    ("Kick [main shop boss]", (BRUSH_KIT, 128), lambda: drum(KICK, [0, 2], 70)),
    ("Tenor sax [main]", (TENOR, 0), melody),
    ("Rhodes [main shop]", (EPIANO, 0), rhodes),
    ("Vibes [packs]", (VIBES, 0), lambda: melody(0, 90)),
    ("Warm pad [packs planet]", (WARM_PAD, 0), pad),
    ("Flute [shop]", (FLUTE, 0), lambda: melody(0, 90)),
    ("Strings [planet boss]", (SLOW_STRINGS, 0), lambda: pad(0, 75)),
    ("Low sax [boss]", (TENOR, 0), lambda: melody(-12, 100)),
    ("Congas [boss]", (STANDARD_KIT, 128), congas),
]

if __name__ == "__main__":
    main(TRACKS, BPM, BARS)
