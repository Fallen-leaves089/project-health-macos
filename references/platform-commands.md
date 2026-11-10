# macOS 命令与环境速查

[中文](platform-commands.md) | [English](platform-commands.en.md)

本文件只覆盖 macOS。先确认 shell、芯片架构和系统版本，再执行会影响构建、依赖、容器或系统状态的命令。

## 0. 先确认环境

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

正式检查前必须通过硬性门禁；任一失败就停止，不要继续用当前解释器或依赖跑回归：

```bash
test "$(uname -m)" = "arm64"
test "$(arch)" = "arm64"
test "$(sysctl -in sysctl.proc_translated)" = "0"
```

判读：

- `uname -m` 为 `arm64`：当前进程运行在 Apple Silicon 原生架构。
- `uname -m` 为 `x86_64`：Rosetta 终端或 Intel Mac；本技能不支持，必须停止正式检查。
- `sysctl.proc_translated` 输出 `1`：当前进程经 Rosetta 翻译；依赖、解释器和 Docker 镜像可能混入 x86_64。
- `xcode-select -p` 指向 CommandLineTools 或 Xcode 路径；缺少时不要直接假设 `clang`、`git`、`make` 可用。

报告里至少记录：macOS 版本、`uname -m`、Rosetta 状态、shell、Python/Node/JDK 版本、容器架构。

## 1. Shell、变量与路径

| 操作 | macOS |
|---|---|
| 当前目录 | `pwd` |
| 环境变量 | `printenv NAME`；当前 shell 中可用 `$NAME` |
| 判断命令 | `command -v <cmd>` |
| 用户目录 | `$HOME` |
| 临时目录 | `mktemp -d "${TMPDIR:-/tmp}/project-health.XXXXXX"` |
| 真实路径 | `python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' <path>` |
| 文件头/编码 | `file <file>`、`xxd -l 32 <file>` |

默认登录 shell 通常是 zsh；非交互脚本不会自动加载 `.zshrc`。系统 `/bin/bash` 是 3.2，不要依赖 bash 4+ 语法。脚本优先使用 `#!/bin/sh`，需要特定功能时写明确 shebang 并在报告中注明。

## 2. BSD 用户态工具差异

macOS 自带的是 BSD 版本，很多 GNU 参数不可用：

| 任务 | macOS 写法 | 注意 |
|---|---|---|
| 原地编辑 | `sed -i '' 's/old/new/' file` | 不能省略 `''` |
| 文件时间/权限 | `stat -f '%Sm %Sp %N' -t '%Y-%m-%d %H:%M:%S' file` | `-c` 是 GNU 写法 |
| 日期换算 | `date -r <epoch>` | 与 GNU `date -d` 不同 |
| SHA-256 | `shasum -a 256 file` | 不要假设有 `sha256sum` |
| MD5 | `md5 file` | 只用于非安全校验 |
| 超时 | `gtimeout 30 <cmd>` | `gtimeout` 来自 coreutils，不是系统自带 |
| GNU find 扩展 | 用 `find ... -exec` 或 Python | `-printf` 不可用 |

需要 GNU 工具时安装 Homebrew `coreutils` / `gnu-sed` / `gawk`，并在脚本中使用明确命令名；不要把 `gsed`/`gtimeout` 当成所有 Mac 默认都有。

## 3. Python、Node 与 Java

### Python

```bash
command -v python3
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest
```

macOS 不保证系统自带可用的 Python，也不要把 `/usr/bin/python3` 当成项目解释器。优先用项目声明的虚拟环境、uv、poetry、pyenv 或 Homebrew Python，并记录架构。

### Node

```bash
command -v node
node --version
command -v npm
npm --version
```

通过 nvm、fnm 或 Volta 安装的 Node 可能只存在于交互式 shell。CI/脚本中先 `command -v`，找不到时显式加载版本管理器或使用宿主的 setup action，不要静默回落到系统旧版本。

### Java

```bash
/usr/libexec/java_home -V
export JAVA_HOME="$(/usr/libexec/java_home -v 17)"
java -version
```

Homebrew 的 OpenJDK 可能需要手动链接或设置 `JAVA_HOME`；不要把某个 Homebrew 前缀写死。项目自带 `./mvnw`、`./gradlew` 时优先用 wrapper。

