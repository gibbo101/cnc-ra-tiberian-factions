#!/usr/bin/env python3
'''
Reader for the ENCRYPTED Red Alert MIX format (the format mix_tools.py
cannot read). Used one-shot to pull RA's palette assets (PALETTE.CPS,
TEMPERAT.PAL, ...) out of REDALERT.MIX so the classic-mode SHP palette
remap can target RA's real palette + house-color "unity" indices.

Crypto chain (mirrors common/mixfile.h + pk.cpp + blowfish.cpp):
  1. 4-byte "alternate" header: First==0, Second bitfield. bit 0x02 = encrypted.
  2. 80-byte PK-encrypted block. Decrypt with WW public key (exponent 65537,
     320-bit modulus from redalert/const.cpp Keys[]). Crypt_Block_Size=40,
     Plain_Block_Size=39 -> 2 blocks -> 78 plaintext bytes; first 56 = Blowfish key.
  3. Blowfish-ECB decrypt the index header: count(u16) + datasize(u32) + count*12
     SubBlocks (crc i32, offset u32, size u32). File consumes roundup8(6+count*12).
  4. File DATA is plaintext, starting right after the (padded) encrypted header.

Usage:
  ra_mix_extract.py extract <mixfile> <filename> <outdir>
  ra_mix_extract.py list    <mixfile>          (raw crc/offset/size, no names)

License: GPL v3 (inherited from Vanilla Conquer base).
'''
import base64
import os
import struct
import sys

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from mix_tools import ww_crc

try:
    from mix_namedb import resolve as resolve_name
except Exception:
    def resolve_name(crc, **kw):
        return None

# redalert/const.cpp Keys[] "[PublicKey]" 1=...  (DER: 0x02 tag, len, big-endian modulus)
_PUBKEY_B64 = "AihRvNoIbTn85FZRYNZRcT+i6KpU+maCsEqr3Q5q+LDB5tH7Tz2qQ38V"
_PK_EXPONENT = 65537


def _load_pubkey_modulus():
    raw = base64.b64decode(_PUBKEY_B64)
    assert raw[0] == 0x02, f"unexpected DER tag {raw[0]:#x}"
    length = raw[1]
    modulus = int.from_bytes(raw[2:2 + length], 'big')
    return modulus


def _pk_block_sizes(modulus):
    bit_precision = modulus.bit_length() - 1
    plain = (bit_precision - 1) // 8
    crypt = plain + 1
    return plain, crypt


def _pk_decrypt(blob, modulus, plain, crypt):
    out = bytearray()
    for i in range(0, len(blob) - crypt + 1, crypt):
        c = int.from_bytes(blob[i:i + crypt], 'little')
        m = pow(c, _PK_EXPONENT, modulus)
        out += m.to_bytes(plain, 'little')
    return bytes(out)


