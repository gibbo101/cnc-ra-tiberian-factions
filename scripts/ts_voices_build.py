#!/usr/bin/env python3
"""Build Tiberian Sun GDI's unit-response voices for the mod.

TS keys its unit voices to numbered voice sets in its own RULES.INI: set 15 is
the GDI infantryman, set 25 the GDI vehicle crew (both in SOUNDS.MIX inside
TIBSUN.MIX). RA instead fires a named VOC_ event and picks an extension from
the response variation -- .V01/.V03 are the direct infantry takes, .V00/.V02
the radio-filtered vehicle takes. So each RA voice event needs four TS
recordings: two infantry, two vehicle.

The rows below assign TS's selection lines to RA's selection events and TS's
move/attack lines to its order events, so a Titan answers an order the way it
does in Tiberian Sun.

The DLL sends the bare event name (dllinterface.cpp, On_Sound_Effect) and the
launcher prefixes RAC_ or RAR_. One recording serves both, as with the TD set.

Idempotent: re-running rewrites the generated XML block and the WAVs in place.

usage: ts_voices_build.py [--ts-dir <Tiberian Sun install>]

License: GPL v3.
"""
import argparse
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

BEGIN = "   <!-- BEGIN generated TS GDI unit-voice events (scripts/ts_voices_build.py) -->"
END = "   <!-- END generated TS GDI unit-voice events -->"

RATE = 44077  # the localized channel's shape, as for the EVA set

# event base -> (infantry .V01, infantry .V03, vehicle .V00, vehicle .V02)
#
# Infantry lines come from TS voice set 15 (GDI rifleman), vehicle lines from
# set 25 (GDI vehicle crew) -- the sets TS's own RULES.INI gives every GDI unit
# we field. Selection events draw on each set's VoiceSelect list, order events
# on VoiceMove and VoiceAttack.
VOICES = {
    "TSYESSIR1": ("15-I000", "15-I004", "25-I000", "25-I002"),
    "TSREPORT1": ("15-I004", "15-I012", "25-I002", "25-I004"),
    "TSAWAIT1":  ("15-I012", "15-I048", "25-I004", "25-I006"),
    "TSREADY":   ("15-I048", "15-I000", "25-I006", "25-I000"),
    "TSVEHIC1":  ("15-I000", "15-I048", "25-I000", "25-I004"),
    "TSUNIT1":   ("15-I004", "15-I000", "25-I002", "25-I006"),
    "TSACKNO":   ("15-I018", "15-I024", "25-I012", "25-I014"),
    "TSAFFIRM1": ("15-I024", "15-I044", "25-I014", "25-I016"),
    "TSROGER":   ("15-I044", "15-I018", "25-I016", "25-I018"),
    "TSMOVOUT1": ("15-I018", "15-I044", "25-I018", "25-I022"),
    "TSUGOTIT":  ("15-I024", "15-I018", "25-I022", "25-I012"),
    "TSNOPROB":  ("15-I044", "15-I024", "25-I012", "25-I016"),
    "TSRITAWAY": ("15-I018", "15-I050", "25-I014", "25-I024"),
}

EXTS = (".V01", ".V03", ".V00", ".V02")  # the order the tuples are written in

# Single takes for the TS infantry with a voice set of their own: set 19 the Engineer, set 20
# the Medic, set 14 the Ghost Stalker (each type's VoiceSelect, VoiceMove and VoiceAttack
# lines). Each becomes the event TS<set>I<line> with no extension, the IN_NOVAR shape the TD
# Commando's lines use; infantry.cpp's response tables choose among them.
SINGLES = (
    "19-I000", "19-I002", "19-I006", "19-I010", "19-I016", "19-I018",
    "20-I000", "20-I004", "20-I006", "20-I008", "20-I010", "20-I012", "20-I016", "20-I018", "20-I020",
    "14-I000", "14-I002", "14-I004", "14-I008", "14-I010", "14-I012", "14-I014", "14-I016",
    "30-I000", "30-I002", "30-I004", "30-I006", "30-I014", "30-I016", "30-I018", "30-I022",
    "30-I030", "30-I034", "30-I036",
)


def single_base(aud):
    return "TS" + aud.replace("-", "")


def extract(ts_dir, tmp):
    mix = Path(ts_dir) / "TIBSUN.MIX"
    if not mix.exists():
        sys.exit("no TIBSUN.MIX under %s" % ts_dir)
    names = sorted({n for row in VOICES.values() for n in row} | set(SINGLES))
    cmd = [sys.executable, str(TS_EXTRACT), str(mix), "SOUNDS.MIX", "extract", str(tmp)]
    cmd += ["%s.AUD" % n for n in names]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("extract failed:\n" + out.stderr)
    missing = [n for n in names if not (tmp / ("%s.AUD" % n)).exists()]
    if missing:
        sys.exit("voices not in SOUNDS.MIX: %s" % missing)
    return len(names)


def sample_name(base, ext):
    return "TS_SFX_UNT_%s%s_EN-US" % (base[2:], ext)


def encode(tmp, base, ext, aud):
    pcm = tmp / ("%s%s.pcm.wav" % (base, ext))
    subprocess.run([sys.executable, str(AUD_DECODE), str(tmp / ("%s.AUD" % aud)), str(pcm)],
                   check=True, capture_output=True)
    dst = AUDIO_OUT / ("%s.WAV" % sample_name(base, ext))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(pcm),
                    "-ac", "2", "-ar", str(RATE), "-c:a", "adpcm_ms", str(dst)], check=True)
    return dst


def event(name, sample):
    return (
        '   <LocalizedSFXEvent Name="%s" Preset="_PRESET_UR">\n'
        "      <SampleNamesList>\n"
        "         <entry> %s.MP3 </entry>\n"
        "      </SampleNamesList>\n"
        "      <LocalizedTextIDs>\n"
        "      </LocalizedTextIDs>\n"
        "      <MinVolume> 100 </MinVolume>\n"
        "      <MaxVolume> 100 </MaxVolume>\n"
        "      <Priority> 2 </Priority>\n"
        "   </LocalizedSFXEvent>\n" % (name, sample))


def write_xml():
    text = XML.read_text(encoding="utf-8", errors="surrogateescape")
    body = [BEGIN + "\n"]
    count = 0
    for base in sorted(VOICES):
        for ext in EXTS:
            sample = sample_name(base, ext)
            for prefix in ("RAC", "RAR"):
                body.append(event("%s_SFX_%s%s" % (prefix, base, ext), sample))
                count += 1
    for aud in SINGLES:
        base = single_base(aud)
        sample = sample_name(base, "")
        for prefix in ("RAC", "RAR"):
            body.append(event("%s_SFX_%s" % (prefix, base), sample))
            count += 1
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
    return count


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts-dir", default=str(DEFAULT_TS))
    args = ap.parse_args()

    AUDIO_OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        print("extracted %d voice lines from SOUNDS.MIX" % extract(args.ts_dir, tmp))
        for base in sorted(VOICES):
            row = VOICES[base]
            for ext, aud in zip(EXTS, row):
                dst = encode(tmp, base, ext, aud)
                print("  %-10s %-4s %s -> %s" % (base, ext, aud, dst.name))
        for aud in SINGLES:
            dst = encode(tmp, single_base(aud), "", aud)
            print("  %-10s      %s -> %s" % (single_base(aud), aud, dst.name))
    print("registered %d events in %s" % (write_xml(), XML.name))


if __name__ == "__main__":
    main()
