# Odeum music brief

What each soundtrack pack sounds like, and the rules every pack follows.
Odeum is Locked's collection of tracks and sounds for Balatro.

## Rules for every pack
- **A version of the original Balatro theme**, not a new song: its chords and form (see
  `ORIGINAL.md`), taken in the pack's own direction. The tune may move freely around the
  original's lead notes (F, C, Bb).
- **150 BPM** like the original. Meter (7/4 or 4/4) is chosen per pack.
- **No high-pitched or piercing sounds, ever.** Warm, natural, fun instruments. Every render is
  checked against the original: 2-4 kHz at or below it, almost nothing above 4 kHz.
- **One song, five versions** (main, packs, planet, shop, boss) with the same tempo, chords and
  length, because the game crossfades between them. Each version is based on what Balatro's own
  version for that place does, and holds its mood for the whole time you are there.
- **Process:** agree the direction with references → short samples → full main → the four
  place versions → export → test in game.

## Packs

### Crescendo: done (2026-11-01)
The theme as a Bolero-style orchestral build with a live garage-band drummer, 7/4.
Main builds inside the loop; boss is tense all loop (heartbeat kick, creeping low strings,
clipped brass). Scripts: `crescendo_garage.py` (main), `crescendo_versions.py` (the rest).

### Vesper: done (2026-11-02)
Morricone / Red Dead Redemption at dusk, "Ghost Riders" triplet shuffle, 4/4. Twangy low guitar
riff, walking upright bass, floor-tom gallop, trumpet tune, trombone, low male choir. No whistle,
no soprano, no whip cracks. Script: `vesper.py`.
- main changes every phrase: the ride, a stop-time break, the "train" (guitar takes the tune),
  a trombone counter-melody, B (campfire, half-time), C (stampede build), A3 (everything)
- shop: stride honky-tonk saloon piano, brushes, banjo · packs: habanera bass, hand drums, nylon
  ripples, muted trumpet · planet: no drums, muffled strings + choir + harmonica ·
  boss: showdown on a grinding F/Gb pedal, war toms, a line creeping up every phrase

### Basilicus: medieval tavern / royal court dance (in progress, 2026-11-02)
Dice games in a king's tavern. Witcher 3 tavern music, Kingdom Come: Deliverance, Age of Empires II.
Lute (plucked guitar + harp), hurdy-gurdy drone (low accordion), English horn as a crumhorn-like
reed on the tune, fiddle, bassoon, frame drum, stomps and claps. No brass. Straight eighths (Vesper
owns the triplet shuffle). Two samples waiting for Locked's pick: `estampie` (4/4) and `dance7`
(7/4, 2+2+3). Script: `basilicus_samples.py`. The pack still holds an old rejected draft.
