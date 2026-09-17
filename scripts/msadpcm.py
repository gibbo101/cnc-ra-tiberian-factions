#!/usr/bin/env python3
"""Encode 16-bit mono PCM to MS-ADPCM at an ARBITRARY block alignment.

ffmpeg's adpcm_ms encoder refuses any block size that is not a power of two, and
the launcher's teardown speech loader wants the base samples' `block_align = 70`
(128 samples per block). That combination is unreachable through ffmpeg, which is
why the era-mailbox payloads used to mix two padding strategies: re-encoded files
for most lines and a byte-level zero-pad of the base file for the one line that
had to keep its alignment. This module removes that split -- every payload can be
produced at whatever alignment its line already uses.

Format, per block (mono): u8 predictor index, s16 delta, s16 sample1, s16 sample2,
then one 4-bit nibble per remaining sample, high nibble first. So

    block_align = 7 + (samples_per_block - 2) / 2

and 70 bytes is 128 samples. Each block re-primes the predictor, so blocks are
independent and a file can be cut or padded on a block boundary safely.

License: GPL v3.
"""
import struct

ADAPT = [230, 230, 230, 230, 307, 409, 512, 614, 768, 614, 512, 409, 307, 230, 230, 230]
COEF1 = [256, 512, 0, 192, 240, 460, 392]
COEF2 = [0, -256, 0, 64, 0, -208, -232]


def samples_per_block(block_align):
    """Inverse of the layout above; raises if the alignment cannot hold whole samples."""
    if block_align < 7:
        raise ValueError("block_align %d is smaller than the block header" % block_align)
    n = (block_align - 7) * 2 + 2
    if 7 + (n - 2) // 2 != block_align:
        raise ValueError("block_align %d does not map to a whole sample count" % block_align)
    return n


def _clamp16(v):
    return -32768 if v < -32768 else (32767 if v > 32767 else v)


def _encode_block(pcm, predictor):
    """Encode one block with a fixed predictor; returns (bytes, squared error)."""
    c1, c2 = COEF1[predictor], COEF2[predictor]
    sample2, sample1 = pcm[0], pcm[1]

    # Seed the step size from the block's own first difference rather than a constant:
    # too small a delta clips the opening transient, too large blurs quiet lines.
    spread = max(abs(pcm[i + 1] - pcm[i]) for i in range(len(pcm) - 1)) if len(pcm) > 1 else 0
    delta = max(16, spread // 4)

    out = bytearray()
    out.append(predictor)
    out += struct.pack("<hhh", delta, sample1, sample2)

    err = 0
    nibbles = []
    for i in range(2, len(pcm)):
        predict = (sample1 * c1 + sample2 * c2) >> 8
        diff = pcm[i] - predict
        # Round to nearest rather than truncating; truncation biases every sample low.
        n = int(round(diff / delta)) if delta else 0
        n = -8 if n < -8 else (7 if n > 7 else n)
        recon = _clamp16(predict + n * delta)
        err += (pcm[i] - recon) ** 2
        nibbles.append(n & 0xF)
        delta = max(16, (ADAPT[n & 0xF] * delta) >> 8)
        sample2, sample1 = sample1, recon

    for i in range(0, len(nibbles), 2):
        out.append((nibbles[i] << 4) | nibbles[i + 1])
    return bytes(out), err


def encode(pcm, block_align):
    """PCM (list of int16) -> MS-ADPCM data bytes. Length must be a whole number of blocks.

    Each block tries all seven predictor sets and keeps the closest, which is what
    stops the quieter EVA lines from going grainy at small block sizes.
    """
    spb = samples_per_block(block_align)
    if len(pcm) % spb:
        raise ValueError("%d samples is not a whole number of %d-sample blocks" % (len(pcm), spb))
    data = bytearray()
    for start in range(0, len(pcm), spb):
        block = pcm[start:start + spb]
        best = None
        for p in range(7):
            enc, err = _encode_block(block, p)
            if best is None or err < best[1]:
                best = (enc, err)
        assert len(best[0]) == block_align, (len(best[0]), block_align)
        data += best[0]
    return bytes(data)


def wav(pcm, rate, block_align):
    """Full .WAV container around encode(), matching the shape the launcher ships."""
    data = encode(pcm, block_align)
    spb = samples_per_block(block_align)
    # WAVEFORMATEX + MS-ADPCM extension: 7 coefficient pairs.
    ext = struct.pack("<HH", spb, 7)
    for a, b in zip(COEF1, COEF2):
        ext += struct.pack("<hh", a, b)
    fmt = struct.pack("<HHIIHH", 2, 1, rate, rate * block_align // spb, block_align, 4) + \
        struct.pack("<H", len(ext)) + ext
    fact = struct.pack("<I", len(pcm))
    chunks = (b"fmt " + struct.pack("<I", len(fmt)) + fmt
              + b"fact" + struct.pack("<I", len(fact)) + fact
              + b"data" + struct.pack("<I", len(data)) + data
              + (b"\0" if len(data) & 1 else b""))
    return b"RIFF" + struct.pack("<I", 4 + len(chunks)) + b"WAVE" + chunks
