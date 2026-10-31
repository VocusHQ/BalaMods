"""Computes track volumes from a `lmms rendertracks` folder so each track hits its target loudness.
Usage: python balance.py TRACKS_DIR TARGETS.json CURRENT_VOLS.json OUT_VOLS.json
TARGETS: {track name: mean dB}. Volumes are capped at 200 (LMMS max); the whole set shifts together.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

tracks, targets, current, out = Path(sys.argv[1]), *map(lambda p: json.loads(Path(p).read_text()), sys.argv[2:4]), Path(sys.argv[4])
mean = {}
for wav in tracks.glob("*.wav"):
    name = re.sub(r"^\d+_", "", wav.stem)
    log = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", "volumedetect", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"mean_volume: (-?[\d.]+) dB", log)
    mean[name] = float(m.group(1)) if m else -120.0
delta = {n: targets[n] - mean[n] for n in targets}
# shift so the loudest required boost still fits under 200
shift = max(20 * math.log10(current[n] * 10 ** (d / 20) / 200) for n, d in delta.items())
shift = max(shift, 0)
vols = {n: max(1, round(current[n] * 10 ** ((d - shift) / 20))) for n, d in delta.items()}
for n in targets:
    print(f"{n:<30} {mean[n]:7.1f} dB -> vol {current[n]:>3} => {vols[n]:>3}")
out.write_text(json.dumps(vols, indent=1))
