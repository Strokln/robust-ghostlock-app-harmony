#!/usr/bin/env bash
# Huawei Mate 50 Pro READ-ONLY runtime probe. Run on macOS/Linux with adb.
# No exploitation, modification, flashing, reboot or privileged operations.
set -euo pipefail
ADB=(adb)
if [[ -n "${ADB_SERIAL:-}" ]]; then ADB+=( -s "$ADB_SERIAL" ); fi
if ! "${ADB[@]}" get-state >/dev/null 2>&1; then
  echo "ERROR: ADB device not connected or authorized" >&2
  exit 2
fi
output="${1:-mate50-runtime-probe.txt}"
"${ADB[@]}" shell 'set +e
printf "## TARGET\n"
printf "uname_r="; uname -r
printf "uname_m="; uname -m
for key in ro.product.model ro.product.device ro.build.version.release ro.build.version.sdk ro.build.display.id ro.build.version.incremental ro.boot.verifiedbootstate ro.boot.vbmeta.device_state ro.boot.flash.locked ro.boot.veritymode; do
  printf "%s=" "$key"; getprop "$key" 2>/dev/null
done
printf "## SECURITY\n"
printf "identity="; id 2>/dev/null
printf "selinux="; getenforce 2>/dev/null
printf "## KERNEL FEATURES\n"
for key in CONFIG_FUTEX_PI CONFIG_KALLSYMS CONFIG_KALLSYMS_ALL CONFIG_RANDOMIZE_BASE CONFIG_CFI_CLANG CONFIG_ARM64_PTR_AUTH CONFIG_ARM64_BTI CONFIG_MODULES CONFIG_MODULE_SIG_FORCE CONFIG_DEBUG_INFO_BTF CONFIG_IKHEADERS; do
  if [ -r /proc/config.gz ]; then
    value=$(zcat /proc/config.gz 2>/dev/null | grep -m 1 -E "^$key=(y|m|n)$|^# $key is not set$" | head -1)
    if [ -n "$value" ]; then printf "%s\n" "$value"; else printf "%s=unknown\n" "$key"; fi
  else
    printf "%s=unavailable (/proc/config.gz unreadable)\n" "$key"
  fi
done
printf "## READABILITY\n"
for path in /proc/kallsyms /sys/kernel/btf/vmlinux /sys/kernel/kheaders.tar.xz /proc/config.gz; do
  if [ -r "$path" ]; then mode=readable; elif [ -e "$path" ]; then mode=exists_not_readable; else mode=missing_or_restricted; fi
  printf "%s=%s\n" "$path" "$mode"
done
' | sed 's/\r$//' | tee "$output"
if [[ ! -s "$output" ]]; then echo "ERROR: no output received" >&2; exit 3; fi
printf '\nSAVED: %s\n' "$output"
printf 'IMPORTANT: this read-only check is NOT evidence of root or exploitability.\n'
