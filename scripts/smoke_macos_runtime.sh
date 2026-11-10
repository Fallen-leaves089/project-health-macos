#!/bin/sh
set -eu

sw_vers
uname -m
arch
sysctl -in sysctl.proc_translated 2>/dev/null || true
sysctl -n machdep.cpu.brand_string 2>/dev/null || true
sysctl -n hw.ncpu
sysctl -n hw.memsize
/bin/bash --version | head -n 1
xcodebuild -version 2>/dev/null || true
xcrun --show-sdk-version 2>/dev/null || true

tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/project-health-smoke.XXXXXX")
trap 'rm -rf "$tmp_dir"' EXIT HUP INT TERM

printf 'old-value\n' > "$tmp_dir/sample.txt"
sed -i '' 's/old-value/new-value/' "$tmp_dir/sample.txt"
test "$(cat "$tmp_dir/sample.txt")" = "new-value"

stat -f '%Sp %Su:%Sg %N' "$tmp_dir/sample.txt" >/dev/null
shasum -a 256 "$tmp_dir/sample.txt" >/dev/null
command -v lsof >/dev/null
command -v xattr >/dev/null
command -v codesign >/dev/null
command -v launchctl >/dev/null
command -v xcrun >/dev/null

printf 'runtime-smoke: PASS\n'
