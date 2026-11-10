#!/bin/sh
set -eu

os_version=$(sw_vers -productVersion)
hardware_arch=$(uname -m)
process_arch=$(arch)
translated=$(sysctl -in sysctl.proc_translated 2>/dev/null || printf 'unknown')
chip=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || printf 'unknown')

printf 'macOS: %s\n' "$os_version"
printf 'hardware_arch: %s\n' "$hardware_arch"
printf 'process_arch: %s\n' "$process_arch"
printf 'rosetta_translated: %s\n' "$translated"
printf 'chip: %s\n' "$chip"

if [ "$hardware_arch" != "arm64" ] || [ "$process_arch" != "arm64" ]; then
  printf 'ERROR: project-health-macos requires a native arm64 process.\n' >&2
  exit 1
fi

if [ "$translated" != "0" ]; then
  printf 'ERROR: Rosetta translation is active or could not be ruled out.\n' >&2
  exit 1
fi

printf 'environment: PASS (native Apple Silicon)\n'
