#!/usr/bin/env python3
"""Build Tiberian Sun GDI's EVA voice set for the mod.

Extracts the GDI announcer's lines from the Tiberian Sun install (TIBSUN.MIX ->
SPEECH01.MIX -> 00-Ixxx.AUD), re-encodes each to the MS-ADPCM WAV shape the
launcher's localized audio channel accepts, ships them loose under
Data/AUDIO/EN-US, and registers one event per line in the mod's loose
SFXEVENTSLOCALIZED.XML.

The DLL hands the launcher the bare event name (SpeechTS[] in audio.cpp); the
launcher prefixes RAC_ or RAR_ for classic and remastered audio. Only one
recording exists per line, so both prefixes resolve to the same file -- the
same compromise the TD voice set ships with.

Sample names are novel: the dormant-host constraint was falsified 2026-08-31.
What matters is the FORMAT (MS-ADPCM, never plain PCM, which crashes ClientG)
and that localized samples sit under a locale directory with the XML naming
them .MP3 while the file on disk is .WAV.

Idempotent: re-running rewrites the generated XML block and the WAVs in place.

usage: ts_eva_build.py [--ts-dir <Tiberian Sun install>]

License: GPL v3.
"""
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parent
TS_EXTRACT = WORKSPACE / "tools/ts_extract.py"
AUD_DECODE = ROOT / "scripts/ts_aud_decode.py"
AUDIO_OUT = ROOT / "resources/remaster_mods/Vanilla_RA/Data/AUDIO/EN-US"
XML = ROOT / "resources/remaster_mods/Vanilla_RA/Data/XML/AUDIO/SFXEVENTSLOCALIZED.XML"
DEFAULT_TS = Path.home() / ".steam/steam/steamapps/common/Command & Conquer Tiberian Sun"

BEGIN = "   <!-- BEGIN generated TS GDI EVA events (scripts/ts_eva_build.py) -->"
END = "   <!-- END generated TS GDI EVA events -->"

# event key -> (TS .AUD line, subtitle text id or None, what the line says)
#
# The .AUD numbers are OpenTS's Speech[] table (reference/OpenTS code/vox.cpp),
# which is EA's own VOX_ ordering, so each row is TS's recording of the same
# announcement RA fires. Subtitles borrow the TD announcer's string where the
# wording matches; a None ships the line with no subtitle rather than a wrong one.
LINES = {
    "ACCOM1":   ("00-I026", "TEXT_SFX_TDC_SFX_ACCOM1",    "mission accomplished"),
    "FAIL1":    ("00-I028", "TEXT_SFX_TDC_SFX_FAIL1",     "your mission has failed"),
    "NOFACT1":  ("00-I064", "TEXT_SFX_TDC_SFX_BLDG1",     "unable to comply, building in progress"),
    "CONSTRU1": ("00-I018", "TEXT_SFX_TDC_SFX_CONSTRU1",  "construction complete"),
    "UNITREDY": ("00-I076", "TEXT_SFX_TDC_SFX_UNITREDY",  "unit ready"),
    "NEWOPT1":  ("00-I032", "TEXT_SFX_TDC_SFX_NEWOPT1",   "new construction options"),
    "DEPLOY1":  ("00-I016", "TEXT_SFX_TDC_SFX_DEPLOY1",   "cannot deploy here"),
    "STRCLOST": ("00-I008", "TEXT_SFX_TDC_SFX_STRCLOST",  "structure lost"),
    "NOCASH1":  ("00-I022", "TEXT_SFX_TDC_SFX_NOCASH1",   "insufficient funds"),
    "BATLCON1": ("00-I012", "TEXT_SFX_TDC_SFX_BATLCON1",  "battle control terminated"),
    "REINFOR1": ("00-I038", "TEXT_SFX_TDC_SFX_REINFOR1",  "reinforcements have arrived"),
    "CANCEL1":  ("00-I220", "TEXT_SFX_TDC_SFX_CANCEL1",   "canceled"),
    "BLDGING1": ("00-I216", "TEXT_SFX_TDC_SFX_BLDGING1",  "building"),
    "TRAIN1":   ("00-I062", None,                         "training"),
    "LOPOWER1": ("00-I024", "TEXT_SFX_TDC_SFX_LOPOWER1",  "low power"),
    "BASEATK1": ("00-I082", "TEXT_SFX_TDC_SFX_BASEATK1",  "our base is under attack"),
    "PRIBLDG1": ("00-I034", "TEXT_SFX_TDC_SFX_PRIBLDG1",  "primary building selected"),
    "UNITLOST": ("00-I074", "TEXT_SFX_TDC_SFX_UNITLOST",  "unit lost"),
    "SELECT1":  ("00-I042", "TEXT_SFX_TDC_SFX_SELECT1",   "select target"),
    "SILOS1":   ("00-I044", "TEXT_SFX_TDC_SFX_SILOS1",    "silos needed"),
    "ONHOLD1":  ("00-I218", "TEXT_SFX_TDC_SFX_ONHOLD1",   "on hold"),
    "REPAIR1":  ("00-I040", "TEXT_SFX_TDC_SFX_REPAIR1",   "repairing"),
    "STRUSLD1": ("00-I228", "TEXT_SFX_TDC_SFX_STRUSLD1",  "structure sold"),
    "UNITREPD": ("00-I078", None,                         "unit repaired"),
    "IONREADY": ("00-I156", None,                         "ion cannon ready"),
    "MISNWON":  ("00-I284", None,                         "you are victorious"),
    "MISNLST":  ("00-I286", None,                         "you have lost"),
}

