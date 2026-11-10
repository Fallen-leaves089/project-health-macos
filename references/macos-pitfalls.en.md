# Common and Hidden macOS Traps (Apple Silicon M1 through M6)

[中文](macos-pitfalls.md) | [English](macos-pitfalls.en.md)

This file collects macOS issues that can change project review, builds, tests, containers, delivery, or security conclusions. It is not a chip encyclopedia; the goal is to prevent false passes, false failures, and incorrect attribution on Apple Silicon.

> As of **2026-11-10**, Apple's public lineup includes **M6** (Mac mini, MacBook Pro, iMac) and **M5 Ultra** (Mac Studio); the latest macOS is **macOS 27 (Golden Gate)**. GitHub's free macOS `macos-latest` runner does not guarantee a fixed chip. This repository observed **macOS 26.7.2 / Apple M2 Pro (Virtual) / 5 logical CPUs / 14 GiB / Xcode 26.6 / arm64 / Rosetta 0**, not M6 and not Intel. Do not hard-code M1. Sources are listed at the end.

## 0. Hard gate before a formal review

This skill accepts native Apple Silicon only:

```bash
test "$(uname -m)" = "arm64"
test "$(arch)" = "arm64"
test "$(sysctl -in sysctl.proc_translated)" = "0"
```

If any check fails, stop the formal review. `x86_64` means a Rosetta terminal or an Intel Mac. Rosetta contaminates dependency architecture; Intel is outside the skill's scope. Record:

```bash
sw_vers
uname -m
sysctl -n machdep.cpu.brand_string
system_profiler SPHardwareDataType | grep -E 'Chip|Memory|Model Name'
```

Do not infer the chip from the macOS version, and do not infer the absence of Rosetta from `uname -m` alone. Verify both separately.

## 1. Chip generations and what they mean for reviews

| Generation | Time and representative systems | What actually matters during a review |
|---|---|---|
| M1 / M1 Pro / Max / Ultra | 2020–2022 | The first arm64 ecosystem wave. Some container images, Python wheels, Node native modules, and JDKs still use Rosetta or provide x86_64 only. GitHub may allocate different generations; do not assume M1. |
| M2 / M2 Pro / Max / Ultra | 2022–2023 | Same `arm64` ABI. Do not invent a new build target for a chip generation; differences are mostly GPU, media engines, and chassis thermals. The GitHub macOS 26 runner observed on 2026-11-10 reported M2 Pro (Virtual). |
| M3 / M3 Pro / Max | 2023–2024 | 3 nm generation with newer OS/Xcode floors. GPU/Metal and ML feature availability may depend on SDK and OS, not only the chip name. M3 Ultra arrived in 2025 and is still `arm64`. |
| M4 / M4 Pro / Max | 2024–2025 | Still `arm64`. Larger unified memory and GPU changes alter performance baselines; do not reuse fixed M1 thread counts. |
| M5 / M5 Pro / Max / Ultra | 2025–2026 | M5 Pro/Max arrived in March 2026 and M5 Ultra in August 2026. High core counts can oversubscribe tests; bound CPU/GPU/Neural Engine work and record a fresh baseline. |
| M6 | 2026 | 2 nm, 12-core CPU/GPU, Dual 16-core Neural Engine; ships with macOS 27. The GitHub runner observed here was not M6. Test new GPU/Neural Engine, newest SDK, or macOS 27 behavior on real target hardware. |

**Key conclusion:** M1 through M6 share the `arm64` ABI. Most CLI, server, and build outputs run across generations. "Different chip generation" is not "different binary architecture". The real reasons to test per generation are performance, GPU/Metal, Neural Engine, media encoding, newest SDKs, and OS permission behavior.

## 2. Rosetta and mixed architectures (the easiest false pass)

**Symptom:** the terminal, IDE, CI step, or parent process runs under Rosetta, so `uname -m` reports `x86_64`; Python wheels, Node native modules, Homebrew packages, and binaries are then x86_64. Commands still run, but performance and compatibility conclusions are invalid.

**Hidden part:** `arch`, `file`, `python3`, `node`, and `java` may report different architectures. A child process normally inherits translation when the parent is translated.

**Correct approach:**

```bash
sysctl -in sysctl.proc_translated
arch
file "$(command -v python3)"
python3 -c 'import platform; print(platform.machine())'
node -p 'process.arch'
java -XshowSettings:properties -version 2>&1 | grep 'os.arch'
lipo -info <binary-or-dylib>
```

