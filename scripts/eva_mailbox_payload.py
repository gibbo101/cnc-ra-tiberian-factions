#!/usr/bin/env python3
"""Build one era-mailbox EVA payload pair (TD + RA) for TF_Mailbox_Write_EVA_Voice.

Both recordings are re-encoded mono MS-ADPCM at the channel rate and padded with trailing
silence to the SAME sample count, so the two files come out byte-equal in length (constant-rate
codec) and the in-process cache overwrite is always same-size. Prints the C needle lines for
TF_Patch_ClientG_Cache: a high-entropy 20-byte slice of real audio from each file plus its
file offset.

  eva_mailbox_payload.py <rate> <td.wav> <ra.wav> <out_dir> <TAG>
    -> <out_dir>/TF_MBX_TD_<TAG>.WAV + TF_MBX_RA_<TAG>.WAV
"""
import os, struct, subprocess, sys, tempfile

def pcm(src, rate):
    out = subprocess.run(['ffmpeg', '-v', 'error', '-i', src, '-ac', '1', '-ar', str(rate),
                          '-f', 's16le', '-'], capture_output=True, check=True).stdout
    return out

def encode(raw, rate, dst):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(rate), '-ac', '1',
                    '-i', '-', '-c:a', 'adpcm_ms', dst], input=raw, check=True)

def data_span(path):
    d = open(path, 'rb').read()
    i = 12
    while i + 8 <= len(d):
        cid = d[i:i+4]; sz = struct.unpack_from('<I', d, i + 4)[0]
        if cid == b'data':
            return d, i + 8, i + 8 + sz
        i += 8 + sz + (sz & 1)
    raise SystemExit('no data chunk in ' + path)

def needle(path, other):
    d, s, e = data_span(path)
    od = open(other, 'rb').read()
    best = None
    # walk the first half of the audio in 1-block steps; skip leading silence
    for off in range(s + 1024, s + (e - s) // 2, 64):
        sl = d[off:off+20]
        ent = len(set(sl))
        if ent < 16 or d.count(sl) != 1 or sl in od:
            continue
        if best is None or ent > best[0]:
            best = (ent, off, sl)
            if ent >= 19:
                break
    if best is None:
        raise SystemExit('no needle in ' + path)
    return best[1], best[2]

def main():
    rate, td, ra, out_dir, tag = int(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]
    a, b = pcm(td, rate), pcm(ra, rate)
    n = max(len(a), len(b))
    n += (-n) % 4096  # whole blocks of samples so both encode to the same block count
    a += b'\0' * (n - len(a)); b += b'\0' * (n - len(b))
    td_out = os.path.join(out_dir, f'TF_MBX_TD_{tag}.WAV')
    ra_out = os.path.join(out_dir, f'TF_MBX_RA_{tag}.WAV')
    encode(a, rate, td_out); encode(b, rate, ra_out)
    st, sr = os.path.getsize(td_out), os.path.getsize(ra_out)
    if st != sr:
        raise SystemExit(f'size mismatch {st} vs {sr}')
    lt = tag.lower()
    for name, path, other in ((f'td_{lt}', td_out, ra_out), (f'ra_{lt}', ra_out, td_out)):
        off, sl = needle(path, other)
        hexs = ', '.join(f'0x{x:02x}' for x in sl)
        print(f'    static const unsigned char {name}[] = {{{hexs}}}; // fileoff {off}')
    print(f'// {tag}: {st} bytes each')

main()
