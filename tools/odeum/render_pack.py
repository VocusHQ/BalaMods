"""Renders an LMMS project into the five synced music tracks of an Odeum pack.

Which game variant a track plays in is set by a tag at the end of its name in LMMS:
    "Kick [shop boss]"   -> only in the shop and boss variants
    "Bass"               -> no tag: plays in every variant
Tags: main, packs, planet, shop, boss (or 1-5). Tracks muted in LMMS stay muted.

The loop is the LMMS loop range (the green bar above the song editor); it must start
at bar 1. Anything that rings past the loop end (reverb, long notes) is wrapped back
onto the start, so the music loops without a click or gap. All five variants get the
same gain, so their volumes stay balanced against each other.

Usage:
  python tools/odeum/render_pack.py music/crescendo/crescendo.mmp
  python tools/odeum/render_pack.py music/crescendo/crescendo.mmp --pack crescendo --only main
"""
import argparse
import array
import copy
import re
import subprocess
import sys
import zlib
import xml.etree.ElementTree as ET
from pathlib import Path

LMMS = Path("C:/Program Files/LMMS/lmms.exe")
ROOT = Path(__file__).resolve().parents[2]
PACKS = ROOT / "mods" / "Odeum" / "packs"
RATE = 44100
PEAK = 0.7  # -3 dBFS: leaves room for .ogg encoding overshoot on drum hits
LEAD_IN = 192  # ticks (one bar) of silence rendered first and cut, so instrument start-up clicks fall outside the loop
MOVABLE = ("pattern", "bbtco", "automationpattern", "sampletco")

SLOTS = {"main": 1, "packs": 2, "planet": 3, "shop": 4, "boss": 5}
ALIASES = {"tarot": 2, "arcana": 2, "spectral": 2, "celestial": 3}
TAG = re.compile(r"\[([^\]]*)\]\s*$")


def load_project(path):
    data = path.read_bytes()
    if path.suffix == ".mmpz":  # Qt qCompress: 4-byte length, then zlib
        data = zlib.decompress(data[4:])
    return ET.ElementTree(ET.fromstring(data))


def track_slots(name):
    """Slots a track plays in, from the [tag] at the end of its name."""
    m = TAG.search(name or "")
    if not m:
        return set(SLOTS.values())
    slots = set()
    for word in re.split(r"[\s,]+", m.group(1).strip().lower()):
        if not word:
            continue
        slot = SLOTS.get(word) or ALIASES.get(word) or (int(word) if word.isdigit() and 1 <= int(word) <= 5 else None)
        if slot is None:
            sys.exit(f"Unknown tag '{word}' in track '{name}'. Use: {', '.join(SLOTS)}")
        slots.add(slot)
    return slots


def song_tracks(tree):
    container = tree.getroot().find("song/trackcontainer")
    return [t for t in container.findall("track") if t.get("type") in ("0", "1", "2")]  # instrument, beat, sample


def loop_frames(tree):
    head = tree.getroot().find("head")
    bpm = float(head.get("bpm"))
    timeline = tree.getroot().find("song/timeline")
    start, end = int(timeline.get("lp0pos", 0)), int(timeline.get("lp1pos", 0))
    if start != 0 or end <= 0:
        sys.exit("Set the LMMS loop range to start at bar 1 and end where the song loops.")
    seconds = end / 48 * 60 / bpm  # LMMS: 48 ticks per quarter note
    return round(seconds * RATE), seconds, bpm


def lead_in_frames(bpm):
    return round(LEAD_IN / 48 * 60 / bpm * RATE)


def render(tree, project, slot, out_wav):
    variant = copy.deepcopy(tree)
    for track in song_tracks(variant):
        if slot not in track_slots(track.get("name")):
            track.set("muted", "1")
        track.set("solo", "0")
    for el in variant.getroot().find("song").iter():
        if el.tag in MOVABLE and el.get("pos") is not None:
            el.set("pos", str(int(el.get("pos")) + LEAD_IN))
    tmp = project.with_name(f".render_{project.stem}_{slot}.mmp")  # next to the project so relative paths work
    variant.write(tmp, encoding="utf-8", xml_declaration=True)
    try:
        subprocess.run([str(LMMS), "render", str(tmp), "-f", "wav", "-a", "-s", str(RATE), "-o", str(out_wav)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    finally:
        tmp.unlink(missing_ok=True)


def read_wav(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(RATE), "-"],
                         check=True, capture_output=True).stdout
    return array.array("f", raw)


def fold(samples, frames):
    """Wraps everything past the loop end back onto the start."""
    n = frames * 2
    out = array.array("f", samples[:n])
    out.extend([0.0] * (n - len(out)))
    for i in range(n, len(samples)):
        out[i % n] += samples[i]
    return out


def write_ogg(samples, gain, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = array.array("f", (s * gain for s in samples)).tobytes()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(RATE), "-ac", "2", "-i", "-",
                    "-c:a", "libvorbis", "-q:a", "6", str(path)], input=data, check=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project", type=Path, help=".mmp or .mmpz LMMS project")
    ap.add_argument("--pack", help="pack id (default: the project's file name)")
    ap.add_argument("--only", choices=list(SLOTS), help="render just one variant (quick check)")
    args = ap.parse_args()

    project = args.project.resolve()
    pack = args.pack or project.stem
    tree = load_project(project)
    frames, seconds, bpm = loop_frames(tree)
    print(f"{project.name}: {bpm:g} BPM, loop {seconds:.2f} s -> packs/{pack}/music")

    for track in song_tracks(tree):
        names = [k for k, v in SLOTS.items() if v in track_slots(track.get("name"))]
        state = " (muted)" if track.get("muted") == "1" else ""
        print(f"  {track.get('name'):<28} {' '.join(names)}{state}")

    slots = {SLOTS[args.only]: args.only} if args.only else {v: k for k, v in SLOTS.items()}
    tmp_dir = project.parent / ".render"
    tmp_dir.mkdir(exist_ok=True)
    mixes = {}
    try:
        for slot, name in slots.items():
            print(f"rendering music{slot} ({name})...", flush=True)
            wav = tmp_dir / f"music{slot}.wav"
            render(tree, project, slot, wav)
            mixes[slot] = fold(read_wav(wav)[lead_in_frames(bpm) * 2:], frames)
            wav.unlink()
    finally:
        try:
            tmp_dir.rmdir()
        except OSError:
            pass

    peak = max(max(abs(s) for s in m) for m in mixes.values()) or 1.0
    gain = PEAK / peak
    for slot, mix in mixes.items():
        write_ogg(mix, gain, PACKS / pack / "music" / f"music{slot}.ogg")
    print(f"done: gain {gain:.2f}, {len(mixes)} track(s) written")


if __name__ == "__main__":
    main()