## 4. 文件哈希、签名与 Gatekeeper

```bash
shasum -a 256 <file>
codesign -dv --verbose=4 <app-or-binary>
codesign --verify --deep --strict --verbose=2 <app-or-binary>
spctl --assess --type execute --verbose=4 <app-or-binary>
xcrun stapler validate <app-or-dmg>
xattr -p com.apple.quarantine <file>
```

`xattr -d com.apple.quarantine` 会移除隔离标记，不应作为让未验证二进制“能跑”的通用绕法。先核实来源、哈希、签名和 notarization；不得建议关闭 Gatekeeper 或 SIP。

## 5. 进程、端口与后台服务

| 操作 | macOS |
|---|---|
| 查监听端口 | `lsof -nP -iTCP:<port> -sTCP:LISTEN` |
| 查全部 TCP | `lsof -nP -iTCP` |
| 查进程 | `ps -axo pid,ppid,comm,args` |
| 按名字查进程 | `pgrep -fl <name>` |
| 优雅停止 | `kill -TERM <pid>`；确认后必要时 `kill -KILL` |
| 查看 launchd 服务 | `launchctl print gui/$(id -u)/<label>` |

`ss`、`systemctl` 不是 macOS 原生工具。后台常驻服务用 launchd/plist；不要套用 Linux 的 systemd 操作。

## 6. Docker、虚拟机与镜像架构

```bash
docker context ls
docker info
docker version --format 'client={{.Client.Arch}} server={{.Server.Arch}}'
docker compose config
docker run --rm --platform linux/arm64 alpine uname -m
```

- Docker Desktop 需要先启动；`docker compose config` 只解析配置，不需要 daemon。
- Apple Silicon 默认拉取 arm64 镜像。只有镜像没有 arm64 版本时才用 `--platform linux/amd64`，并记录仿真带来的性能和行为差异。
- 容器内连接宿主机时，Docker Desktop 常用 `host.docker.internal`；不要默认 `localhost` 指向宿主机。
- 大量小文件 bind mount、数据库卷和 `node_modules` 放在 macOS 文件系统上可能很慢；优先使用命名卷、项目内已忽略目录或 Linux VM 原生存储，并用实际 I/O 基线验证。
- 使用 Colima 时记录 `colima status`、`colima start --arch <arch>` 和 Docker context；不要假设与 Docker Desktop 完全等价。

## 7. 网络与代理

```bash
route -n get default
scutil --dns
networksetup -getinfo Wi-Fi
curl -fsSL --http1.1 https://example.com -o /dev/null
```

代理可能只配置在浏览器或交互式 shell 中。CI/脚本先检查 `env | grep -i proxy` 和 `git config --global --get http.proxy`，但输出前要脱敏。

## 8. Apple Silicon 架构

```bash
uname -m
arch
sysctl -in sysctl.proc_translated 2>/dev/null || true
file <binary>
lipo -info <binary>
arch -arm64 <command>
```

- `arm64` 是 Apple Silicon 原生；`x86_64` 表示 Rosetta 或 Intel Mac，不能作为本技能的正式运行环境。
- 混用 Homebrew 前缀、Python 扩展、Node 原生模块、JDK 和容器镜像会产生架构不匹配。
- 先确认 `file`/`lipo` 输出，再决定重装或重建；不要只用“命令能启动”判断架构正确。

## 9. 最小验证清单

- [ ] 记录 `sw_vers`、`uname -m`、Rosetta 状态和 shell。
- [ ] 解释器、包管理器、JDK 和容器镜像架构一致或有明确理由。
- [ ] 用 `command -v` 确认工具真实存在，不依赖交互式 shell 配置。
- [ ] 涉及 BSD/GNU 参数差异时，命令已在当前 Mac 实际跑过。
- [ ] 涉及签名、quarantine、TCC、SIP 时保留原始证据，不通过降低系统安全性绕过。
- [ ] Docker 配置校验与真实启动分开记录，镜像架构和卷位置明确。
- [ ] 删除或移动前核对绝对路径和真实路径，并确认目标在预期目录内。
