# BalaMods

My collection of [Balatro](https://www.playbalatro.com/) mods, built on [Steamodded](https://github.com/Steamodded/smods) + [Lovely](https://github.com/ethangreen-dev/lovely-injector).

## Mods

| Mod | Description | Latest |
|-----|-------------|--------|
| _none yet_ | | |

Download a mod's zip from [Releases](../../releases) and extract it into `%AppData%\Balatro\Mods`.

## Repo layout

```
mods/<ModId>/        one folder per mod (manifest.json, main.lua, assets/, localization/)
_template/           starting point copied by tools/new-mod.ps1
tools/new-mod.ps1    scaffold a new mod and link it into the game
tools/link.ps1       link repo mods into %AppData%\Balatro\Mods (junctions)
.github/workflows/   tag-based release: one zip per mod
```

## Workflow

**New mod**
```powershell
.\tools\new-mod.ps1 -Id MyMod -Name "My Mod" -Prefix mymod
```
This creates `mods/MyMod` and links it into the game's Mods folder, so editing files here is what the game loads. Restart Balatro (or use Steamodded's reload) to see changes.

**Re-link after a fresh clone:** `.\tools\link.ps1`

**Release a mod**
1. Bump `version` in `mods/MyMod/manifest.json` and commit.
2. `git tag MyMod-v0.2.0; git push origin MyMod-v0.2.0`
3. GitHub Actions publishes a release with `MyMod-v0.2.0.zip` containing only that mod.

## Editor setup
Install the VS Code **Lua** extension (sumneko). `.luarc.json` points it at Steamodded's `lsp_def`, so you get autocomplete for `SMODS.*`.
