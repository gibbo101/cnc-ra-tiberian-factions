#!/usr/bin/env python3
"""Decode a Westwood .AUD (Tiberian Sun / RA era) to a 16-bit PCM .WAV.

AUD header: u16 sample_rate, u32 comp_size, u32 out_size, u8 flags,
u8 compression. flags bit0 = stereo, bit1 = 16-bit samples. compression 99
(0x63) = IMA ADPCM in DEAF-tagged chunks, 1 = Westwood's own RLE/delta codec.

Each chunk: u16 comp_size, u16 out_size, u32 id (0x0000DEAF), then payload.
The IMA predictor and step index run CONTINUOUSLY across chunk boundaries --
resetting them per chunk is the classic way to get a track that starts clean
and degrades into noise.

Output is plain PCM. The launcher's Data/AUDIO override slot needs MS-ADPCM
(fmt tag 2) instead, so pipe the result through:

    ffmpeg -i out.wav -c:a adpcm_ms -ar <rate> TDR_SFX_<HOST>.WAV

Usage:  ts_aud_decode.py IN.AUD OUT.WAV
"""
import struct, sys, wave

_STEP = [
    7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 21, 23, 25, 28, 31, 34, 37, 41,
    45, 50, 55, 60, 66, 73, 80, 88, 97, 107, 118, 130, 143, 157, 173, 190,
    209, 230, 253, 279, 307, 337, 371, 408, 449, 494, 544, 598, 658, 724,
    796, 876, 963, 1060, 1166, 1282, 1411, 1552, 1707, 1878, 2066, 2272,
    2499, 2749, 3024, 3327, 3660, 4026, 4428, 4871, 5358, 5894, 6484, 7132,
    7845, 8630, 9493, 10442, 11487, 12635, 13899, 15289, 16818, 18500,
    20350, 22385, 24623, 27086, 29794, 32767,
]
_INDEX = [-1, -1, -1, -1, 2, 4, 6, 8]


def _ima(nibble, state):
    """One IMA-ADPCM nibble -> one 16-bit sample; state = [predictor, index]."""
    pred, idx = state
    step = _STEP[idx]
    diff = step >> 3
    if nibble & 1:
        diff += step >> 2
    if nibble & 2:
        diff += step >> 1
    if nibble & 4:
        diff += step
    if nibble & 8:
        pred -= diff
    else:
        pred += diff
    pred = max(-32768, min(32767, pred))
    idx = max(0, min(len(_STEP) - 1, idx + _INDEX[nibble & 7]))
    state[0], state[1] = pred, idx
    return pred


def decode(path):
    d = open(path, 'rb').read()
    rate, comp_size, out_size, flags, comp = struct.unpack_from('<HIIBB', d, 0)
    if comp != 99:
        raise SystemExit(f'{path}: compression {comp} unsupported (only 99 = IMA ADPCM)')
    channels = 2 if (flags & 1) else 1
    pcm = bytearray()
    state = [0, 0]          # predictor + step index, continuous across chunks
    off = 12
    while off + 8 <= len(d) and len(pcm) < out_size:
        csize, usize, cid = struct.unpack_from('<HHI', d, off)
        off += 8
        chunk = d[off:off + csize]
        off += csize
        for byte in chunk:
            pcm += struct.pack('<h', _ima(byte & 0x0F, state))
            pcm += struct.pack('<h', _ima(byte >> 4, state))
    return rate, channels, bytes(pcm[:out_size] if out_size else pcm)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    rate, channels, pcm = decode(src)
    with wave.open(dst, 'wb') as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(pcm)
    print(f'{src}: {rate} Hz, {channels}ch, {len(pcm)} PCM bytes -> {dst}')


if __name__ == '__main__':
    main()
