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
