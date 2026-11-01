"""Crescendo main v3 with a different drum part. DRUMS env picks the variant; everything else is v3.

All variants play Balatro's own beat (kick 1, &2, &5, 6; snare 3 and 7) instead of the Bolero snare roll,
and build the same way through the C section (denser hits, snare 8ths -> 16ths, every-beat kick, fill).
  balatro    standard kit: kick, snare, very soft hats (like the original)
  hands      congas and bongos on the Balatro beat, soft kick underneath for weight
  orchestral concert bass drum and concert snare on the Balatro beat
Render: DRUMS=hands python reference_render.py OUT.mp3 crescendo_drums
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403
import crescendo_main3 as v3  # noqa: E402
from crescendo_main3 import FORM, SEC, at, build_ramp, vel_of, first_bar  # noqa: E402

VARIANT = os.environ.get("DRUMS", "balatro")
BPM, BEATS_PER_BAR, LEAD_IN, BARS = v3.BPM, v3.BEATS_PER_BAR, v3.LEAD_IN, v3.BARS
KICKS, SNARES = (0, 1.5, 4.5, 5), (2, 6)
GHOSTS = tuple(e / 2 for e in range(14) if e / 2 not in KICKS + SNARES)
MUTE_HI_CONGA, OPEN_HI_CONGA, LOW_CONGA_K, HI_BONGO, LOW_BONGO = 62, 63, 64, 60, 61
LOW_TOM, MID_TOM, HIGH_TOM = 45, 47, 50
CONCERT_BD = 36

# per variant: (kick key, snare key, ghost key or None, kit program)
VOICES = {
    "balatro": (KICK, SNARE, CLOSED_HH, STANDARD_KIT),
    "hands": (LOW_CONGA_K, OPEN_HI_CONGA, MUTE_HI_CONGA, STANDARD_KIT),
    "orchestral": (CONCERT_BD, SNARE, None, 48),
}
KICK_KEY, SNARE_KEY, GHOST_KEY, KIT = VOICES[VARIANT]


def drums():
    out = []

    def hit(bar, beat, key, v, length=.5):
        out.append(note(*at(bar, beat), key, length, max(1, min(127, int(v)))))

    for bar, (r, (sec, i)) in enumerate(zip(FORM, SEC)):
        if r == "-":
            continue
        if sec == "intro":  # come in gently: kicks and ghosts only
            for b in KICKS:
                hit(bar, b, KICK_KEY, 60 + 12 * i)
            if GHOST_KEY:
                for b in GHOSTS:
                    hit(bar, b, GHOST_KEY, 25 + 6 * i, .25)
            continue
        if sec != "C":
            for b in KICKS:
                hit(bar, b, KICK_KEY, vel_of(bar, 108))
            for b in SNARES:
                hit(bar, b, SNARE_KEY, vel_of(bar, 100))
            if GHOST_KEY:
                for b in GHOSTS:
                    hit(bar, b, GHOST_KEY, vel_of(bar, 40 if VARIANT == "balatro" else 45), .25)
            if VARIANT == "hands" and sec in ("A2", "A3"):  # low bongo answers on the offbeats
                for b in (.5, 3.5, 6.5):
                    hit(bar, b, LOW_BONGO, vel_of(bar, 55), .25)
            continue
        # the build (6 bars): same beat, getting denser and louder
        for b in KICKS if i < 3 else range(7):  # every-beat kick from bar 4
            hit(bar, b, KICK_KEY, 60 + 60 * build_ramp(bar, b / 7))
        if i < 2:
            for b in SNARES:
                hit(bar, b, SNARE_KEY, 55 + 40 * build_ramp(bar, b / 7))
        else:
            step = .5 if i < 4 else .25  # snare 8ths, then 16ths
            for s in range(int(7 / step)):
                b = s * step
                if i == 5 and b >= 5:
                    break
                hit(bar, b, SNARE_KEY, (45 + 70 * build_ramp(bar, b / 7)) * (1.15 if b in SNARES else 1) * (.8 if VARIANT == "hands" else 1), .25)
        if GHOST_KEY and VARIANT != "balatro" and i >= 1:
            for b in GHOSTS:
                hit(bar, b, GHOST_KEY, 45 + 40 * build_ramp(bar, b / 7), .25)
        if VARIANT == "hands" and i >= 3:
            for b in (.5, 2.5, 3.5, 6.5):
                hit(bar, b, LOW_BONGO, 55 + 50 * build_ramp(bar, b / 7), .25)
        if i == 5:  # fill on the last two beats
            for j, tom in enumerate([HIGH_TOM, HIGH_TOM, MID_TOM, MID_TOM, LOW_TOM, LOW_TOM, LOW_TOM, LOW_TOM]):
                hit(bar, 5 + j / 4, tom, 95 + j * 4, .25)
    a3 = first_bar("A3")
    hit(a3, 0, KICK_KEY, 127, 1)
    hit(a3, 0, CONCERT_BD, 120, 1) if VARIANT != "orchestral" else None
    return out


TRACKS = [t if t[0] != "Drums" else ("Drums", (KIT, 128), drums) for t in v3.TRACKS]
TRACKS.append(("Landing", (48, 128), lambda: [note(*at(first_bar("A3"), 0), CONCERT_BD, 1, 120)]))
MIX = dict(v3.MIX, Drums=(1.0, 0, 0, 0, 0), Landing=(0.8, 0, 0, 0, 0))
LOWPASS = dict(v3.LOWPASS, Drums={"balatro": 4500, "hands": 1400, "orchestral": 6000}[VARIANT])  # no-highs rule