Rebuild dependencies in a native arm64 terminal. Do not run the formal regression with `arch -x86_64`, and do not put Rosetta-only results into a delivery decision.

## 3. Homebrew prefixes and PATH shadowing

**Symptom:** native Homebrew lives under `/opt/homebrew`, while Rosetta Homebrew may live under `/usr/local`. With both installed, `which brew`, `which python3`, and `which node` may point to different architectures.

```bash
command -v brew
brew --prefix
brew config
brew doctor
```

Never hard-code `/opt/homebrew/bin`. Resolve it with `brew --prefix`, and inspect `PATH` for a second prefix. In CI, use a setup action or an explicit absolute path rather than relying on login-shell initialization files.

## 4. BSD userland is not GNU

**Common failure:** Linux habits such as `sed -i`, `stat -c`, `date -d`, `readlink -f`, `find -printf`, `sha256sum`, and `timeout` either fail or behave differently.

```bash
sed -i '' 's/old/new/' file
stat -f '%Sp %Su:%Sg %N' file
date -r 0
shasum -a 256 file
python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' file
gtimeout 30 <command>   # only after installing coreutils
```

**Hidden part:** a script can pass in an interactive shell because the developer installed GNU tools, then fail on CI or a clean Mac. Verify on a clean environment. Do not assume `gsed`, `gstat`, or `gtimeout` exists.

## 5. System bash is still 3.2

**Symptom:** a script passes on the developer machine using Homebrew bash 5, then fails under `/bin/bash` or CI because associative arrays, `mapfile`, `wait -n`, or `${var,,}` are unavailable.

```bash
/bin/bash --version
command -v bash
```

Prefer `#!/bin/sh`. When bash features are required, use `#!/usr/bin/env bash` and pin a version in CI. Do not depend on a user's `.zshrc` or interactive aliases.

## 6. APFS case behavior and Unicode normalization

**Symptom:** the default APFS volume is usually case-insensitive, so `README.md` and `readme.md` may resolve to the same file. macOS also normalizes Unicode differently from byte-oriented Linux filesystems. Git's `core.ignorecase` and `core.precomposeUnicode` can hide case-only or composed-character differences.

```bash
diskutil info / | grep -i 'File System Personality'
git config --show-origin --get core.ignorecase
git config --show-origin --get core.precomposeUnicode
find . -maxdepth 2 -print | LC_ALL=C sort
```

For case-only renames, cross-platform sync, resource paths, or import casing, recheck on a case-sensitive APFS volume or Linux. A clean `git status` alone does not prove path compatibility.

## 7. Gatekeeper, quarantine, codesign, and notarization

**Symptom:** downloaded binaries, `.app`, `.dmg`, or scripts receive `com.apple.quarantine` and are blocked by Gatekeeper. Teams often remove the attribute globally, allowing unverified artifacts into the build chain.

```bash
xattr -p com.apple.quarantine <file>
codesign -dv --verbose=4 <app-or-binary>
codesign --verify --deep --strict --verbose=2 <app-or-binary>
spctl --assess --type execute --verbose=4 <app-or-binary>
xcrun stapler validate <app-or-dmg>
shasum -a 256 <file>
```

"Unsigned or not notarized" and "malicious" are different conclusions. Do not turn a `spctl` failure into a malware claim. Release artifacts need signature and notarization verification. Local builds may be ad-hoc signed, but must not be presented as distributable signatures. Never recommend disabling Gatekeeper or SIP.

## 8. TCC, SIP, and automation permissions

**Symptom:** access to Desktop, Documents, Downloads, Photos, Contacts, Calendars, screen recording, or automation of another app triggers a TCC prompt. CI, SSH, headless sessions, or a logged-out user may fail immediately. SIP also blocks writes to system paths and protected files.

Review rules:

- Explain why a permission is needed, then request the minimum; do not ask for Full Disk Access just to run tests.
- A TCC denial is an environment limitation, not automatically a code bug. Record it as uncovered.
- Do not disable SIP, lower Gatekeeper, or use `sudo` to modify system directories as a workaround.
- GUI automation, AppleScript, `screencapture`, and Accessibility permissions are especially unreliable on GitHub runners and must be listed as uncovered.

## 9. launchd is not systemd

**Symptom:** applying Linux `systemctl`, `service`, or `journalctl` to macOS; or using deprecated `launchctl load/unload`, so the service is invisible in another login session.

