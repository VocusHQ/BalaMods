# Music projects

LMMS source projects for Odeum's soundtrack packs. One folder per pack:
`music/<pack>/<pack>.mmp` is exported into `mods/Odeum/packs/<pack>/music/`.

## Workflow
1. Open `music/<pack>/<pack>.mmp` in LMMS and edit it. Save.
2. Export the five game versions:
   ```
   python tools/odeum/render_pack.py music/<pack>/<pack>.mmp
   ```
3. Restart Balatro and pick the pack in Mods → Odeum → Config.

## One song, five versions
Every track plays in every version unless its name ends with a tag:

| Tag      | Version heard                                 |
|----------|-----------------------------------------------|
| `main`   | normal play                                   |
| `packs`  | Tarot, Spectral, Standard and Buffoon packs   |
| `planet` | Planet (Celestial) packs                      |
| `shop`   | the shop                                      |
| `boss`   | boss blinds                                   |

Example: rename a track to `Kick [shop boss]` (right-click the track name → Rename)
and it is only heard in the shop and on boss blinds.

- The **loop range** (green bar above the Song Editor) sets where the song loops. Keep
  it starting at bar 1. The export wraps anything ringing past the end back to the start.
- To quickly hear one version: `python tools/odeum/render_pack.py <project> --only shop`.
- Muting a track in LMMS mutes it in every version.
