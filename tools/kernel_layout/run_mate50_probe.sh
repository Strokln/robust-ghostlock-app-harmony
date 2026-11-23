#!/usr/bin/env bash
# OFFLINE RESEARCH ONLY: compile header offsetof probes, never touch device.
set -euo pipefail
headers="${1:?Usage: $0 <extracted-kheaders-dir> [output.s]}"
output="${2:-./mate50-layout.s}"
source_file="${PROBE_SOURCE:-$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/mate50_layout_probe.c}"
[[ -f "$headers/include/generated/autoconf.h" ]] || { echo 'Missing kernel autoconf.h' >&2; exit 2; }
[[ -f "$headers/include/generated/utsrelease.h" ]] || { echo 'Missing UTS release header' >&2; exit 2; }
[[ -f "$source_file" ]] || { echo "Missing probe file: $source_file" >&2; exit 2; }
headers="$(cd "$headers" && pwd)"
resource="$(clang -print-resource-dir)"
shim="$(mktemp -d)"
trap 'rm -rf "$shim"' EXIT
for vendor in chipset_common/hwqos/hwqos_rwsem.h chipset_common/hwcfs/hwcfs_rwsem.h; do
  if [[ ! -f "$headers/$vendor" ]]; then
    mkdir -p "$shim/$(dirname "$vendor")"
    printf '/* OFFLINE-ONLY placeholder, vendor definition unavailable. */\n' > "$shim/$vendor"
    echo "NOTICE: temporary empty include shim: $vendor" >&2
  fi
done
clang --target=aarch64-linux-gnu -S -O0 -fno-builtin -Wno-pointer-sign \
  -nostdinc -isystem "$resource/include" -D__KERNEL__ \
  -I "$shim" \
  -I "$headers/arch/arm64/include" \
  -I "$headers/arch/arm64/include/generated" \
  -I "$headers/include" \
  -I "$headers/arch/arm64/include/uapi" \
  -I "$headers/arch/arm64/include/generated/uapi" \
  -I "$headers/include/uapi" \
  -I "$headers/include/generated/uapi" \
  -include "$headers/include/linux/kconfig.h" \
  "$source_file" -o "$output"
echo "ASSEMBLER=$output"
awk '/^probe_[a-zA-Z0-9_]+:$/ { name=$0; sub(/:$/, "", name); getline; if ($1 == ".xword") print name, $2 }' "$output"
