# Creates a new mod from _template and links it into Balatro's Mods folder.
# Usage: .\tools\new-mod.ps1 -Id MyMod -Name "My Mod" -Prefix mymod
param(
    [Parameter(Mandatory)] [string] $Id,
    [string] $Name = $Id,
    [string] $Prefix = $Id.ToLower(),
    [string] $Author = "VocusHQ"
)

$root = Split-Path $PSScriptRoot -Parent
$dest = Join-Path $root "mods\$Id"
if (Test-Path $dest) { throw "mods\$Id already exists" }

Copy-Item (Join-Path $root "_template") $dest -Recurse
Get-ChildItem $dest -Recurse -File -Include *.json, *.lua, *.md | ForEach-Object {
    $text = [IO.File]::ReadAllText($_.FullName)
    $text = $text.Replace("__MOD_ID__", $Id).Replace("__MOD_NAME__", $Name).Replace("__PREFIX__", $Prefix).Replace("__AUTHOR__", $Author)
    [IO.File]::WriteAllText($_.FullName, $text)
}

Write-Host "Created mods\$Id"
& (Join-Path $PSScriptRoot "link.ps1") -Id $Id
