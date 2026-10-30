# Links mods from this repo into %AppData%\Balatro\Mods using directory junctions
# (no admin needed). Edits in the repo show up in-game on restart.
# Usage: .\tools\link.ps1            -> link every mod in mods\
#        .\tools\link.ps1 -Id MyMod  -> link one mod
#        .\tools\link.ps1 -Unlink    -> remove the links (repo files are untouched)
param(
    [string] $Id,
    [switch] $Unlink
)

$root = Split-Path $PSScriptRoot -Parent
$gameMods = Join-Path $env:APPDATA "Balatro\Mods"
if (-not (Test-Path $gameMods)) { throw "Balatro Mods folder not found: $gameMods" }

$mods = if ($Id) { @(Get-Item (Join-Path $root "mods\$Id")) } else { Get-ChildItem (Join-Path $root "mods") -Directory }

foreach ($mod in $mods) {
    $link = Join-Path $gameMods $mod.Name
    $existing = Get-Item $link -ErrorAction SilentlyContinue

    if ($Unlink) {
        if ($existing -and $existing.LinkType -eq "Junction") {
            $existing.Delete()
            Write-Host "Unlinked $($mod.Name)"
        }
        continue
    }

    if ($existing) {
        if ($existing.LinkType -eq "Junction") { Write-Host "Already linked: $($mod.Name)"; continue }
        Write-Warning "$link exists and is a real folder - skipping (remove it first)"
        continue
    }
    New-Item -ItemType Junction -Path $link -Target $mod.FullName | Out-Null
    Write-Host "Linked $($mod.Name) -> $link"
}
