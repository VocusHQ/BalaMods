# Draft generators

Python scripts that wrote the first LMMS drafts of each pack (MuseScore_General SoundFont).
The `.mmp` files in `music/` are the real source once someone edits them in LMMS; these
scripts only regenerate a draft from scratch.

| Script | Pack | Draft |
|---|---|---|
| `draft_crescendo4.py` | Crescendo | v4 electro swing (current) |
| `draft_crescendo3.py` | Crescendo | v3 Basie-style big band (also holds `sf2`/`swing` helpers v4 imports) |
| `draft_vesper.py` | Vesper | v1 bossa nova + lounge |
| `draft_basilicus.py` | Basilicus | v1 Las Vegas casino swing |
| `lmmsgen.py` | | shared: SoundFont instrument XML, swing timing, project builder |
| `balance.py` | | sets track volumes from per-track loudness targets |

Workflow for one pack (example: vesper):
```
python tools/odeum/drafts/draft_vesper.py music/vesper/vesper.mmp
"C:/Program Files/LMMS/lmms.exe" rendertracks music/vesper/vesper.mmp -f wav -a -o <tmp dir>
python tools/odeum/drafts/balance.py <tmp dir> tools/odeum/drafts/targets_vesper.json <current vols.json> tools/odeum/drafts/vols_vesper.json
python tools/odeum/drafts/draft_vesper.py music/vesper/vesper.mmp tools/odeum/drafts/vols_vesper.json
python tools/odeum/render_pack.py music/vesper/vesper.mmp
```
Needs `music/soundfonts/MuseScore_General.sf2` (not in git, 216 MB, MIT):
https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf2
