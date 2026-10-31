"""Crescendo v3: big band swing, built on the MuseScore_General SoundFont.
Bb jazz blues, 148 BPM, two 12-bar choruses (24-bar loop), swung eighths.
Usage: python draft_crescendo3.py OUT.mmp
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SF2 = "D:/Downloads/BalaMods/music/soundfonts/MuseScore_General.sf2"
BPM = 148
BEAT, BAR = 48, 192
CHORUS = 12
BARS = 2 * CHORUS

# chord: (bass root, quality, rootless voicing)
CH = {
    "Bb7": (34, "dom", [56, 62, 67]),
    "Eb7": (39, "dom", [55, 61, 65]),
    "Fm7": (41, "min", [56, 63, 67]),
    "Edim": (40, "dim", [55, 58, 61, 64]),
    "G7": (43, "dom", [53, 59, 64]),
    "Cm7": (36, "min", [51, 58, 62]),
    "F7": (41, "dom", [51, 57, 62]),
}
# each bar: chord, or (first half, second half)
FORM = ["Bb7", "Eb7", "Bb7", ("Fm7", "Bb7"), "Eb7", "Edim", "Bb7", "G7", "Cm7", "F7", ("Bb7", "G7"), ("Cm7", "F7")]


def halves(bar):
    c = FORM[bar % CHORUS]
    return (c, c) if isinstance(c, str) else c


def chord_at(bar, beat):
    return CH[halves(bar)[0 if beat < 2 else 1]]


def swing(beat):
    """Beat position (0.5 steps) -> ticks, with swung eighths (2:1 triplet feel)."""
    whole = int(beat)
    return whole * BEAT + (32 if beat - whole >= 0.5 else 0)


def phrase(start_bar, notes, shift=0, vel=100):
    out = []
    for b, key, dur in notes:
        pos = start_bar * BAR + swing(b)
        out.append((pos, key + shift, max(10, int(dur * BEAT) - 8), vel))
    return out


# The riff (two bars) and its variations
RIFF_A = [(0, 65, .5), (.5, 67, .5), (1, 70, 1), (2.5, 67, .5), (3, 70, .5), (4.5, 68, .5), (5, 67, .5), (5.5, 65, 1.5)]
RIFF_A2 = RIFF_A[:-1] + [(5.5, 70, 1.5)]  # chorus 2 ends up high
RIFF_C = [(0, 67, .5), (.5, 70, .5), (1, 72, 1), (2.5, 70, .5), (3, 67, .5), (4.5, 65, .5), (5, 63, .5), (5.5, 62, 1.5)]


def riffs(shift=0, vel=100):
    out = []
    for chorus in range(2):
        b = chorus * CHORUS
        out += phrase(b + 0, RIFF_A if chorus == 0 else RIFF_A2, shift, vel)
        out += phrase(b + 4, RIFF_A, shift + 5, vel)  # same riff up a fourth over Eb7
        out += phrase(b + 8, RIFF_C, shift, vel)
    return out


def walking_bass():
    out = []
    for bar in range(BARS):
        first, second = halves(bar)
        nxt = CH[halves(bar + 1)[0]][0]
        steps = []
        for beat in range(4):
            root, q, _ = CH[first if beat < 2 else second]
            third = 3 if q in ("min", "dim") else 4
            fifth = 6 if q == "dim" else 7
            if first != second:  # two chords: root, fifth | root, approach
                k = [root, root + fifth, root, None][beat]
            else:
                k = [root, root + (third if bar % 2 == 0 else fifth), root + (fifth if bar % 2 == 0 else 9), None][beat]
            if k is None:  # chromatic approach into the next bar's root
                k = nxt - 1 if (nxt - 1) >= 33 else nxt + 1
            steps.append(k)
        out += [(bar * BAR + i * BEAT, k, 40, 95 if i % 2 == 0 else 85) for i, k in enumerate(steps)]
    return out


def comping(vel=70):  # "Charleston": beat 1 and the and-of-2
    out = []
    for bar in range(BARS):
        for beat, length in ((0, 30), (1.5, 36)):
            for k in chord_at(bar, 2 if beat > 1 else 0)[2]:
                out.append((bar * BAR + swing(beat), k, length, vel))
    return out


def brass_hits(vel=95):  # answers in the bars where the saxes rest
    out = []
    for chorus in range(2):
        for bar in (2, 3, 6, 7, 10, 11):
            b = chorus * CHORUS + bar
            for beat in (1.5, 3):
                for k in chord_at(b, beat)[2]:
                    out.append((b * BAR + swing(beat), k, 18, vel))
    return out


def pads(vel=70):
    out = []
    for bar in range(BARS):
        first, second = halves(bar)
        if first == second:
            out += [(bar * BAR, k, BAR - 6, vel) for k in CH[first][2]]
        else:
            out += [(bar * BAR, k, 2 * BEAT - 4, vel) for k in CH[first][2]]
            out += [(bar * BAR + 2 * BEAT, k, 2 * BEAT - 6, vel) for k in CH[second][2]]
    return out


def vibes(vel=65):  # slow quarter-note arpeggio through the voicing
    out = []
    for bar in range(BARS):
        for beat in range(4):
            v = chord_at(bar, beat)[2]
            out.append((bar * BAR + beat * BEAT, v[beat % len(v)] + 12, 40, vel))
    return out


# GM drum keys
KICK, SNARE, STICK, PEDAL_HH, RIDE, CRASH = 36, 38, 37, 44, 51, 49


def drums(key, positions, vel, bars=range(BARS)):
    return [(bar * BAR + p, key, 24, vel) for bar in bars for p in positions]


RIDE_PATTERN = [0, 48, 80, 96, 144, 176]  # ding, ding-a, ding, ding-a


def ride(vel=70):
    return [(bar * BAR + p, RIDE, 24, vel + (10 if p in (48, 144) else 0)) for bar in range(BARS) for p in RIDE_PATTERN]


# --- instruments -------------------------------------------------------------

ENV = dict(latt="0", lamt="0", lspd_numerator="4", lspd_denominator="4", userwavefile="", ctlenvamt="0", lshp="0",
           x100="0", lpdel="0", lspd="0.1", pdel="0", syncmode="0", hold="0.5", att="0", dec="0.5", sustain="0.5",
           rel="0.1", amt="0")


def sf2(patch, bank=0):
    it = ET.Element("instrumenttrack", pitch="0", fxch="0", basenote="57", usemasterpitch="1", pitchrange="1",
                    vol="100", pan="0")
    inst = ET.SubElement(it, "instrument", name="sf2player")
    ET.SubElement(inst, "sf2player", src=SF2, bank=str(bank), patch=str(patch), gain="1",
                  reverbOn="1", reverbRoomSize="0.5", reverbDamping="0.4", reverbWidth="0.8", reverbLevel="0.35",
                  chorusOn="0", chorusNum="3", chorusLevel="2", chorusSpeed="0.3", chorusDepth="8")
    el = ET.SubElement(it, "eldata", ftype="0", fres="0.5", fcut="14000", fwet="0")
    for n in ("elvol", "elcut", "elres"):
        ET.SubElement(el, n, **ENV)
    ET.SubElement(it, "chordcreator", chord="0", chordrange="1", **{"chord-enabled": "0"})
    ET.SubElement(it, "arpeggiator", arp="0", arptime_numerator="4", arptime_denominator="4", arprange="1",
                  arpmode="0", arptime="100", arpdir="0", arpgate="100", syncmode="0", **{"arp-enabled": "0"})
    ET.SubElement(it, "fxchain", enabled="0", numofeffects="0")
    return it


PIANO, VIBES, ACOUSTIC_BASS, TRUMPET, TROMBONE, HORN, BRASS = 0, 11, 32, 56, 57, 60, 61
ALTO, TENOR, CLARINET = 65, 66, 71
JAZZ_KIT, BRUSH_KIT = 32, 40

# name, (patch, bank), notes, volume
TRACKS = [
    ("Bass", (ACOUSTIC_BASS, 0), walking_bass, 39),
    ("Piano", (PIANO, 0), comping, 43),
    ("Ride [main shop boss]", (JAZZ_KIT, 128), ride, 21),
    ("Hi-hat foot [main shop boss]", (JAZZ_KIT, 128), lambda: drums(PEDAL_HH, [48, 144], 70), 37),
    ("Kick [main shop boss]", (JAZZ_KIT, 128), lambda: drums(KICK, [0, 48, 96, 144], 45), 39),
    ("Brushes [packs planet]", (BRUSH_KIT, 128), lambda: drums(SNARE, RIDE_PATTERN, 45), 38),
    ("Alto sax [main boss]", (ALTO, 0), riffs, 62),
    ("Tenor sax [main boss]", (TENOR, 0), lambda: riffs(-12), 65),
    ("Brass hits [main boss]", (BRASS, 0), brass_hits, 44),
    ("Clarinet [packs]", (CLARINET, 0), lambda: riffs(0, 85), 141),
    ("Piano melody [shop]", (PIANO, 0), lambda: riffs(12, 80), 188),
    ("Horns [planet]", (HORN, 0), pads, 16),
    ("Vibes [planet packs]", (VIBES, 0), vibes, 165),
    ("Trumpets [boss]", (TRUMPET, 0), lambda: riffs(0, 110), 44),
    ("Trombones [boss]", (TROMBONE, 0), lambda: riffs(-12, 110), 23),
    ("Snare [boss]", (JAZZ_KIT, 128), lambda: drums(SNARE, [48, 144], 80), 31),
    ("Crash [boss]", (JAZZ_KIT, 128), lambda: drums(CRASH, [0], 90, bars=[0, CHORUS]), 45),
]


def build():
    proj = ET.Element("lmms-project", creator="LMMS", version="1.0", type="song", creatorversion="1.2.2")
    ET.SubElement(proj, "head", timesig_numerator="4", bpm=str(BPM), timesig_denominator="4", mastervol="100",
                  masterpitch="0")
    song = ET.SubElement(proj, "song")
    tc = ET.SubElement(song, "trackcontainer", type="song", x="5", y="5", width="900", height="420", visible="1",
                       maximized="0", minimized="0")
    for name, (patch, bank), notes, vol in TRACKS:
        tr = ET.SubElement(tc, "track", muted="0", name=name, solo="0", type="0")
        it = sf2(patch, bank)
        it.set("vol", str(vol))
        tr.append(it)
        pat = ET.SubElement(tr, "pattern", pos="0", len=str(BARS * BAR), muted="0", name=name.split(" [")[0],
                            steps="16", type="1")
        for pos, key, length, vel in sorted(notes()):
            ET.SubElement(pat, "note", pos=str(pos), key=str(key), len=str(length), vol=str(vel), pan="0")
    fx = ET.SubElement(song, "fxmixer", x="1", y="463", width="530", height="332", visible="0", maximized="0",
                       minimized="0")
    ch = ET.SubElement(fx, "fxchannel", num="0", name="Master", volume="1", muted="0", soloed="0")
    ET.SubElement(ch, "fxchain", enabled="0", numofeffects="0")
    ET.SubElement(song, "timeline", lp0pos="0", lp1pos=str(BARS * BAR), lpstate="1")
    ET.SubElement(song, "controllers")
    return ET.ElementTree(proj)


if __name__ == "__main__":
    out = Path(sys.argv[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    tree = build()
    ET.indent(tree)
    with open(out, "wb") as f:
        f.write(b'<?xml version="1.0"?>\n<!DOCTYPE lmms-project>\n')
        tree.write(f, encoding="utf-8")
    print(out)