def _blowfish_decrypt(key, data):
    # Whole 8-byte ECB blocks only; WW uses standard Blowfish (big-endian words).
    cipher = Cipher(algorithms.Blowfish(key), modes.ECB())
    dec = cipher.decryptor()
    n = (len(data) // 8) * 8
    return dec.update(data[:n]) + dec.finalize()


def read_encrypted_mix(path):
    '''Return (count, datasize, [(crc, offset, size), ...], data_start, raw_bytes).'''
    with open(path, 'rb') as f:
        raw = f.read()

    first, second = struct.unpack_from('<hh', raw, 0)
    if first != 0:
        raise ValueError("not an extended-format mix (First != 0)")
    if not (second & 0x02):
        raise ValueError("mix is not encrypted; use mix_tools.py instead")

    modulus = _load_pubkey_modulus()
    plain, crypt = _pk_block_sizes(modulus)

    pk_blob = raw[4:4 + 80]
    pk_plain = _pk_decrypt(pk_blob, modulus, plain, crypt)
    bf_key = pk_plain[:56]

    enc_header = raw[4 + 80:]
    # First decrypt one block to learn count, then the full header span.
    first_block = _blowfish_decrypt(bf_key, enc_header[:8])
    count, datasize = struct.unpack_from('<HI', first_block, 0)

    header_bytes = 6 + count * 12
    span = ((header_bytes + 7) // 8) * 8
    header_plain = _blowfish_decrypt(bf_key, enc_header[:span])

    entries = []
    for i in range(count):
        off = 6 + i * 12
        crc, offset, size = struct.unpack_from('<iII', header_plain, off)
        entries.append((crc, offset, size))

    data_start = 4 + 80 + span
    return count, datasize, entries, data_start, raw


def _parse_mix_blob(blob):
    '''Parse a mix held in memory (encrypted or classic). Returns
    (entries, data_start, raw) or None if it doesn't parse as a mix.'''
    if len(blob) < 6:
        return None
    first, second = struct.unpack_from('<hh', blob, 0)
    if first == 0 and (second & 0x02):
        import tempfile
        tf = tempfile.NamedTemporaryFile(delete=False, suffix='.mix')
        tf.write(blob)
        tf.close()
        try:
            _, _, entries, data_start, raw = read_encrypted_mix(tf.name)
        except Exception:
            # A nested data blob can coincidentally start with First==0 &
            # encrypted-flag but not actually be an encrypted mix (the RSA
            # "decrypt" then overflows). Treat as not-a-mix so recursion
            # continues to the real nested containers instead of crashing.
            return None
        finally:
            os.unlink(tf.name)
        return entries, data_start, raw
    count, _ = struct.unpack_from('<HI', blob, 0)
    data_start = 6 + count * 12
    if count == 0 or data_start > len(blob):
        return None
    entries = []
    for i in range(count):
        crc, offset, size = struct.unpack_from('<iII', blob, 6 + i * 12)
        # Bounds check rejects random data masquerading as a classic header.
        if offset < 0 or size < 0 or data_start + offset + size > len(blob):
            return None
        entries.append((crc, offset, size))
    return entries, data_start, blob


def find_in_mix(blob, target_crc, _seen=None):
    '''Recursively search a (possibly nested-container) mix for an entry
    whose CRC matches target_crc. Returns the file bytes or None.'''
    parsed = _parse_mix_blob(blob)
    if parsed is None:
        return None
    entries, data_start, raw = parsed
    nested = []
    for crc, offset, size in entries:
        sub = raw[data_start + offset:data_start + offset + size]
        if (crc & 0xFFFFFFFF) == (target_crc & 0xFFFFFFFF):
            return sub
        if size > 64:
            nested.append(sub)
    for sub in nested:
        hit = find_in_mix(sub, target_crc)
        if hit is not None:
            return hit
    return None


def cmd_list(args):
    with open(args[0], 'rb') as f:
        blob = f.read()
    parsed = _parse_mix_blob(blob)
    if parsed is None:
        print('could not parse as a mix (encrypted or classic)', file=sys.stderr)
        return 1
    entries, data_start, raw = parsed
    known = 0
    nested = 0
    for crc, offset, size in entries:
        name = resolve_name(crc)
        if name:
            known += 1
        label = name if name else '(unknown)'
        if name and name.lower().endswith('.mix'):
            nested += 1
            label += '   <-- nested container'
        print(f'  crc={crc & 0xFFFFFFFF:#010x} size={size:>9d}  {label}')
    print(f'  -- {len(entries)} entries, {known} names resolved, {nested} nested .mix',
          file=sys.stderr)
    return 0


def cmd_extract(args):
    if len(args) < 3:
        print('usage: ra_mix_extract.py extract <mixfile> <filename> <outdir>', file=sys.stderr)
        return 2
    mixfile, filename, outdir = args[:3]
    with open(mixfile, 'rb') as f:
        blob = f.read()
    target = ww_crc(filename)
    data = find_in_mix(blob, target)
    if data is None:
        print(f'no entry matching CRC of "{filename}" ({target & 0xFFFFFFFF:#010x})', file=sys.stderr)
        return 1
    os.makedirs(outdir, exist_ok=True)
    outpath = os.path.join(outdir, filename)
    with open(outpath, 'wb') as f:
        f.write(data)
    print(f'extracted {filename} ({len(data)} bytes) -> {outpath}')
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    cmd, args = argv[1], argv[2:]
    if cmd == 'list':
        return cmd_list(args)
    if cmd == 'extract':
        return cmd_extract(args)
    print(f'unknown command: {cmd}', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
