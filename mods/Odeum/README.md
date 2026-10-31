# Odeum

Soundtrack packs for Balatro. Each pack replaces the game's music with its own song and
brings its own title logo. Pick the active pack in **Mods → Odeum → Config → Soundtrack**;
switching is instant, and **Vanilla** turns everything back to the original game.

## Requirements
- [Lovely](https://github.com/ethangreen-dev/lovely-injector)
- [Steamodded](https://github.com/Steamodded/smods) 1.0.0+

## Install
Download `Odeum-vX.Y.Z.zip` from this repo's Releases and extract it into `%AppData%\Balatro\Mods`.

## Making a pack
Add a folder to `packs/`. The folder name is the pack's id.

```
packs/<id>/
  pack.lua          -- name and options (see packs/testum/pack.lua)
  title.png         -- optional title logo, 666x432 (drawn at 333x216)
  music/
    music1.ogg      -- main theme (required)
    music2.ogg      -- Tarot / Spectral / Standard / Buffoon packs
    music3.ogg      -- Planet (Celestial) packs
    music4.ogg      -- shop
    music5.ogg      -- boss blind
```

- **The five tracks are versions of one song.** The game plays them all at once and fades
  between them, so they must be exactly the same length and tempo. Any missing version
  falls back to `music1`.
- **Title logo:** the card in the middle of the title screen sits at the centre of the
  image (about x 290–376 at 666 px wide), so leave a gap there. `card` in `pack.lua` picks which
  card is shown (e.g. `"H_K"` for the King of Hearts).
- Use `.ogg` files.
