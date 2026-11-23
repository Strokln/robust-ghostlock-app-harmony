#!/usr/bin/env bash
# Build static no-libc Android arm64 executable with LLVM Clang + LLD.
set -euo pipefail
cd "$(dirname "$0")"
command -v clang >/dev/null || { echo "Missing LLVM clang" >&2; exit 2; }
clang --target=aarch64-linux-android31 \
  -ffreestanding -nostdlib -static -fno-stack-protector -O2 \
  -fno-builtin -fno-pic -fuse-ld=lld \
  -Wl,-e,_start -Wl,-z,max-page-size=4096 -Wl,--build-id=none \
  mate50_perf_event_probe.c -o mate50_perf_event_probe_arm64
if command -v readelf >/dev/null; then
    readelf -h mate50_perf_event_probe_arm64 | grep -E 'Class:|Machine:|Type:|Entry point'
    if readelf -l mate50_perf_event_probe_arm64 | grep -q INTERP; then
        echo "ERROR: unexpected dynamic loader" >&2; exit 2
    fi
fi
echo "Built: mate50_perf_event_probe_arm64"