```bash
launchctl print gui/$(id -u)/<label>
launchctl print system/<label>
launchctl bootstrap gui/$(id -u) <plist>
launchctl bootout gui/$(id -u)/<label>
```

State whether the service belongs to `gui/$UID` or the `system` domain. Verify plist path, log paths, environment, and executable permissions. Do not treat a service that needs a logged-in GUI session as testable in CI.

## 10. Docker Desktop, image architecture, and volume performance

**Symptom:** Apple Silicon pulls arm64 images by default. Images available only as amd64 run through QEMU, slowly and sometimes differently. `localhost` inside a container is not the host. Large bind mounts may be extremely slow.

```bash
docker context ls
docker version --format 'client={{.Client.Arch}} server={{.Server.Arch}}'
docker image inspect <image> --format '{{.Architecture}}/{{.Os}}'
docker run --rm <image> uname -m
```

Rules:

- Record client, server, and image architecture; do not check only one.
- Use `--platform linux/amd64` only when no arm64 image exists, and document emulation effects.
- From a container, prefer `host.docker.internal` for the host; do not assume `localhost` points to it.
- Do not put `node_modules`, database files, or many small files on a macOS bind mount without measurement. Compare named volumes, an ignored project directory, or VM-native storage.
- Colima and Docker Desktop do not have identical contexts, networking, or volume behavior. Revalidate after switching.

## 11. Ports, processes, and permissions

```bash
lsof -nP -iTCP:<port> -sTCP:LISTEN
ps -axo pid,ppid,comm,args
pgrep -fl <name>
kill -TERM <pid>
```

Linux habits such as `ss` and `netstat -tulpn` do not transfer directly. If `lsof` cannot see another user's or a protected process, check permissions and TCC before adding `sudo` or sending repeated kills.

## 12. Archives, extended attributes, resource forks, and symlinks

**Symptom:** ordinary `zip`/`tar` creation and extraction lose signatures, quarantine, executable bits, symlinks, or extended attributes. macOS also creates `__MACOSX` and `._*` entries that pollute artifacts.

```bash
ditto -c -k --keepParent <dir> <archive>.zip
ditto -x -k <archive>.zip <dest>
xattr -l <path>
find <dir> -type l -print
```

After delivery, extract in a clean directory and re-verify signature, permissions, links, and hashes. `COPYFILE_DISABLE=1` can reduce AppleDouble metadata, but it is not a substitute for artifact verification.

## 13. Multi-language toolchain architecture

### Python

```bash
python3 -c 'import platform; print(platform.machine())'
python3 -m pip debug --verbose | grep -i 'tags'
```

A virtual environment can inherit Rosetta architecture. `pip` may install universal2, arm64, or x86_64 wheels. Record both the interpreter and extension architecture, not only `python3 --version`.

### Node

```bash
node -p 'process.arch'
npm config get arch
printenv npm_config_arch 2>/dev/null || true
```

Native modules such as `node-gyp`, sharp, canvas, and SQLite commonly fail after an architecture mismatch. Delete `node_modules` and reinstall under native arm64; do not copy caches across architectures.

### Java

```bash
/usr/libexec/java_home -V
java -XshowSettings:properties -version 2>&1 | grep -E 'os.arch|java.home'
```

JDK, JNI libraries, and base images must share an architecture. Changing only `JAVA_HOME` without reinstalling JNI dependencies can still load the wrong `.dylib`.

### Dynamic libraries

```bash
file <binary-or-dylib>
lipo -info <binary-or-dylib>
otool -L <binary-or-dylib>
```

Re-sign after modifying a dylib. `DYLD_LIBRARY_PATH` may be ignored by protected processes or under SIP. Do not treat environment injection as a long-term compatibility solution.

## 14. Xcode, Command Line Tools, and SDKs

**Symptom:** `xcode-select -p` points to Command Line Tools while the project needs full Xcode; multiple Xcodes make `xcodebuild` use the wrong one; an unaccepted CLT license causes an opaque CI failure.

```bash
xcode-select -p
xcodebuild -version
xcrun --show-sdk-path
sudo xcodebuild -license check
```

Record Xcode, SDK, Command Line Tools, and `MACOSX_DEPLOYMENT_TARGET`. Do not run `sudo xcode-select -s` or `xcodebuild -runFirstLaunch` without stating the impact. On Apple Silicon, verify target architecture and signing settings; "it compiled" is not enough.

## 15. Do not reuse performance baselines across generations

