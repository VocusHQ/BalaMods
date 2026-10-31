"""Crescendo v4: electro swing (Caravan Palace / Parov Stelar style), MuseScore_General SoundFont.
G minor swing, 124 BPM, 16-bar loop, swung eighths over a four-on-the-floor kick.
Usage: python draft_crescendo4.py OUT.mmp
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from draft_crescendo3 import sf2, swing, BEAT, BAR  # SoundFont instrument builder, swing timing

BPM = 124
BARS = 16

CH = {  # root, voicing
    "Gm6": (43, [55, 58, 62, 64]),
    "Cm6": (36, [55, 60, 63, 69]),
    "D7": (38, [54, 57, 60, 62]),
    "Eb7": (39, [55, 58, 61, 63]),
}
FORM = ["Gm6", "Gm6", "Cm6", "Cm6", "D7", "D7", "Gm6", "Gm6",
        "Cm6", "Cm6", "Gm6", "Gm6", "Eb7", "D7", "Gm6", "D7"]

MELODY = [  # one list per bar: (beat, key, length in beats)
    [(.5, 62, .5), (1, 67, .5), (1.5, 70, .5), (2, 74, 1), (3, 70, .5), (3.5, 69, .5)],
    [(0, 67, 1.5), (2.5, 64, .5), (3, 67, .5), (3.5, 70, .5)],
    [(0, 72, 1), (1, 75, .5), (1.5, 72, .5), (2, 69, 1), (3, 67, .5), (3.5, 63, .5)],
    [(0, 67, 2), (2.5, 69, .5), (3, 72, .5), (3.5, 69, .5)],
    [(0, 66, .5), (.5, 69, .5), (1, 72, 1), (2, 74, .5), (2.5, 72, .5), (3, 69, .5), (3.5, 66, .5)],
    [(0, 62, 1), (1, 66, .5), (1.5, 69, .5), (2, 72, 1.5), (3.5, 70, .5)],
    [(0, 67, .5), (.5, 70, .5), (1, 74, 1), (2, 72, .5), (2.5, 70, .5), (3, 69, .5), (3.5, 64, .5)],
    [(0, 67, 2)],
    [(0, 75, 1), (1, 74, .5), (1.5, 72, .5), (2, 69, 1), (3, 72, 1)],
    [(0, 63, .5), (.5, 67, .5), (1, 72, .5), (1.5, 75, .5), (2, 74, 2)],
    [(0, 74, 1), (1, 70, .5), (1.5, 67, .5), (2, 64, 1), (3, 67, 1)],
    [(0, 62, .5), (.5, 67, .5), (1, 70, .5), (1.5, 74, .5), (2, 72, 2)],
    [(0, 70, 1), (1, 67, .5), (1.5, 73, .5), (2, 70, 1), (3, 67, .5), (3.5, 65, .5)],
    [(0, 66, 1), (1, 69, .5), (1.5, 72, .5), (2, 74, 1), (3, 72, .5), (3.5, 69, .5)],
    [(0, 67, 1), (1, 70, 1), (2, 67, 1), (3, 62, 1)],
    [(0, 66, .5), (.5, 69, .5), (1, 72, .5), (1.5, 74, .5), (2, 72, .5), (2.5, 69, .5), (3, 66, .5), (3.5, 62, .5)],
]


def ch(bar):
    return CH[FORM[bar % BARS]]


def note(bar, beat, key, beats, vel=100):
    return (bar * BAR + swing(beat), key, max(10, int(beats * BEAT) - 8), vel)


def melody(shift=0, vel=100):
    return [note(bar, b, k + shift, d, vel) for bar, notes in enumerate(MELODY) for b, k, d in notes]


def pompe(vel=80):  # gypsy-jazz rhythm guitar: chord on every beat, short and accented on 2 and 4
    out = []
    for bar in range(BARS):
        for beat in range(4):
            accent = beat % 2 == 1
            for k in ch(bar)[1]:
                out.append((bar * BAR + beat * BEAT, k, 10 if accent else 20, vel + (15 if accent else 0)))
    return out


def upright():  # oom-pah: root on 1, fifth on 3, pickup on 4
    out = []
    for bar in range(BARS):
        root = ch(bar)[0]
        out += [note(bar, 0, root, .8, 100), note(bar, 2, root + 7, .8, 95), note(bar, 3.5, root + 12, .4, 80)]
    return out


def synth_bass():  # offbeat bass: the electro "pump"
    return [note(bar, b + .5, ch(bar)[0], .4, 100) for bar in range(BARS) for b in range(4)]


def stabs(vel=100):  # short brass hits on the offbeats of 2 and 4
    return [note(bar, b, k, .3, vel) for bar in range(BARS) for b in (1.5, 3.5) for k in ch(bar)[1]]


def pads(vel=70):
    return [(bar * BAR, k + 12, BAR - 6, vel) for bar in range(BARS) for k in ch(bar)[1][:3]]


def vibes(vel=70):
    return [(bar * BAR + b * BEAT, ch(bar)[1][b % 4] + 12, 40, vel) for bar in range(BARS) for b in range(4)]


KICK, CLAP, CLOSED_HH, OPEN_HH, CRASH = 36, 39, 42, 46, 49


def hits(key, beats, vel, bars=range(BARS)):
    return [note(bar, b, key, .25, vel) for bar in bars for b in beats]


EIGHTHS = [b / 2 for b in range(8)]
OFFBEATS = [b + .5 for b in range(4)]

PIANO, VIBES_P, ACOUSTIC_BASS, SYNTH_BASS = 0, 11, 32, 38
STEEL_GUITAR, STRINGS, TRUMPET, MUTED_TRUMPET, BRASS, ALTO, CLARINET = 25, 49, 56, 59, 61, 65, 71
STANDARD_KIT = 0

TRACKS = [  # name, (patch, bank), notes, volume
    ("Upright bass", (ACOUSTIC_BASS, 0), upright, 60),
    ("Guitar", (STEEL_GUITAR, 0), pompe, 60),
    ("Kick [main shop boss]", (STANDARD_KIT, 128), lambda: hits(KICK, range(4), 110), 60),
    ("Clap [main boss]", (STANDARD_KIT, 128), lambda: hits(CLAP, [1, 3], 100), 60),
    ("Hats [main packs shop boss]", (STANDARD_KIT, 128), lambda: hits(CLOSED_HH, EIGHTHS, 80), 60),
    ("Open hat [boss]", (STANDARD_KIT, 128), lambda: hits(OPEN_HH, OFFBEATS, 80), 60),
    ("Clarinet [main boss]", (CLARINET, 0), melody, 60),
    ("Muted trumpet [packs]", (MUTED_TRUMPET, 0), lambda: melody(0, 90), 60),
    ("Piano melody [shop]", (PIANO, 0), lambda: melody(12, 85), 60),
    ("Vibes [packs planet]", (VIBES_P, 0), vibes, 60),
    ("Strings [planet]", (STRINGS, 0), pads, 60),
    ("Synth bass [boss]", (SYNTH_BASS, 0), synth_bass, 60),
    ("Trumpet [boss]", (TRUMPET, 0), lambda: melody(0, 105), 60),
    ("Alto sax [boss]", (ALTO, 0), lambda: melody(-12, 105), 60),
    ("Brass stabs [boss]", (BRASS, 0), stabs, 60),
    ("Crash [boss]", (STANDARD_KIT, 128), lambda: hits(CRASH, [0], 100, bars=[0, 8]), 60),
]


def build(vols=None):
    vols = vols or {}
    proj = ET.Element("lmms-project", creator="LMMS", version="1.0", type="song", creatorversion="1.2.2")
    ET.SubElement(proj, "head", timesig_numerator="4", bpm=str(BPM), timesig_denominator="4", mastervol="100",
                  masterpitch="0")
    song = ET.SubElement(proj, "song")
    tc = ET.SubElement(song, "trackcontainer", type="song", x="5", y="5", width="900", height="420", visible="1",
                       maximized="0", minimized="0")
    for name, (patch, bank), notes, vol in TRACKS:
        tr = ET.SubElement(tc, "track", muted="0", name=name, solo="0", type="0")
        it = sf2(patch, bank)
        it.set("vol", str(vols.get(name, vol)))
        tr.append(it)
        pat = ET.SubElement(tr, "pattern", pos="0", len=str(BARS * BAR), muted="0", name=name.split(" [")[0],
                            steps="16", type="1")
        for pos, key, length, vel in sorted(notes()):
            ET.SubElement(pat, "note", pos=str(pos), key=str(key), len=str(length), vol=str(vel), pan="0")
    fx = ET.SubElement(song, "fxmixer", x="1", y="463", width="530", height="332", visible="0", maximized="0",
                       minimized="0")
    c = ET.SubElement(fx, "fxchannel", num="0", name="Master", volume="1", muted="0", soloed="0")
    ET.SubElement(c, "fxchain", enabled="0", numofeffects="0")
    ET.SubElement(song, "timeline", lp0pos="0", lp1pos=str(BARS * BAR), lpstate="1")
    ET.SubElement(song, "controllers")
    return ET.ElementTree(proj)


if __name__ == "__main__":
    import json
    out = Path(sys.argv[1])
    vols = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else {}
    out.parent.mkdir(parents=True, exist_ok=True)
    tree = build(vols)
    ET.indent(tree)
    with open(out, "wb") as f:
        f.write(b'<?xml version="1.0"?>\n<!DOCTYPE lmms-project>\n')
        tree.write(f, encoding="utf-8")
    print(out)
