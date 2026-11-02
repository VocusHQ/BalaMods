# Odeum music scripts

Every Odeum soundtrack is written as Python: each module lists its tracks as notes for the
MuseScore_General SoundFont, which LMMS renders track by track. `reference_render.py` mixes a
module into an mp3 for listening, and `export_pack.py` writes the five game versions into a pack.

| File | What it is |
|---|---|
| `lmmsgen.py` | shared: SoundFont instrument XML, note timing, LMMS project builder |
| `reference_render.py` | renders a module to an mp3 (per-track gain, Balatro-style pitch wobble, low-pass) |
| `export_pack.py` | renders all five versions of a pack, loops them seamlessly, matches Balatro's loudness, writes `music1-5.ogg` |
| `reference_full.py` | transcription of the original Balatro theme (62 bars), see `music/ORIGINAL.md` |
| `crescendo_garage.py` | **Crescendo** main (blinds): Bolero-style orchestra + live drummer, 7/4 |
| `crescendo_versions.py` | **Crescendo** shop, packs, planet and boss (`VERSION=`) |
| `crescendo_main*.py`, `crescendo_bolero.py`, `crescendo_samples.py` | earlier Crescendo steps; the two files above import their form, tunes and voicings |
| `vesper.py` | **Vesper**: spaghetti-western ride, 4/4 triplet shuffle, all five versions (`VERSION=main\|shop\|packs\|planet\|boss`) |

```
# listen to one version
VERSION=boss python tools/odeum/drafts/reference_render.py "music/vesper/sketches/vesper boss.mp3" vesper
# export a pack into the mod (BALATRO_MUSIC = folder with the game's own music1-5.ogg, for loudness)
BALATRO_MUSIC=<folder> python tools/odeum/drafts/export_pack.py vesper
# high-frequency check (no piercing highs, ever): compare with the original
python tools/odeum/analysis/highs.py "music/vesper/sketches/vesper main.mp3" "music/reference/2 - original (same 8 bars).mp3"
```

Needs LMMS 1.2.2 (`C:/Program Files/LMMS/lmms.exe`), ffmpeg, numpy and scipy, and
`music/soundfonts/MuseScore_General.sf2` (not in git, 216 MB, MIT):
https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf2
