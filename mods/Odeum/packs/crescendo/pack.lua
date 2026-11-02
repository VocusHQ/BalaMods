-- Crescendo: Bolero-style orchestra + live drummer, 7/4 at 150 BPM. Exported with tools/odeum/drafts/export_pack.py crescendo
return {
    name = "Crescendo",
    author = "Locked",
    description = "Building, rising, louder every hand",
    volume = 1.0, -- SoundFont mixes are quieter than the synth drafts were
    pitch = 1,
    card = "S_A",
    -- title.png is generated from this: python tools/odeum/make_title.py --pack mods/Odeum/packs/crescendo
    title = { left = "CRES", right = "CENDO", font = "CHILLER.TTF" },
}
