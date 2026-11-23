#!/usr/bin/env python3
"""Offline P50 GhostLock ELF -> Mate 50 Pro firmware compatibility gate.

No ADB, no exploitation, no device writes, and no runnable exploit output.
Run using: python3 tools/kernel_layout/p50_mate50_gate.py <P50 ELF> <DCO boot.img>
           <DCO HOCON profile> <DCO layout-audit JSON>
Prints a machine-readable compatibility report. Exit status 2 = NOT PORTED.
"""
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

P50_KERNELS = [
    "5.4.86-qgki-g46da5ebe7e3c-dirty",
    "5.4.86-qgki-g0b6800e4a3c5-dirty",
    "5.4.86-qgki-g89b2dfc9cd7e-dirty",
]
P50_TASK = {"real_cred": 0x7b8, "cred": 0x7c0, "comm": 0x7d0}
DCO_BOOT_SHA256 = "96344a91f72798adfb8e08a7d0a2725420f97c30ef29cf828a2af2255241d4cf"


def sha256(path):
    dig = hashlib.sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1 << 20), b""):
            dig.update(block)
    return dig.hexdigest()


def audit(elf, boot, profile, layout):
    with Path(elf).open("rb") as file:
        header = file.read(64)
    if len(header) < 64 or header[:6] != b"\x7fELF\x02\x01":
        raise ValueError("Expected ELF64 little-endian file")
    if struct.unpack_from("<H", header, 18)[0] != 183:
        raise ValueError("Expected AArch64 e_machine=183")

    text = Path(profile).read_text(encoding="utf-8")
    match = re.search(r'(?m)^release\s*=\s*"([^"]+)"', text)
    if not match:
        raise ValueError("Profile is missing exact kernel release")
    release = match.group(1)
    geometry = json.loads(Path(layout).read_text(encoding="utf-8"))
    if geometry.get("kernel_release") != release:
        raise ValueError("Profile and kheaders layout refer to different kernels")
    fields = geometry["task_struct"]["fields"]
    boot_hash = sha256(boot)
    offsets = {name: {"p50": val, "mate50": fields.get(name),
                      "equal": val == fields.get(name)}
               for name, val in P50_TASK.items()}
    return {
        "status": "NOT_PORTED",
        "safe_to_execute_p50_binary_on_mate50": False,
        "mate50_kernel": release,
        "p50_verified_kernels": P50_KERNELS,
        "kernel_exact_match": release in P50_KERNELS,
        "boot_sha256": boot_hash,
        "boot_matches_researched_image": boot_hash == DCO_BOOT_SHA256,
        "p50_exploit_sha256": sha256(elf),
        "struct_offsets": offsets,
        "null_fields_in_unfinished_conf": len(re.findall(
            r'(?m)^\s*[\w.]+\s*=\s*null\s*$', text)),
        "unverified": [
            "5.10 waiter layout and UAF trigger viability",
            "P50-specific KASLR anchors and memory primitives",
            "credential reference restoration and integrity",
            "tested kernel-module load and root path",
        ],
        "not_an_exploit": True,
    }


def main(argv):
    if len(argv) != 4:
        print("Usage: p50_mate50_gate.py P50_ELF DCO_BOOT DCO_CONF LAYOUT_JSON",
              file=sys.stderr)
        return 64
    result = audit(*argv)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 2  # target is not validated, even if structural fields happen to match


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