# The localized EVA channel: MS-ADPCM, stereo, 44077 Hz -- the shape proven in
# game 2026-08-31. Plain PCM crashes ClientG's ADPCM block maths.
RATE = 44077


def extract(ts_dir, tmp):
    mix = Path(ts_dir) / "TIBSUN.MIX"
    if not mix.exists():
        sys.exit("no TIBSUN.MIX under %s" % ts_dir)
    names = sorted({aud for aud, _, _ in LINES.values()})
    cmd = [sys.executable, str(TS_EXTRACT), str(mix), "SPEECH01.MIX", "extract", str(tmp)]
    cmd += ["%s.AUD" % n for n in names]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("extract failed:\n" + out.stderr)
    missing = [n for n in names if not (tmp / ("%s.AUD" % n)).exists()]
    if missing:
        sys.exit("lines not in SPEECH01.MIX: %s" % missing)
    return len(names)


def encode(tmp, key, aud):
    """AUD -> PCM WAV -> the launcher's MS-ADPCM shape."""
    pcm = tmp / ("%s.pcm.wav" % key)
    subprocess.run([sys.executable, str(AUD_DECODE), str(tmp / ("%s.AUD" % aud)), str(pcm)],
                   check=True, capture_output=True)
    dst = AUDIO_OUT / ("TS_SFX_EVA_%s_EN-US.WAV" % key)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pcm),
                    "-ac", "2", "-ar", str(RATE), "-c:a", "adpcm_ms", str(dst)], check=True)
    return dst


def event(name, sample, text_id, says):
    subtitle = "         <entry> %s </entry>\n" % text_id if text_id else ""
    return (
        '   <!-- "%s" -->\n'
        '   <LocalizedSFXEvent Name="%s" Preset="_PRESET_HUD">\n'
        "      <SampleNamesList>\n"
        "         <entry> %s </entry>\n"
        "      </SampleNamesList>\n"
        "      <LocalizedTextIDs>\n"
        "%s"
        "      </LocalizedTextIDs>\n"
        "      <MinVolume> 100 </MinVolume>\n"
        "      <MaxVolume> 100 </MaxVolume>\n"
        "      <Priority> 2 </Priority>\n"
        "      <QueueIfCantPlay> True </QueueIfCantPlay>\n"
        "   </LocalizedSFXEvent>\n" % (says, name, sample, subtitle))


def write_xml():
    text = XML.read_text(encoding="utf-8", errors="surrogateescape")
    body = [BEGIN + "\n"]
    for key in sorted(LINES):
        _, text_id, says = LINES[key]
        sample = "TS_SFX_EVA_%s_EN-US.MP3" % key
        for prefix in ("RAC", "RAR"):
            body.append(event("%s_SFX_TS%s" % (prefix, key), sample, text_id, says))
    body.append(END + "\n")
    block = "".join(body)

    start = text.find(BEGIN)
    if start >= 0:
        stop = text.find(END, start) + len(END) + 1
        text = text[:start] + block + text[stop:]
    else:
        close = text.rfind("</LocalizedSFXEvents>")
        text = text[:close] + "\n" + block + "\n" + text[close:]
    XML.write_text(text, encoding="utf-8", errors="surrogateescape")
    return len(LINES) * 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts-dir", default=str(DEFAULT_TS))
    args = ap.parse_args()

    AUDIO_OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        print("extracted %d lines from SPEECH01.MIX" % extract(args.ts_dir, tmp))
        for key in sorted(LINES):
            aud = LINES[key][0]
            dst = encode(tmp, key, aud)
            print("  %-9s %s -> %s (%d bytes)" % (key, aud, dst.name, dst.stat().st_size))
    print("registered %d events in %s" % (write_xml(), XML.name))


if __name__ == "__main__":
    main()
