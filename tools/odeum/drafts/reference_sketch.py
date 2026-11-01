"""Plain reference sketch of the original Balatro theme's A section, as transcribed (music/ORIGINAL.md).

Two 4-bar cycles of 7/4 at 150 BPM: bass riff, pad chords, long lead notes. Simple sounds on purpose:
it exists only so Locked can check the transcription by ear against the game.
Usage: python reference_sketch.py OUT.mmp
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lmmsgen import *  # noqa: F401,F403

BPM, BEATS_PER_BAR, CYCLES = 150, 7, 2
BARS = 4 * CYCLES
LEAD_IN = 1  # beats of silence before bar 1

# MIDI keys
F1, Bb1, C2, Db2, Eb2, F2, Ab2, A2, Bb2, C3, Db3 = 29, 34, 36, 37, 39, 41, 44, 45, 46, 48, 49
Bb3, C4, Db4, Eb4, F4, Gb4, Ab4, A4, Bb4, C5, Db5, F5 = 58, 60, 61, 63, 65, 66, 68, 69, 70, 72, 73, 77

# per bar of the cycle: (beat, key, length)
BASS = [
    [(0, Eb2, .5), (1.5, F1, 3), (4.5, F2, .5), (5, A2, .5), (5.5, Eb2, .5), (6, C2, .5), (6.5, F2, .5)],  # F7
    [(0, Db2, 3), (3.5, Bb1, 1), (5, Eb2, 1), (6, Ab2, 1)],                                                 # Dbmaj7
    [(0, Bb1, 4.5), (5, Db3, .5), (5.5, Ab2, .5), (6, Eb2, 1)],                                             # Bbm
    [(.5, Eb2, 1), (1.5, Bb1, 2), (3.5, Eb2, 1), (4.75, Db3, .5), (5.25, C3, .5), (5.75, Bb2, .5), (6.25, F2, .75)],  # Ebm7
]
PAD = [[Eb4, F4, A4, C5], [Db4, F4, Ab4, C5], [Bb3, Db4, F4, Ab4], [Db4, Eb4, Gb4, Bb4]]
LEAD = [[(0, F5, 14)], [], [(0, C5, 7)], [(.5, Bb4, 6), (6.5, Db5, .5)]]  # F5 spans bars 1-2


def at(bar, beat):  # absolute beat -> lmmsgen note() in 4/4 terms
    b = LEAD_IN + bar * BEATS_PER_BAR + beat
    return 0, b


# The original swaps bar 2 (Dbmaj7) for a second Bbm bar on some passes (cycle 3 of the track = cycle 2 here)
ALT_BAR2 = {1}


def bar_of(table, c, i):
    return table[2] if i == 1 and c in ALT_BAR2 and table is not LEAD else table[i]


def notes_from(table, vel):
    out = []
    for c in range(CYCLES):
        for i in range(4):
            ns = bar_of(table, c, i)
            for beat, key, length in ns:
                out.append(note(*at(c * 4 + i, beat), key, length, vel))
    return out


def pad():
    return [note(*at(c * 4 + i, 0), k, BEATS_PER_BAR, 70) for c in range(CYCLES) for i in range(4) for k in bar_of(PAD, c, i)]


# Drums, measured from the drums stem (bars 5-20): kick 1, &2, &5, 6; snare 3 and 7 (3+4 feel); 8th hats, beats accented
KICK_AT, SNARE_AT = (0, 1.5, 4.5, 5), (2, 6)


def drums():
    out = []
    for bar in range(BARS):
        out += [note(*at(bar, b), KICK, .5, 110) for b in KICK_AT]
        out += [note(*at(bar, b), SNARE, .5, 100) for b in SNARE_AT]
        out += [note(*at(bar, h / 2), CLOSED_HH, .25, 85 if h % 2 == 0 else 55) for h in range(14)]
    return out


TRACKS = [
    ("Bass", (38, 0), lambda: notes_from(BASS, 105)),    # Synth Bass 1
    ("Pad", (WARM_PAD, 0), pad),
    ("Lead", (80, 0), lambda: notes_from(LEAD, 90)),      # Square Lead
    ("Drums", (STANDARD_KIT, 128), drums),
]

if __name__ == "__main__":
    total_beats = LEAD_IN + BARS * BEATS_PER_BAR + 4
    main(TRACKS, BPM, -(-total_beats // 4))
