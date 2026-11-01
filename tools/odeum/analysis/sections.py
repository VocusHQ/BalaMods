"""Per-section check of a Crescendo render: loudness, 2-4 kHz vs total, brightness, and bar-by-bar loudness
inside a range (to see a build). Usage: python sections.py FILE "name:first-last,..." [build_first-build_last]"""
import sys, numpy as np, librosa, scipy.signal as ss
y, sr = librosa.load(sys.argv[1], sr=22050)
fps = sr / 512; cen = librosa.feature.spectral_centroid(y=y, sr=sr)[0]; B = 2.8
db = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
print(f"length {len(y)/sr:.1f}s")
for part in sys.argv[2].split(","):
    name, rng = part.split(":"); s, e = map(int, rng.split("-"))
    seg = y[int((s - 1) * B * sr):int(e * B * sr)]
    hi = ss.sosfiltfilt(ss.butter(4, [2000, 4000], btype='band', fs=sr, output='sos'), seg)
    print(f"{name:6s} bars {s:2d}-{e:2d}: level {db(seg):6.1f} dB  2-4k {db(hi)-db(seg):6.1f} (original -18)  centroid {cen[int((s-1)*B*fps):int(e*B*fps)].mean():5.0f}Hz")
if len(sys.argv) > 3:
    s, e = map(int, sys.argv[3].split("-"))
    print("bar loudness:", " ".join(f"{b}:{db(y[int((b-1)*B*sr):int(b*B*sr)]):.1f}" for b in range(s, e + 1)))
