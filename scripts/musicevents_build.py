#!/usr/bin/env python3
"""Rebuild MUSICEVENTS.XML with the mod's skirmish music playlist.

Emits the RA_MULTIPLAYER_MODE remastered playlist (`RAR_MUS_RA_MULTIPLAYER_MODE`)
carrying the full mod track list: every remastered RA track, the remastered TD
tracks minus the excluded cues, and the RA+TD bonus tracks.

The Classic (`RAC_`) and Bonus (`RAB_`) playlists pass through untouched, so a
player on Classic audio keeps the mod's established 50/50 RA/TD rotation.

The base is the MUSICEVENTS.XML already inside the mod's CONFIG.MEG, NOT the
pristine game file: the Classic and Bonus playlists carry mod edits of their
own, and rebasing on vanilla would silently revert them to the stock RA-only
rotation.

CONTRACT: the emitted file MUST be byte-for-byte the same length as the base.
MEG member offsets resolve against the base archive, so any size change makes
the launcher abort at startup while parsing the XML header. Slack is reclaimed
from inert commented-out MusicEvent blocks and the remainder is absorbed by a
trailing pad comment.

License: GPL v3.
"""
import re
import sys

EVENT = "RAR_MUS_RA_MULTIPLAYER_MODE"

# Remastered TD tracks excluded from the rotation.
# Menu/title cues and score-screen stingers: all under a minute, they cut in
# and out mid-battle rather than playing as music.
TD_EXCLUDED = {
    "GDI_MAP_THEME", "NOD_MAP_THEME",          # menu / title
    "GREAT_SHOT", "GREAT_SHOT_EXTENDED", "NOD_SCORE",   # score-screen stingers
    "UNTAMED_LAND",                             # excluded by preference
    "REACHING_OUT", "CC_80S_MIX", "HEARTBREAK", # cut from the rotation
}

# Remastered RA tracks excluded from the rotation.
RA_EXCLUDED = {
    "INTRO_MENU", "MAP_THEME",   # menu / title
    "MILITANT_FORCE",            # bonus arrangement carries this theme instead
}


def track_names(music_meg_listing, prefix):
    """Track stems present in MUSIC.MEG under `prefix`, without extension."""
    out = set()
    for line in music_meg_listing:
        name = line.strip().rsplit("\\", 1)[-1]
        if name.upper().startswith(prefix):
            out.add(name.rsplit(".", 1)[0])
    return out


def build_playlist(listing):
    """The ordered track list for the remastered skirmish rotation.

    Remastered RA and TD tracks only. Bonus-mode tracks (RAB_/TDB_) are
    deliberately excluded: they play but never appear in the in-game jukebox,
    which put unlisted oddities like the credits-outtakes bloopers reel into a
    live match.
    """
    ra = track_names(listing, "RAR_")
    td = track_names(listing, "TDR_")

    keep_ra = sorted(t for t in ra if t.upper().replace("RAR_MUS_", "") not in RA_EXCLUDED)
    keep_td = sorted(t for t in td if t.upper().replace("TDR_MUS_", "") not in TD_EXCLUDED)

    # Interleave RA and TD so the rotation alternates eras.
    woven = []
    for i in range(max(len(keep_ra), len(keep_td))):
        if i < len(keep_ra):
            woven.append(keep_ra[i])
        if i < len(keep_td):
            woven.append(keep_td[i])
    return woven


def render_block(base_block, tracks, eol):
    """Replace the PlayList entries of `base_block`, keeping its settings."""
    entries = "".join(f"\t\t\t<Entry> {t}.WAV </Entry>{eol}" for t in tracks)
    return re.sub(
        r"(<PlayList>" + re.escape(eol) + r").*?(\t\t</PlayList>)",
        lambda m: m.group(1) + entries + m.group(2),
        base_block,
        flags=re.S,
    )


def main(base_path, listing_path, out_path):
    # Read as bytes and keep line endings verbatim: the file is CRLF, and text
    # mode would silently drop one byte per line, breaking the size contract.
    raw = open(base_path, "rb").read()
    target_len = len(raw)
    base = raw.decode("utf-8", errors="surrogateescape")
    eol = "\r\n" if b"\r\n" in raw else "\n"
    listing = open(listing_path, encoding="utf-8", errors="replace").readlines()

    tracks = build_playlist(listing)

    m = re.search(rf'(\t<MusicEvent Name="{EVENT}".*?</MusicEvent>)', base, re.S)
    if not m:
        sys.exit(f"ERROR: {EVENT} block not found in base")
    out = base.replace(m.group(1), render_block(m.group(1), tracks, eol))

    def size(s):
        return len(s.encode("utf-8", "surrogateescape"))

    # Reclaim slack from inert commented-out MusicEvent blocks, largest first,
    # until the result fits inside the fixed member size.
    dead = sorted(
        (c for c in re.findall(r"<!--.*?-->", out, re.S) if "<MusicEvent" in c),
        key=len,
        reverse=True,
    )
    for block in dead:
        if size(out) <= target_len:
            break
        out = out.replace(block + eol, "", 1) if block + eol in out else out.replace(block, "", 1)

    grown = size(out)
    if grown > target_len:
        sys.exit(
            f"ERROR: playlist needs {grown - target_len} more bytes than the "
            f"member can hold ({grown} > {target_len}). Cut tracks to fit."
        )

    # Absorb the remainder in a pad comment so the member length is exact.
    marker = "</MusicEvents>"
    pad_needed = target_len - grown
    if pad_needed:
        if pad_needed < len("<!--  -->"):
            sys.exit(f"ERROR: {pad_needed} bytes of slack is too small to pad")
        pad = "<!--" + " " * (pad_needed - len("<!---->")) + "-->"
        out = out.replace(marker, pad + marker, 1)

    final = out.encode("utf-8", "surrogateescape")
    if len(final) != target_len:
        sys.exit(f"ERROR: size {len(final)} != required {target_len}")
    if not final.rstrip().endswith(marker.encode()):
        sys.exit("ERROR: output does not end at the document close tag")

    with open(out_path, "wb") as fh:
        fh.write(final)
    print(f"OK: {len(tracks)} tracks, {len(final)} bytes (matches base exactly)")


if __name__ == "__main__":
    main(*sys.argv[1:4])
