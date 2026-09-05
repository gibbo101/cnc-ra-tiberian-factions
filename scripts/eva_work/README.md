# Era-mailbox sources

`src/` holds the **pristine** RA and TD mailbox payloads as they stood before the era count
grew past two. `scripts/eva_mailbox_build.py` reads its RA/TD content from here and never from
the shipped payloads, because the shipped payloads are its own output: reading those back would
put one more ADPCM generation on the recordings every time the builder ran.

These are already padded, re-encoded copies of the base game's samples rather than untouched
originals -- the true sources were not kept when the mailbox was first built. Trimming their
pad and re-encoding costs one extra generation on RA and TD, which is why they are frozen here
rather than regenerated. If the base recordings are ever re-extracted cleanly, replace these.
