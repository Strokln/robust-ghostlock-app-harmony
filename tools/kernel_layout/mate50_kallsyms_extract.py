#!/usr/bin/env python3
"""Offline symbol recovery for the exact owner-provided DCO-AL00 boot_42.img.
Pinned SHA-256; no device access, no exploit, no untrusted geometry fallback.
Usage: python3 mate50_kallsyms_extract.py boot_42.img symbols.txt
"""
import hashlib
import struct
import sys
from pathlib import Path

BOOT_HASH = "96344a91f72798adfb8e08a7d0a2725420f97c30ef29cf828a2af2255241d4cf"
IMAGE_HASH = "03537d7f14ad9b44e70a9565115e529d76893328a0ff708034038a5eb958237c"
IMAGE_OFFSET, IMAGE_LENGTH = 4096, 44954580
TOKEN_INDEX = 33779080
TOKEN_TABLE = 33778264
MARKERS = 33775552
NUM_SYMS = 29752432
NAMES = 29752440
OFFSETS = 29059704
BASE = 0xffffffc010000000

def verify_sha(data, expected, what):
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise ValueError(f"{what} SHA mismatch: {actual}")

def recover(boot):
    verify_sha(boot, BOOT_HASH, "boot")
    image = boot[IMAGE_OFFSET:IMAGE_OFFSET + IMAGE_LENGTH]
    verify_sha(image, IMAGE_HASH, "ARM64 Image")
    n, = struct.unpack_from("<Q", image, NUM_SYMS)
    base, = struct.unpack_from("<Q", image, NUM_SYMS - 8)
    if (n, base) != (173179, BASE):
        raise ValueError("Unsupported kallsyms metadata")
    indices = struct.unpack_from("<256H", image, TOKEN_INDEX)
    tokens = []
    for offset in indices:
        begin = TOKEN_TABLE + offset
        end = image.find(b"\0", begin, begin + 100)
        if end < begin or end >= TOKEN_INDEX:
            raise ValueError("Bad kallsyms token table")
        tokens.append(image[begin:end])
    position = NAMES
    result = []
    for i in range(n):
        length = image[position]
        position += 1
        if not length or position + length > MARKERS:
            raise ValueError(f"Bad token name at symbol {i}")
        name = b"".join(tokens[t] for t in image[position:position + length])
        position += length
        if not name or not all(32 <= c < 127 for c in name):
            raise ValueError(f"Bad recovered name at symbol {i}")
        relative, = struct.unpack_from("<i", image, OFFSETS + 4 * i)
        result.append(((base + relative) & 0xffffffffffffffff,
                       chr(name[0]), name[1:].decode("ascii")))
    if position > MARKERS or MARKERS - position > 8:
        raise ValueError("Unexpected compressed names length")
    known = {name: addr for addr, kind, name in result}
    if known.get("init_task") != BASE + 41267456 or known.get("init_cred") != BASE + 41376728:
        raise ValueError("Recovered symbols inconsistent with static kernel objects")
    return result

def main(argv):
    if len(argv) != 2:
        print("Usage: mate50_kallsyms_extract.py boot_42.img symbols.txt", file=sys.stderr)
        return 64
    result = recover(Path(argv[0]).read_bytes())
    Path(argv[1]).write_text("".join(f"{address:016x} {kind} {name}\n"
                                      for address, kind, name in result), encoding="utf-8")
    print(f"Recovered {len(result)} ARM64 kernel symbols")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
