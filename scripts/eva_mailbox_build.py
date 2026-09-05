#!/usr/bin/env python3
"""Build the era-mailbox EVA payloads and the DLL's lookup table, for N eras.

Six EVA lines are fired by the launcher itself and never reach On_Speech: "cannot
deploy here", "battle control terminated", mission won, mission lost, "select
target" and "insufficient power". The mod speaks them in the picked side's voice
by writing the era-correct recording over the launcher's own sample names at match
start, and by overwriting ClientG's already-cached copy so an in-session faction
switch is corrected too (docs/eva-ram-patch-spike.md).

The cache overwrite hunts the WRONG era's distinctive bytes in ClientG's heap and
writes the RIGHT era's file over the blob it found, so **every era's payload for a
line must be byte-identical in length**. Adding an era therefore re-pads every
line and invalidates every needle -- which is why this generates the whole table
rather than leaving 20-byte arrays to be pasted in by hand. A new era is one entry
in ERAS plus its recordings.

Formats follow the line's existing RA payload (rate and block alignment), because
those match the base samples the launcher loaded; the teardown line in particular
needs block_align 70, which ffmpeg cannot produce (scripts/msadpcm.py exists for
exactly that reason).

usage: eva_mailbox_build.py [--ts-dir <Tiberian Sun install>] [--check]

  --check  rebuild into a temporary directory and report what would change

License: GPL v3.
"""
import argparse
import array
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import msadpcm  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parent
AUDIO = ROOT / "resources/remaster_mods/Vanilla_RA/Data/AUDIO/EN-US"
# The RA and TD recordings come from a frozen snapshot, never from AUDIO: the files in
# AUDIO are this script's own output, so reading them back would add one more ADPCM
# generation on every run. See scripts/eva_work/README.md.
SRC = ROOT / "scripts/eva_work/src"
HEADER = ROOT / "redalert/tf_eva_mailbox.h"
TS_EXTRACT = WORKSPACE / "tools/ts_extract.py"
AUD_DECODE = ROOT / "scripts/ts_aud_decode.py"
DEFAULT_TS = Path.home() / ".steam/steam/steamapps/common/Command & Conquer Tiberian Sun"

# The eras, in the order the generated table indexes them. Adding one (TS Nod's
# CABAL, RA2's announcers) means adding it here with its sources and re-running.
ERAS = ["RA", "TD", "TS"]

# tag -> (launcher sample name for the classic channel, for the remastered channel)
LINES = {
    "NODEPLY": ("RAC_SFX_EVA_NODEPLY1_EN-US.WAV", "RAR_SFX_EVA_NODEPLY1_EN-US.WAV"),
    "BCT":     ("RAC_SFX_EVA_BCT1_EN-US.WAV", "RAR_SFX_EVA_BCT1_EN-US.WAV"),
    "WON":     ("RAC_SFX_EVA_MISNWON1_EN-US.WAV", "RAR_SFX_EVA_MISNWON1_EN-US.WAV"),
    "LST":     ("RAC_SFX_EVA_MISNLST1_EN-US.WAV", "RAR_SFX_EVA_MISNLST1_EN-US.WAV"),
    "SLCT":    ("RAC_SFX_EVA_SLCTTGT1_EN-US.WAV", "RAR_SFX_EVA_SLCTTGT1_EN-US.WAV"),
    "NOPOW":   ("RAC_SFX_EVA_NOPOWR1_EN-US.WAV", "RAR_SFX_EVA_NOPOWR1_EN-US.WAV"),
}

# Tiberian Sun's recording of each line, by .AUD name in SPEECH01.MIX (GDI's EVA).
# The numbers are OpenTS's Speech[] table, i.e. EA's own VOX_ ordering.
TS_AUD = {
    "NODEPLY": "00-I016",   # cannot deploy here
    "BCT":     "00-I012",   # battle control terminated
    "WON":     "00-I284",   # you are victorious
    "LST":     "00-I286",   # you have lost
    "SLCT":    "00-I042",   # select target
    "NOPOW":   "00-I024",   # low power (TS has no separate "insufficient power")
}

NEEDLE_LEN = 20


