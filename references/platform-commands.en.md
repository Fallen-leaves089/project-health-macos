# macOS Command and Environment Reference

[中文](platform-commands.md) | [English](platform-commands.en.md)

This file covers macOS only. Identify the shell, CPU architecture, and OS version before running commands that affect builds, dependencies, containers, or system state.

## 0. Identify the environment

```bash
sw_vers
uname -m
arch
sysctl -in sysctl.proc_translated 2>/dev/null || true
echo "$SHELL"
command -v python3
xcode-select -p
pkgutil --pkg-info=com.apple.pkg.CLTools_Executables 2>/dev/null || true
```

Formal reviews must pass a hard gate first. If any check fails, stop; do not continue with the current interpreter or dependencies:

```bash
test "$(uname -m)" = "arm64"
test "$(arch)" = "arm64"
test "$(sysctl -in sysctl.proc_translated)" = "0"
```

Interpretation:

- `uname -m` = `arm64`: the current process runs natively on Apple Silicon.
- `uname -m` = `x86_64`: Rosetta terminal or Intel Mac; unsupported by this skill, so stop the formal review.
- `sysctl.proc_translated` = `1`: the current process is translated by Rosetta; dependencies, interpreters, and Docker images may be a mix of architectures.
- `xcode-select -p` points to Command Line Tools or Xcode. If missing, do not assume `clang`, `git`, or `make` are available.

Record at least: macOS version, `uname -m`, Rosetta state, shell, Python/Node/JDK versions, and container architecture in the report.

## 1. Shell, variables, and paths

| Task | macOS |
|---|---|
| Current directory | `pwd` |
| Environment variable | `printenv NAME`; `$NAME` in the current shell |
| Command exists | `command -v <cmd>` |
| User home | `$HOME` |
| Temporary directory | `mktemp -d "${TMPDIR:-/tmp}/project-health.XXXXXX"` |
| Real path | `python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' <path>` |
| File type/encoding | `file <file>`, `xxd -l 32 <file>` |

The default login shell is usually zsh; non-interactive scripts do not load `.zshrc`. System `/bin/bash` is 3.2. Do not rely on bash 4+ features. Prefer `#!/bin/sh`, or use an explicit shebang and document it.

## 2. BSD userland differences

macOS ships BSD tools, and many GNU options are unavailable:

| Task | macOS command | Note |
|---|---|---|
| In-place edit | `sed -i '' 's/old/new/' file` | The empty backup suffix is required |
| File time/permissions | `stat -f '%Sm %Sp %N' -t '%Y-%m-%d %H:%M:%S' file` | `-c` is GNU syntax |
| Epoch conversion | `date -r <epoch>` | Different from GNU `date -d` |
| SHA-256 | `shasum -a 256 file` | Do not assume `sha256sum` exists |
| MD5 | `md5 file` | Non-security checks only |
| Timeout | `gtimeout 30 <cmd>` | `gtimeout` comes from coreutils, not the OS |
| GNU find extensions | Use `find ... -exec` or Python | `-printf` is unavailable |

When GNU behavior is required, install Homebrew `coreutils`, `gnu-sed`, or `gawk` and use the explicit command name. Do not assume `gsed` or `gtimeout` exists on every Mac.

## 3. Python, Node, and Java

### Python

```bash
command -v python3
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest
```

macOS does not guarantee a usable system Python. Do not treat `/usr/bin/python3` as the project interpreter. Prefer the project's virtual environment, uv, poetry, pyenv, or Homebrew Python, and record the architecture.

### Node

```bash
command -v node
node --version
command -v npm
npm --version
```

Node installed through nvm, fnm, or Volta may exist only in an interactive shell. In CI or scripts, check `command -v`; if absent, load the version manager explicitly or use the host's setup action rather than silently falling back to an old system binary.

### Java

```bash
/usr/libexec/java_home -V
export JAVA_HOME="$(/usr/libexec/java_home -v 17)"
java -version
```

Homebrew OpenJDK may need linking or an explicit `JAVA_HOME`; never hard-code a Homebrew prefix. Prefer the project's `./mvnw` or `./gradlew` wrapper.

