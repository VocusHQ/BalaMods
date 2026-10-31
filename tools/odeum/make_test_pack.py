"""Generates the music of Odeum's placeholder pack (mods/Odeum/packs/testum):
five synced variants of one 16-second loop.

Only the Python standard library and ffmpeg are needed.
Usage: python tools/odeum/make_test_pack.py
"""
import math
import random
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

RATE = 32000
BPM = 120
BEAT = 60 / BPM
BARS = 8
LENGTH = int(RATE * BEAT * 4 * BARS)  # exactly 16 s, identical for every variant

# A minor - F - C - G, twice. Each chord is MIDI notes (root first).
CHORDS = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]] * 2
MELODY = [76, 72, 69, 72, 77, 76, 72, 69, 76, 79, 76, 72, 74, 71, 67, 71]  # one note per half bar

PACK = Path(__file__).resolve().parents[2] / "mods" / "Odeum" / "packs" / "testum"


def freq(note):
    return 440.0 * 2 ** ((note - 69) / 12)


def add(buf, start, samples):
    """Mixes samples into buf, wrapping past the end so the loop is seamless."""
    start = int(start * RATE)
    for i, s in enumerate(samples):
        buf[(start + i) % LENGTH] += s


def tone(note, dur, vol, decay, harmonics=(1.0,), attack=0.005):
    f = freq(note)
    n = int(dur * RATE)
    a = int(attack * RATE) or 1
    out = []
    for i in range(n):
        t = i / RATE
        env = min(1.0, i / a) * math.exp(-t * decay)
        s = sum(h * math.sin(2 * math.pi * f * (k + 1) * t) for k, h in enumerate(harmonics))
        out.append(vol * env * s)
    return out


def bell(note, dur, vol):
    f = freq(note)
    return [vol * math.exp(-i / RATE * 3) * (math.sin(2 * math.pi * f * i / RATE)
            + 0.4 * math.sin(2 * math.pi * f * 2.76 * i / RATE)) for i in range(int(dur * RATE))]


def kick(vol):
    out = []
    phase = 0.0
    for i in range(int(0.35 * RATE)):
        t = i / RATE
        phase += 2 * math.pi * (45 + 90 * math.exp(-t * 30)) / RATE
        out.append(vol * math.exp(-t * 9) * math.sin(phase))
    return out


def hat(vol, rng):
    return [vol * math.exp(-i / RATE * 60) * rng.uniform(-1, 1) for i in range(int(0.08 * RATE))]


def base_layers():
    buf = [0.0] * LENGTH
    for bar, chord in enumerate(CHORDS):
        t0 = bar * 4 * BEAT
        for e in range(8):  # bass: eighth notes on the root
            add(buf, t0 + e * BEAT / 2, tone(chord[0] - 24, BEAT / 2, 0.30, 6, (1, 0.5, 0.25)))
        arp = chord + [chord[0] + 12]
        for e in range(8):  # arpeggio up and down
            note = arp[[0, 1, 2, 3, 2, 1, 0, 1][e]]
            add(buf, t0 + e * BEAT / 2, tone(note, BEAT, 0.14, 7, (1, 0.3)))
    return buf


def variant(slot):
    buf = base_layers()
    rng = random.Random(slot)
    for bar, chord in enumerate(CHORDS):
        t0 = bar * 4 * BEAT
        if slot == 1:  # main: light hats
            for e in range(8):
                add(buf, t0 + e * BEAT / 2, hat(0.05 if e % 2 else 0.08, rng))
        elif slot == 2:  # tarot pack: bell melody
            for h in range(2):
                add(buf, t0 + h * 2 * BEAT, bell(MELODY[bar * 2 + h], 2 * BEAT, 0.12))
        elif slot == 3:  # planet pack: slow airy pad
            for note in chord:
                add(buf, t0, tone(note + 12, 4 * BEAT, 0.05, 0.4, (1, 0.2), attack=0.6))
                add(buf, t0, tone(note + 12.08, 4 * BEAT, 0.04, 0.4, (1,), attack=0.6))
        elif slot == 4:  # shop: offbeat organ stabs
            for b in range(4):
                for note in chord:
                    add(buf, t0 + (b + 0.5) * BEAT, tone(note + 12, BEAT / 3, 0.06, 5, (1, 0.5, 0.3)))
        elif slot == 5:  # boss: kick on every beat + low drone
            for b in range(4):
                add(buf, t0 + b * BEAT, kick(0.45))
            add(buf, t0, tone(chord[0] - 36, 4 * BEAT, 0.18, 0.2, (1, 0.6, 0.4, 0.3), attack=0.05))
    return buf


def write_wav(path, buf):
    peak = max(abs(s) for s in buf) or 1.0
    scale = 0.8 * 32767 / peak
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(int(s * scale).to_bytes(2, "little", signed=True) for s in buf))


def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def main():
    (PACK / "music").mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    try:
        for slot in range(1, 6):
            wav = tmp / f"music{slot}.wav"
            write_wav(wav, variant(slot))
            ffmpeg("-i", str(wav), "-c:a", "libvorbis", "-q:a", "5", str(PACK / "music" / f"music{slot}.ogg"))
            print(f"music{slot}.ogg")
    finally:
        shutil.rmtree(tmp)
    print("Logo: python tools/odeum/make_title.py --pack mods/Odeum/packs/testum")


if __name__ == "__main__":
    main()
