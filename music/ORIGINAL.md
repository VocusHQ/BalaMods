# Original Balatro theme: measured analysis

Source: game's resources/sounds/music1-5.ogg (extracted from Balatro.exe; not stored in this repo).
Method: librosa + Spotify Basic Pitch audio-to-MIDI, then grid/chord fitting (tools/odeum/analysis/).

- All 5 variants: 173.6 s, same piece, synced.
- Tempo: exactly 150 BPM, straight 16th grid. Meter: 7/4 (bar = 2.8 s). 62 bars.
- Key: Bb minor.

## Form (bar numbers, music1)
| Bars  | Section | Harmony (per bar) |
|-------|---------|-------------------|
| 1-4   | Intro   | Bbm, Db/B, Bbm, F/Eb |
| 5-20  | A x4    | F7 , Dbmaj7 , Bbm , Ebm7  (V - III - i - iv); 3rd pass (bar 14) swaps Dbmaj7 for a 2nd Bbm |
| 21-22 | Turn    | F7, Bbm |
| 23-36 | B       | Gb, Gb, Fm/Ab, Fm/Ab, Gb, Gb, Fm/Ab, Fm, Cb(B), Gb, Fm, Fm, Cb(B), Gb |
| 37-46 | C       | Fm, Fm, Db, Fm, Db, F, Db, Fm, Fm, Fm |
| 47-62 | A x4    | as above, ends on F/Bb7 back to the top |

## Melody and texture (after Demucs htdemucs_6s split of music1)
Stem levels: bass -23 dB and "other" (synths) -24 dB carry everything; drums -26; guitar/piano minor; no vocals.
The piece has no busy tune. It is a slow sustained pad with a few long lead notes, over a repeating bass riff:
- A section lead (per 4-bar cycle): long F5 over bars 1-2 (F7, Dbmaj7) -> C5 held a whole bar (Bbm) -> Bb4 held a whole bar (Ebm7), Db5 pickup into the next cycle. Later cycles add short Db5/C5/A4 and Eb5 turns in bars 1-2.
- Bass riff (4 bars, repeats): Eb2 pickup -> F1 (low, held) with F2/C2 jumps | Db2 held | Bb1 held + Bb2/Ab2 | Eb2 hits with F2 lead-in. Octave leaps, syncopated against the 7/4.
- B section: pad Bb3-Db4-F4 over Gb bass; lead C5 (bar 29) -> F5 held two bars (30-31) -> Db5 (bar 35-36).
- C section: F4 held as a drone for ~10 bars with C5/Ab4 pad movement and short F5 calls.
- Lead synth wobbles in pitch (transcriber chops it into fragments), part of the signature sound.
Piano rolls: regenerate with tools/odeum/analysis/roll.py.

## Drums (drums stem, folded over bars 5-20; same pattern in B and C)
7/4 felt as 3+4. Kick on 1, &2, &5, 6 (lighter on 7). Snare on 3 and 7. Closed hats on 8ths, accented on the beat.

## Wobble (measured with pyin on the stems)
The whole synth layer warbles: fast vibrato ~4.5-7 Hz, lead +-11-27 cents, pad ~+-10 cents, plus slow tape-like drift
of ~50-60 cents range. Reproduced in tools/odeum/drafts/reference_render.py (time-varying delay per track).

## Full form, bar by bar (from the bass stem; riffs below)
| Bars | Bass riffs |
|------|-----------|
| 1 | none: pad only (Bb3 Db4 F4 Ab4), no drums. Drums enter bar 2 (softer) |
| 2-4 | Cb, Bb, Eb. Lead dyad C5+F5 enters bar 3 beat 3 and holds into bar 6 |
| 5-20 | A: F, Db, Bb, Eb x4 (bar 14 = Bb instead of Db) |
| 21-22 | F, Bb |
| 23-36 | B: Gb, Gb, Ab, Ab, Gb, Gb, Ab, F, Cb, Gb, Fm-walk, Fm-walk, Cb, Gb |
| 37-46 | C: Ab, F, then Db-low / F-low alternating (39-46) under an F4 drone |
| 47-62 | A': Bb, Eb, then F, Db, Bb, Eb x3, ending F, Bb -> loops to bar 1 |

Riffs, as (beat, note, beats) in a 7/4 bar:
- F:  Eb2 0 1.25, F1 1.5 3, F2 4.5 .5, A2 5 .5, Eb2 5.5 .5, C2 6 .5, F2 6.5 .5
- Db: Db2 0 3.25, Bb1 3.5 .75, Eb2 5 1, Bb2 6.5 .5
- Bb: Bb1 0 4.5, Bb2 4.5 .5, Db3 5 .5, Ab2 5.5 .5, Eb2 6 .5, F2 6.5 .5
- Eb: Eb2 0 1.25, Bb1 1.5 1.75, Eb2 3.5 1, Db3 4.5 .5, C3 5 .5, Bb2 5.5 .5, F2 6 .5, Gb2 6.5 .5
- Gb: Gb1 0 4.5, Gb2 4.5 .5, Bb2 5 .5, Db2 5.5 .5, Gb2 6 1
- Ab: Ab1 0 4.5, Ab2 4.5 .5, C3 5 .5, Eb2 5.5 .5, Ab2 6 .5, C2 6.5 .5
- Cb: B1 0 4.25, Gb2 4.5 .5, B2 5 .5, Eb2 5.25 1, B1 6.25 .75
- Fm-walk: Ab1 0 1.25, Bb1 1.5 1.75, C2 3.5 .75, Ab2 4.5 .5, C3 5.25 .5, F2 5.5 .5, Ab2 6 .5, C2 6.5 .5
- C-section Db-low: Db1 0 1, Db1 1.5 1.25, Db1 3.5 1, C3 4.5 .5, Db3 5 .5, Ab2 5.5 .5, Db2 6 .5, Eb2 6.5 .5
- C-section F-low: F1 0 1.25, C1 1.75 1.25, F1 3.25 2.25, Ab1 6 1
Riffs often anticipate the next bar's root by a 16th.

Full reference: tools/odeum/drafts/reference_full.py (plays the cleaned transcription). Chroma vs original
0.88 mean per bar (weakest 0.70-0.79: bars 6, 28, 35, 43, 48; original shows a G natural there, likely drift smear).
