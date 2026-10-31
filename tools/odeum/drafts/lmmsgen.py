"""Shared helpers for writing LMMS song projects that use the MuseScore_General SoundFont."""
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SF2 = "D:/Downloads/BalaMods/music/soundfonts/MuseScore_General.sf2"
BEAT, BAR = 48, 192

# General MIDI programs (bank 0) and drum kits (bank 128)
PIANO, EPIANO, VIBES, ORGAN = 0, 4, 11, 16
NYLON_GUITAR, STEEL_GUITAR, ACOUSTIC_BASS = 24, 25, 32
STRINGS, SLOW_STRINGS, HARP = 48, 49, 46
TRUMPET, TROMBONE, MUTED_TRUMPET, BRASS = 56, 57, 59, 61
ALTO, TENOR, CLARINET, FLUTE = 65, 66, 71, 73
WARM_PAD = 89
STANDARD_KIT, JAZZ_KIT, BRUSH_KIT = 0, 32, 40
# GM drum keys
KICK, STICK, SNARE, CLAP, CLOSED_HH, PEDAL_HH, OPEN_HH, CRASH, RIDE = 36, 37, 38, 39, 42, 44, 46, 49, 51
LOW_CONGA, MUTE_CONGA, OPEN_CONGA, MARACAS = 64, 62, 63, 70

ENV = dict(latt="0", lamt="0", lspd_numerator="4", lspd_denominator="4", userwavefile="", ctlenvamt="0", lshp="0",
           x100="0", lpdel="0", lspd="0.1", pdel="0", syncmode="0", hold="0.5", att="0", dec="0.5", sustain="0.5",
           rel="0.1", amt="0")


def pos(beat, swung):
    """Beat (in 0.5 steps) -> ticks. Swung eighths fall on the triplet (2:1)."""
    whole = int(beat)
    frac = beat - whole
    if swung and frac >= 0.5:
        return whole * BEAT + 32
    return whole * BEAT + round(frac * BEAT)


def note(bar, beat, key, beats, vel=100, swung=False):
    return (bar * BAR + pos(beat, swung), key, max(8, int(beats * BEAT) - 6), vel)


def sf2(patch, bank=0, reverb=0.35):
    it = ET.Element("instrumenttrack", pitch="0", fxch="0", basenote="57", usemasterpitch="1", pitchrange="1",
                    vol="100", pan="0")
    inst = ET.SubElement(it, "instrument", name="sf2player")
    ET.SubElement(inst, "sf2player", src=SF2, bank=str(bank), patch=str(patch), gain="1",
                  reverbOn="1", reverbRoomSize="0.5", reverbDamping="0.4", reverbWidth="0.8", reverbLevel=str(reverb),
                  chorusOn="0", chorusNum="3", chorusLevel="2", chorusSpeed="0.3", chorusDepth="8")
    el = ET.SubElement(it, "eldata", ftype="0", fres="0.5", fcut="14000", fwet="0")
    for n in ("elvol", "elcut", "elres"):
        ET.SubElement(el, n, **ENV)
    ET.SubElement(it, "chordcreator", chord="0", chordrange="1", **{"chord-enabled": "0"})
    ET.SubElement(it, "arpeggiator", arp="0", arptime_numerator="4", arptime_denominator="4", arprange="1",
                  arpmode="0", arptime="100", arpdir="0", arpgate="100", syncmode="0", **{"arp-enabled": "0"})
    ET.SubElement(it, "fxchain", enabled="0", numofeffects="0")
    return it


def build(tracks, bpm, bars, vols=None):
    """tracks: [(name, (patch, bank), notes_fn)] -> ElementTree. vols: {name: volume}."""
    vols = vols or {}
    proj = ET.Element("lmms-project", creator="LMMS", version="1.0", type="song", creatorversion="1.2.2")
    ET.SubElement(proj, "head", timesig_numerator="4", bpm=str(bpm), timesig_denominator="4", mastervol="100",
                  masterpitch="0")
    song = ET.SubElement(proj, "song")
    tc = ET.SubElement(song, "trackcontainer", type="song", x="5", y="5", width="900", height="420", visible="1",
                       maximized="0", minimized="0")
    for name, (patch, bank), notes in tracks:
        tr = ET.SubElement(tc, "track", muted="0", name=name, solo="0", type="0")
        it = sf2(patch, bank)
        it.set("vol", str(vols.get(name, 60)))
        tr.append(it)
        pat = ET.SubElement(tr, "pattern", pos="0", len=str(bars * BAR), muted="0", name=name.split(" [")[0],
                            steps="16", type="1")
        for p, key, length, vel in sorted(notes()):
            ET.SubElement(pat, "note", pos=str(p), key=str(key), len=str(length), vol=str(vel), pan="0")
    fx = ET.SubElement(song, "fxmixer", x="1", y="463", width="530", height="332", visible="0", maximized="0",
                       minimized="0")
    c = ET.SubElement(fx, "fxchannel", num="0", name="Master", volume="1", muted="0", soloed="0")
    ET.SubElement(c, "fxchain", enabled="0", numofeffects="0")
    ET.SubElement(song, "timeline", lp0pos="0", lp1pos=str(bars * BAR), lpstate="1")
    ET.SubElement(song, "controllers")
    return ET.ElementTree(proj)


def main(tracks, bpm, bars):
    """CLI: script.py OUT.mmp [VOLS.json]"""
    out = Path(sys.argv[1])
    vols = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else {}
    out.parent.mkdir(parents=True, exist_ok=True)
    tree = build(tracks, bpm, bars, vols)
    ET.indent(tree)
    with open(out, "wb") as f:
        f.write(b'<?xml version="1.0"?>\n<!DOCTYPE lmms-project>\n')
        tree.write(f, encoding="utf-8")
    print(out)