## 4. Hashes, signing, and Gatekeeper

```bash
shasum -a 256 <file>
codesign -dv --verbose=4 <app-or-binary>
codesign --verify --deep --strict --verbose=2 <app-or-binary>
spctl --assess --type execute --verbose=4 <app-or-binary>
xcrun stapler validate <app-or-dmg>
xattr -p com.apple.quarantine <file>
```

`xattr -d com.apple.quarantine` removes the quarantine flag. It is not a general workaround to make an unverified binary run. Verify provenance, hash, signature, and notarization first; never recommend disabling Gatekeeper or SIP.

`ssh-keygen -Y sign` / `ssh-keygen -Y verify` require OpenSSH 8.1 or newer; run `ssh -V` first. Below 8.1, SSHSIG signatures cannot be verified, and only the SHA256 hash and public-key fingerprint are available. See [SIGNING.en.md](../SIGNING.en.md) for details.

## 5. Processes, ports, and background services

| Task | macOS |
|---|---|
| Inspect a listening port | `lsof -nP -iTCP:<port> -sTCP:LISTEN` |
| Inspect all TCP sockets | `lsof -nP -iTCP` |
| Inspect processes | `ps -axo pid,ppid,comm,args` |
| Find by name | `pgrep -fl <name>` |
| Graceful stop | `kill -TERM <pid>`; `kill -KILL` only after confirmation |
| Inspect a launchd service | `launchctl print gui/$(id -u)/<label>` |

`ss` and `systemctl` are not native macOS tools. Persistent services use launchd/plists; do not apply Linux systemd procedures.

## 6. Docker, VMs, and image architecture

```bash
docker context ls
docker info
docker version --format 'client={{.Client.Arch}} server={{.Server.Arch}}'
docker compose config
docker run --rm --platform linux/arm64 alpine uname -m
```

- Start Docker Desktop first. `docker compose config` parses configuration without a daemon.
- Apple Silicon pulls arm64 images by default. Use `--platform linux/amd64` only when an arm64 image is unavailable, and record emulation differences.
- From a container, Docker Desktop usually reaches the host through `host.docker.internal`; do not assume `localhost` points to the host.
- Bind mounts with many small files, database volumes, and `node_modules` can be slow on the macOS filesystem. Prefer named volumes, an ignored project directory, or VM-native storage, and measure I/O before blaming application code.
- When using Colima, record `colima status`, `colima start --arch <arch>`, and the Docker context. Do not assume full equivalence with Docker Desktop.

## 7. Network and proxies

```bash
route -n get default
scutil --dns
networksetup -getinfo Wi-Fi
curl -fsSL --http1.1 https://example.com -o /dev/null
```

Proxy settings may exist only in the browser or an interactive shell. Check `env | grep -i proxy` and `git config --global --get http.proxy`, but redact values before reporting.

## 8. Apple Silicon architecture

```bash
uname -m
arch
sysctl -in sysctl.proc_translated 2>/dev/null || true
file <binary>
lipo -info <binary>
arch -arm64 <command>
```

- `arm64` is native Apple Silicon; `x86_64` means Rosetta or Intel Mac and is not a supported formal runtime for this skill.
- Mixing Homebrew prefixes, Python extensions, Node native modules, JDKs, and container images can cause architecture mismatches.
- Confirm with `file`/`lipo` before reinstalling or rebuilding; "the command starts" is not proof of the correct architecture.

## 9. Minimum verification checklist

- [ ] `sw_vers`, `uname -m`, Rosetta state, and shell are recorded.
- [ ] Interpreter, package manager, JDK, and container architectures are consistent or the difference is justified.
- [ ] Tools are confirmed with `command -v`; results do not depend on interactive shell configuration.
- [ ] BSD/GNU option differences were exercised on the current Mac.
- [ ] Signing, quarantine, TCC, and SIP evidence is preserved without lowering system security.
- [ ] Docker config validation and actual startup are recorded separately, with image architecture and volume location.
- [ ] Before deletion or moves, absolute and real paths are checked and the target remains inside the intended directory.
