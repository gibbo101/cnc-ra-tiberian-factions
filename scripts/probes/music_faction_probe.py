#!/usr/bin/env python3
"""Writes a loose MUSICEVENTS.XML: the mod's own (from its CONFIG.MEG) plus a test TS GDI
faction playlist of one TD track, so the faction-music hook can be heard working."""
import os
import subprocess
import sys
import tempfile

MOD = "resources/remaster_mods/Vanilla_RA/Data"
OUT = os.path.join(MOD, "XML/AUDIO/MUSICEVENTS.XML")
TRACKS = {"RAR": "TDR_MUS_Act_On_Instinct.WAV", "RAB": "TDR_MUS_Act_On_Instinct.WAV",
          "RAC": "TDC_MUS_Act_On_Instinct.WAV"}
EVENT = """	<MusicEvent Name="{prefix}_TF_MUS_TSGDI">
		<PlayList>
			<Entry> {track} </Entry>
		</PlayList>
		<VolumePercent> 50 </VolumePercent>
		<FadeInSeconds> 0.0 </FadeInSeconds>
		<ContinueLastSample> No </ContinueLastSample>
		<ContinueLastSampleThreshold> 0.75 </ContinueLastSampleThreshold>
		<FadeOutPrevSeconds> 1.0 </FadeOutPrevSeconds>
		<GapDelayMinSeconds> 5.0 </GapDelayMinSeconds>
		<GapDelayMaxSeconds> 5.0 </GapDelayMaxSeconds>
		<LoopInfinitely> No </LoopInfinitely>
		<RandomizePlayList> False </RandomizePlayList>
	</MusicEvent>

"""

with tempfile.TemporaryDirectory() as tmp:
    subprocess.run([sys.executable, "scripts/meg_extract.py", "extract", os.path.join(MOD, "CONFIG.MEG"),
                    "MUSICEVENTS.XML", tmp], check=True, stdout=subprocess.DEVNULL)
    base = open(os.path.join(tmp, "MUSICEVENTS.XML"), "rb").read().decode("utf-8")
end = base.rindex("</MusicEvents>")
events = "".join(EVENT.format(prefix=p, track=t) for p, t in TRACKS.items())
open(OUT, "w", encoding="utf-8", newline="").write(base[:end] + events + base[end:])
print(f"{OUT}: {len(base)} -> {len(base) + len(events)} bytes")
