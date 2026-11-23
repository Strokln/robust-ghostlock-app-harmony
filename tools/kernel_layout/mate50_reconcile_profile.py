#!/usr/bin/env python3
"""Conservative DCO-AL00 profile reconciliation against owner-verified kernel headers.

This does not create a runnable/root-ready profile. It only replaces eight
unknown task_struct fields after verifying the exact owner-supplied boot image.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

BOOT_SHA256 = "96344a91f72798adfb8e08a7d0a2725420f97c30ef29cf828a2af2255241d4cf"
RELEASE = "5.10.136-gfdd4fb7e74b6-dirty"
TASK_OFFSETS = {
    "pi_lock": 2188,
    "pi_waiters": 2208,
    "pi_top_task": 2224,
    "pi_blocked_on": 2232,
    "pid": 1504,
    "tgid": 1508,
    "atomic_flags": 1448,
    "tasks": 1248,
}

def reconcile(profile_text: str, boot_sha256: str):
    if boot_sha256 != BOOT_SHA256:
        raise ValueError("boot SHA-256 mismatch: refusing foreign firmware")
    release = re.search(r'^release\s*=\s*"([^"]+)"\s*$', profile_text, re.M)
    if not release or release.group(1) != RELEASE:
        raise ValueError("wrong or absent kernel release")
    if not re.search(r'^kernel_phys_load\s*=\s*\{\s*HWDCO\s*=\s*2818572288\s*\}', profile_text, re.M):
        raise ValueError("unexpected DCO-AL00 physical-memory declaration")
    match = re.search(r'(?m)^task_struct\s*\{\s*\n(?P<body>.*?)^\}', profile_text, re.S)
    if not match:
        raise ValueError("missing task_struct block")
    body = match.group("body")
    changed = []
    for key, value in TASK_OFFSETS.items():
        pattern = rf'(?m)^(\s*{re.escape(key)}\s*=\s*)(null|\d+)(\s*)$'
        hits = list(re.finditer(pattern, body))
        if len(hits) != 1:
            raise ValueError(f"missing or repeated task_struct.{key}")
        current = hits[0].group(2)
        if current not in ("null", str(value)):
            raise ValueError(f"contradictory task_struct.{key}={current}; expected {value}")
        if current == "null":
            body = re.sub(pattern, lambda m: m.group(1) + str(value) + m.group(3), body)
            changed.append(key)
    profile = profile_text[:match.start("body")] + body + profile_text[match.end("body"):]
    remaining = re.findall(r'(?m)^\s*[A-Za-z_][A-Za-z_0-9]*\s*=\s*null\s*$', profile)
    prefix = (
        "# EVIDENCE RECONCILIATION ONLY: NOT VERIFIED FOR ROOT; DO NOT EXECUTE\n"
        "# Derived from compiled headers of SHA-256 pinned DCO-AL00 boot_42.img.\n"
        "# Does NOT validate KASLR, select_stack, credential restoration or phys offset.\n"
    )
    report = {
        "status": "INCOMPLETE_NOT_SAFE_FOR_ROOT",
        "device": "HWDCO / DCO-AL00",
        "kernel_release": RELEASE,
        "boot_sha256": boot_sha256,
        "filled_task_struct_fields": {key: TASK_OFFSETS[key] for key in changed},
        "supported_task_struct_fields": TASK_OFFSETS,
        "remaining_null_count": len(remaining),
        "unresolved_critical": ["kernel_phys_offset", "cred.*", "select_stack runtime geometry"],
        "no_root_attempted": True,
    }
    return prefix + profile, report

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", type=Path, required=True)
    ap.add_argument("--boot", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    args = ap.parse_args()
    boot_hash = hashlib.file_digest(args.boot.open("rb"), "sha256").hexdigest()
    result, report = reconcile(args.profile.read_text(encoding="utf-8"), boot_hash)
    args.out.write_text(result, encoding="utf-8")
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{report['status']}: filled={len(report['filled_task_struct_fields'])}; "
          f"remaining_null={report['remaining_null_count']}")
    print(f"profile={args.out} report={args.report}")

if __name__ == "__main__":
    main()