def payload_name(era, tag, chan):
    return "TF_MBX_%s_%s_%s.WAV" % (era, tag, chan)


def wav_format(path):
    d = path.read_bytes()
    i = d.find(b"fmt ")
    tag, ch, rate, bps, align, bits = struct.unpack_from("<HHIIHH", d, i + 8)
    return dict(tag=tag, ch=ch, rate=rate, align=align)


def decode_pcm(path, rate):
    """Any WAV -> mono int16 PCM at `rate`."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
                          "-ar", str(rate), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    pcm = array.array("h")
    pcm.frombytes(raw)
    return list(pcm)


def trim_tail(pcm, floor=48):
    """Drop the trailing pad. Existing payloads are padded with digital silence, and
    re-padding to a new common length must not stack one pad on top of another."""
    end = len(pcm)
    while end > 0 and abs(pcm[end - 1]) <= floor:
        end -= 1
    return pcm[:end]


def ts_pcm(tmp, tag, rate, ts_dir):
    """The Tiberian Sun recording for a line, as mono PCM at `rate`."""
    aud = TS_AUD[tag]
    mix = Path(ts_dir) / "TIBSUN.MIX"
    out = subprocess.run([sys.executable, str(TS_EXTRACT), str(mix), "SPEECH01.MIX",
                          "extract", str(tmp), "%s.AUD" % aud], capture_output=True, text=True)
    if out.returncode != 0 or not (tmp / ("%s.AUD" % aud)).exists():
        sys.exit("could not extract %s from SPEECH01.MIX:\n%s" % (aud, out.stderr))
    wav = tmp / ("%s.wav" % aud)
    subprocess.run([sys.executable, str(AUD_DECODE), str(tmp / ("%s.AUD" % aud)), str(wav)],
                   check=True, capture_output=True)
    return trim_tail(decode_pcm(wav, rate))


def needle_for(data, others, start):
    """A 20-byte run unique inside `data` and absent from every other era's file.

    `start` skips the header and the opening silence, where the eras look alike.
    """
    best = None
    for off in range(start, len(data) - NEEDLE_LEN, 2):
        sl = data[off:off + NEEDLE_LEN]
        spread = len(set(sl))
        if spread < 12:
            continue
        if data.count(sl) != 1:
            continue
        if any(sl in o for o in others):
            continue
        if best is None or spread > best[0]:
            best = (spread, off, sl)
            if spread >= 18:
                break
    if best is None:
        sys.exit("no distinctive needle found; widen the search or re-pad")
    return best[1], best[2]


def build(ts_dir, out_dir):
    rows = []
    for tag, (dst_c, dst_r) in LINES.items():
        for chan, dst in (("C", dst_c), ("R", dst_r)):
            # The RA payload defines the line's shape: same rate and block alignment as
            # the base sample the launcher loaded.
            ra_path = SRC / ("TF_MBX_RA_%s_%s.WAV" % (tag, chan))
            if not ra_path.exists():
                sys.exit("missing frozen source %s (see scripts/eva_work/README.md)" % ra_path)
            fmt = wav_format(ra_path)
            rate, align = fmt["rate"], fmt["align"]
            spb = msadpcm.samples_per_block(align)

            pcm = {}
            for era in ERAS:
                if era == "TS":
                    pcm[era] = ts_pcm(out_dir, tag, rate, ts_dir)
                else:
                    old = SRC / ("TF_MBX_%s_%s_%s.WAV" % (era, tag, chan))
                    if not old.exists():
                        sys.exit("missing frozen source %s (see scripts/eva_work/README.md)" % old)
                    pcm[era] = trim_tail(decode_pcm(old, rate))

            # One common length, rounded up to a whole block so every era encodes to
            # the same number of blocks and therefore the same byte count.
            longest = max(len(p) for p in pcm.values())
            total = ((longest + spb - 1) // spb) * spb

            files = {}
            for era in ERAS:
                padded = pcm[era] + [0] * (total - len(pcm[era]))
                files[era] = msadpcm.wav(padded, rate, align)
            sizes = {len(b) for b in files.values()}
            if len(sizes) != 1:
                sys.exit("era payloads differ in size for %s_%s: %s" % (tag, chan, sizes))

            for era in ERAS:
                (out_dir / payload_name(era, tag, chan)).write_bytes(files[era])

            entries = []
            for era in ERAS:
                others = [files[o] for o in ERAS if o != era]
                # Skip the RIFF header and roughly the first tenth of a second, which is
                # near-silent lead-in on most of these lines.
                start = 64 + (rate // 10) * align // spb
                off, sl = needle_for(files[era], others, start)
                entries.append((era, off, sl))
            rows.append((tag, chan, dst, entries))
            print("  %-8s %s  rate %5d align %3d  %6d bytes x %d eras"
                  % (tag, chan, rate, align, len(files[ERAS[0]]), len(ERAS)))
    return rows


def emit_header(rows, path):
    out = []
    out.append("/*\n"
               "**\tGENERATED by scripts/eva_mailbox_build.py -- do not edit by hand.\n"
               "**\n"
               "**\tThe launcher-fired EVA lines, one row per line and audio channel, with every\n"
               "**\tera's payload: a distinctive 20-byte needle, that needle's offset in the file,\n"
               "**\tand the file itself. All of a row's payloads are the same byte length, which is\n"
               "**\twhat lets the cache overwrite swap one for another in place.\n"
               "*/\n")
    out.append("#define TF_EVA_ERA_COUNT %d\n" % len(ERAS))
    for i, era in enumerate(ERAS):
        out.append("#define TF_EVA_ERA_%s %d\n" % (era, i))
    out.append("#define TF_EVA_NEEDLE_LEN %d\n\n" % NEEDLE_LEN)
    out.append("struct TF_EvaMailboxSlot\n{\n    const unsigned char* needle;\n"
               "    int fileoff;\n    const char* file;\n};\n\n")
    out.append("struct TF_EvaMailboxLine\n{\n    const char* dst;\n"
               "    TF_EvaMailboxSlot era[TF_EVA_ERA_COUNT];\n};\n\n")

    for tag, chan, dst, entries in rows:
        for era, off, sl in entries:
            out.append("static const unsigned char tf_mbx_%s_%s_%s[] = {%s};\n"
                       % (era.lower(), tag.lower(), chan.lower(),
                          ", ".join("0x%02x" % b for b in sl)))
    out.append("\nstatic const TF_EvaMailboxLine TF_EvaMailboxLines[] = {\n")
    for tag, chan, dst, entries in rows:
        slots = ", ".join("{tf_mbx_%s_%s_%s, %d, \"%s\"}"
                          % (era.lower(), tag.lower(), chan.lower(), off,
                             payload_name(era, tag, chan))
                          for era, off, sl in entries)
        out.append("    {\"%s\", {%s}},\n" % (dst, slots))
    out.append("};\n")
    path.write_text("".join(out), encoding="utf-8")
    print("wrote %s (%d lines x %d eras)" % (path.name, len(rows), len(ERAS)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ts-dir", default=str(DEFAULT_TS))
    ap.add_argument("--check", action="store_true", help="build to a temp dir, change nothing")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        print("Building %d lines x 2 channels x %d eras (%s)"
              % (len(LINES), len(ERAS), ", ".join(ERAS)))
        rows = build(args.ts_dir, tmp)
        if args.check:
            print("--check: nothing written")
            return
        for f in tmp.glob("TF_MBX_*.WAV"):
            (AUDIO / f.name).write_bytes(f.read_bytes())
        # The shipped runtime seeds ARE the RA payloads, byte for byte. ClientG caches
        # whatever sits at the launcher's sample name when it starts, so on a fresh install
        # the cached blob is the seed -- and the cache overwrite can only find it if the
        # seed is one of the era payloads at the current length. Drift here and the first
        # session of a new install silently keeps the RA voice.
        for tag, chan, dst, _ in rows:
            src = tmp / payload_name("RA", tag, chan)
            (AUDIO / dst).write_bytes(src.read_bytes())
        emit_header(rows, HEADER)
        print("payloads + %d runtime seeds written to %s" % (len(rows), AUDIO))


if __name__ == "__main__":
    main()