M1 through M6 differ significantly in CPU/GPU cores, unified-memory bandwidth, and Neural Engine size. Copying fixed M1 worker counts, connection pools, parallel test counts, or Docker CPU limits to M5/M6 can cause contention, timeouts, or false performance regressions.

```bash
sysctl -n hw.ncpu
sysctl -n hw.memsize
vm_stat
sysctl -n machdep.cpu.brand_string
```

Bind performance conclusions to chip, memory, macOS, Xcode/SDK, workload, and concurrency. CI proves functional and basic regressions; it does not replace M6 or M5 Ultra hardware testing.

## 16. GitHub macOS runners are not the newest Macs

GitHub's free Apple Silicon runner pool can change chip and hardware specifications. On **2026-11-10**, this repository observed the following on `macos-latest`:

```text
macOS: 26.7.2
hardware_arch: arm64
process_arch: arm64
rosetta_translated: 0
chip: Apple M2 Pro (Virtual)
cpu_count: 5
memory_bytes: 15032385536 (14 GiB)
Xcode: 26.6 (17F113)
SDK: 26.5
```

Different jobs in the same workflow may land on different machines. In this run, `macos-latest` was arm64, but it was **not M6 and not macOS 27**. Separate Intel labels such as `macos-15-intel` and `macos-26-intel` also exist. Do not hard-code specifications such as "M1, 3 CPU, 7 GB" into audit conclusions.

Review rules:

- Use `runs-on: macos-latest` or an explicit arm64 label, then hard-gate `uname -m` and `arch` in the first step.
- Record the chip, CPU count, memory, macOS, Xcode/SDK, and Rosetta state from that run's log. Do not turn a CI pass into "all M-series Macs pass".
- GPU/Metal, Neural Engine, video encoding, very large unified memory, M6-only features, and macOS 27 behavior must be tested on real target hardware or listed as uncovered.

## 17. Common false-pass checklist

- The terminal is under Rosetta, but only `python3 --version` was checked, not `platform.machine()`.
- `brew`, `python3`, and `node` come from different Homebrew prefixes and architectures.
- A Linux script passes on the developer machine because GNU tools are installed locally, then fails on a clean Mac.
- Cross-platform paths were tested only on case-insensitive APFS, missing a case collision.
- The app was declared runnable only after removing quarantine with `xattr -d`.
- A Docker image starts, so its architecture is assumed to match the host.
- CI passes on one arm64 runner image/chip, then the result is presented as coverage for every M-series Mac or macOS 27.

## 18. Sources

These are the main primary sources. Command behavior remains governed by the current Mac's `man` pages and actual execution:

- Apple Newsroom, "Apple introduces M6 and M5 Ultra for a big leap in performance and AI compute": <https://www.apple.com/newsroom/2026/08/apple-introduces-m6-and-m5-ultra-for-a-big-leap-in-performance-and-ai-compute/>
- Apple Newsroom, "Apple introduces the new 14-inch MacBook Pro with M6" (macOS 27): <https://www.apple.com/newsroom/2026/10/apple-introduces-the-new-14-inch-macbook-pro-with-m6/>
- Apple Newsroom, M5 Pro/Max MacBook Pro: <https://www.apple.com.cn/newsroom/2026/03/apple-introduces-macbook-pro-with-all-new-m5-pro-and-m5-max/>
- Apple Developer Documentation, "About the Rosetta translation environment": <https://developer.apple.com/documentation/apple-silicon/about-the-rosetta-translation-environment>
- GitHub Docs, "GitHub-hosted runners" (macOS arm64 and Intel labels): <https://docs.github.com/en/actions/reference/runners/github-hosted-runners>
- GitHub Actions runner image, macOS 26 arm64: <https://github.com/actions/runner-images/blob/main/images/macos/macos-26-arm64-Readme.md>
- Homebrew Documentation, "Installation" (prefix and supported macOS versions): <https://docs.brew.sh/Installation>
- Docker Docs, "Networking on Docker Desktop": <https://docs.docker.com/desktop/features/networking/>
- Git documentation, `core.precomposeUnicode`: <https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreprecomposeUnicode>
- Apple Platform Security, Gatekeeper and runtime protection: <https://support.apple.com/guide/security/gatekeeper-and-runtime-protection-sec5599b66df/web>
- Apple Platform Security, System Integrity Protection: <https://support.apple.com/guide/security/system-integrity-protection-secb7ea06b49/web>
