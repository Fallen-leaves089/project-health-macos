# macOS 常见与隐蔽坑（Apple Silicon M1 至 M6）

[中文](macos-pitfalls.md) | [English](macos-pitfalls.en.md)

本文件只收录会影响项目检查、构建、测试、容器、交付或安全判断的 macOS 问题。目标不是做芯片百科，而是帮助审计者在 Apple Silicon 上避免假绿、假红和错误归因。

> 截至 **2026-11-10**，Apple 官网公开的最新组合是 **M6**（Mac mini、MacBook Pro、iMac）与 **M5 Ultra**（Mac Studio）；最新 macOS 为 **macOS 27（Golden Gate）**。GitHub 免费 macOS runner 的 `macos-latest` 当前映射到 **macOS 26 arm64 / M1 / 3 CPU / 7 GB 内存**，不是 M6，也不是 Intel。来源见文末。

## 0. 正式检查前的硬门禁

本技能只接受原生 Apple Silicon：

```bash
test "$(uname -m)" = "arm64"
test "$(arch)" = "arm64"
test "$(sysctl -in sysctl.proc_translated)" = "0"
```

任一失败就停止正式检查。`x86_64` 表示 Rosetta 终端或 Intel Mac；前者会污染依赖架构，后者不在技能范围内。记录：

```bash
sw_vers
uname -m
sysctl -n machdep.cpu.brand_string
system_profiler SPHardwareDataType | grep -E 'Chip|Memory|Model Name'
```

不要只凭 macOS 版本推断芯片，也不要只凭 `uname -m` 推断没有 Rosetta。两者必须分开确认。

## 1. 芯片世代与审计含义

| 世代 | 时间与代表机型 | 审计时真正需要关注什么 |
|---|---|---|
| M1 / M1 Pro / Max / Ultra | 2020–2022 | 最早一批 arm64 生态；部分容器镜像、Python wheel、Node 原生模块、JDK 仍在 Rosetta 或只有 x86_64。GitHub 免费 runner 就是 M1。 |
| M2 / M2 Pro / Max / Ultra | 2022–2023 | 仍是同一 `arm64` ABI；不要因为芯片代数变化就新增构建目标。主要差异在 GPU、媒体引擎和机型散热。 |
| M3 / M3 Pro / Max | 2023–2024 | 引入 3 nm 世代；系统版本和 Xcode 下限更高。GPU/Metal 与 ML 框架的可用特性可能取决于 SDK 和系统，而不是只看芯片名。M3 Ultra 于 2025 年推出，仍属 `arm64`。 |
| M4 / M4 Pro / Max | 2024–2025 | 继续 `arm64`；统一内存和 GPU 能力提升会改变性能基线。并行测试不要沿用 M1 的固定线程数。 |
| M5 / M5 Pro / Max / Ultra | 2025–2026 | M5 Pro/Max 于 2026-03 发布，M5 Ultra 于 2026-08 发布；高核心数容易让测试过度并行，CPU/GPU/Neural Engine 负载需要单独限流和基线。 |
| M6 | 2026 | 2 nm、12 核 CPU/GPU、Dual 16 核 Neural Engine；随 macOS 27 发布。当前 GitHub runner 没有 M6，涉及新 GPU/Neural Engine、最新 SDK 或 macOS 27 行为时必须用真实目标机补测。 |

**关键结论：** M1 到 M6 都是 `arm64`，普通命令行、服务端和多数构建产物可以跨世代运行；不能把“芯片代数不同”误判成“二进制架构不同”。真正要分世代验证的是性能、GPU/Metal、Neural Engine、媒体编码、最新 SDK 和系统权限行为。

## 2. Rosetta 与架构混用（最容易造成假绿）

**现象：** 终端、IDE、CI step 或父进程在 Rosetta 下启动，`uname -m` 变成 `x86_64`；随后安装的 Python wheel、Node 原生模块、Homebrew 包和二进制都是 x86_64。命令能跑，但性能和兼容性结论都不可信。

**隐蔽点：** `arch`、`file`、`python3`、`node`、`java` 可能各自报告不同架构；父进程通过 Rosetta 启动后，子进程通常继续继承翻译环境。

**正确做法：**

```bash
sysctl -in sysctl.proc_translated
arch
file "$(command -v python3)"
python3 -c 'import platform; print(platform.machine())'
node -p 'process.arch'
java -XshowSettings:properties -version 2>&1 | grep 'os.arch'
lipo -info <binary-or-dylib>
```

统一在原生 arm64 终端重建依赖。不要用 `arch -x86_64` 继续跑正式回归，也不要把 Rosetta 下的通过结果写进交付结论。

## 3. Homebrew 双前缀与 PATH 遮蔽

**现象：** 原生 Homebrew 在 `/opt/homebrew`，Rosetta Homebrew 可能在 `/usr/local`；两者都装过时，`which brew`、`which python3`、`which node` 可能指向不同架构。

**正确做法：**

```bash
command -v brew
brew --prefix
brew config
brew doctor
```

脚本不要写死 `/opt/homebrew/bin`。使用 `brew --prefix` 解析路径，并检查 `PATH` 中是否存在另一套前缀。CI 中显式使用 setup action 或绝对路径，不要依赖登录 shell 的初始化文件。

## 4. BSD 用户态工具不是 GNU

**高频误判：** 从 Linux 复制来的 `sed -i`、`stat -c`、`date -d`、`readlink -f`、`find -printf`、`sha256sum`、`timeout` 在 macOS 上失败或行为不同。

```bash
sed -i '' 's/old/new/' file
stat -f '%Sp %Su:%Sg %N' file
date -r 0
shasum -a 256 file
python3 -c 'import os,sys; print(os.path.realpath(sys.argv[1]))' file
gtimeout 30 <command>   # 仅在安装 coreutils 后可用
```

**隐蔽点：** 某些脚本在交互式 shell 中因为用户装了 GNU 工具而通过，在 CI 或干净 Mac 上失败。审计时必须在干净环境验证；不要把 `gsed`、`gstat`、`gtimeout` 当系统自带。

## 5. 系统 bash 仍是 3.2

**现象：** 脚本在开发者机器上通过，因为开发者用 Homebrew bash 5；换到 `/bin/bash` 或 CI 后，关联数组、`mapfile`、`wait -n`、`${var,,}` 等语法失败。

**正确做法：**

```bash
/bin/bash --version
command -v bash
```

脚本优先 `#!/bin/sh`；明确需要 bash 功能时写 `#!/usr/bin/env bash` 并在 CI 固定版本。不要依赖用户 `.zshrc` 或交互式 alias。

## 6. APFS 大小写与 Unicode 规范化

**现象：** 默认 APFS 卷通常大小写不敏感，`README.md` 和 `readme.md` 可能指向同一文件；macOS 文件系统还会做 Unicode 规范化，和 Linux 的字节级文件名不完全一致。Git 的 `core.ignorecase` / `core.precomposeUnicode` 可能掩盖大小写或组合字符差异。

**正确做法：**

```bash
diskutil info / | grep -i 'File System Personality'
git config --show-origin --get core.ignorecase
git config --show-origin --get core.precomposeUnicode
find . -maxdepth 2 -print | LC_ALL=C sort
```

涉及大小写重命名、跨平台同步、资源路径或 `import` 大小写时，在区分大小写的 APFS 卷或 Linux 上复核。不要只看 `git status` 干净就判定路径兼容。

## 7. Gatekeeper、quarantine、codesign 与 notarization

**现象：** 下载的二进制、`.app`、`.dmg` 或脚本被加上 `com.apple.quarantine`；直接运行时被 Gatekeeper 拦截。团队常用 `xattr -d` 绕过，导致未验证的产物进入构建链。

**正确做法：**

```bash
xattr -p com.apple.quarantine <file>
codesign -dv --verbose=4 <app-or-binary>
codesign --verify --deep --strict --verbose=2 <app-or-binary>
spctl --assess --type execute --verbose=4 <app-or-binary>
xcrun stapler validate <app-or-dmg>
shasum -a 256 <file>
```

区分“未签名/未公证”和“恶意”是两件事；不要把 `spctl` 失败直接写成恶意软件。发布产物必须验证签名和 notarization；本地临时构建可以使用 ad-hoc 签名，但不能冒充可分发签名。不要建议关闭 Gatekeeper 或 SIP。

## 8. TCC、SIP 与自动化权限

**现象：** 访问 Desktop、Documents、Downloads、照片、通讯录、日历、屏幕录制或自动化其他 App 时，macOS TCC 会弹出权限请求；CI、SSH、无 GUI 会话或未登录用户可能直接失败。SIP 还会阻止修改系统目录和部分受保护文件。

**审计规则：**

- 先说明为什么需要权限，再请求最小权限；不要为了跑测试让用户授予 Full Disk Access。
- 不把“TCC 拒绝”误判成代码 bug；记录为环境限制和未覆盖项。
- 不通过关闭 SIP、降低 Gatekeeper、使用 `sudo` 修改系统目录来绕过。
- GUI 自动化、AppleScript、`screencapture`、辅助功能权限在 GitHub runner 上尤其不可靠，必须单列为未覆盖。

## 9. launchd 不是 systemd

**现象：** 把 Linux 的 `systemctl`、`service`、`journalctl` 直接搬到 macOS；或者用已弃用的 `launchctl load/unload` 管理用户服务，导致服务在不同登录会话中不可见。

**正确做法：**

```bash
launchctl print gui/$(id -u)/<label>
launchctl print system/<label>
launchctl bootstrap gui/$(id -u) <plist>
launchctl bootout gui/$(id -u)/<label>
```

明确服务属于 `gui/$UID` 还是 `system` 域；plist 路径、日志路径、环境变量和可执行文件权限都要核对。CI 中不要把需要登录 GUI 会话的服务当成可测试。

## 10. Docker Desktop、镜像架构与卷性能

**现象：** Apple Silicon 默认拉 arm64 镜像；只有 amd64 的镜像通过 QEMU 运行，速度慢且行为可能不同。容器里的 `localhost` 不是宿主机；大项目 bind mount 可能极慢。

```bash
docker context ls
docker version --format 'client={{.Client.Arch}} server={{.Server.Arch}}'
docker image inspect <image> --format '{{.Architecture}}/{{.Os}}'
docker run --rm <image> uname -m
```

规则：

- 记录 client、server 和镜像三者架构；不要只看其中一项。
- 只在镜像没有 arm64 版本时使用 `--platform linux/amd64`，并说明仿真影响。
- 从容器访问宿主机优先用 `host.docker.internal`，不要假设 `localhost`。
- `node_modules`、数据库文件和大量小文件不要盲目放在 macOS bind mount；用命名卷、项目内已忽略目录或 VM 原生存储做 A/B 基线。
- Colima 与 Docker Desktop 的 context、网络和卷行为不完全等价，切换后重新验证。

## 11. 端口、进程与权限

```bash
lsof -nP -iTCP:<port> -sTCP:LISTEN
ps -axo pid,ppid,comm,args
pgrep -fl <name>
kill -TERM <pid>
```

`ss`、`netstat -tulpn` 的 Linux 习惯在 macOS 上不可直接复用。`lsof` 看不到其他用户或受保护进程时，先判断权限和 TCC，不要直接加 `sudo` 或反复强杀。

## 12. 归档、扩展属性、资源叉与符号链接

**现象：** 用普通 `zip`/`tar` 打包再解压后，签名、quarantine、可执行位、符号链接或扩展属性丢失；macOS 生成的 `__MACOSX`、`._*` 文件污染产物。

**正确做法：**

```bash
ditto -c -k --keepParent <dir> <archive>.zip
ditto -x -k <archive>.zip <dest>
xattr -l <path>
find <dir> -type l -print
```

交付前在干净目录解压并重新验证签名、权限、链接和哈希。`COPYFILE_DISABLE=1` 可减少 AppleDouble 元数据，但不要用它替代产物验证。

## 13. 多语言工具链架构

### Python

```bash
python3 -c 'import platform; print(platform.machine())'
python3 -m pip debug --verbose | grep -i 'tags'
```

虚拟环境可能继承 Rosetta 架构；`pip install` 可能拿到 universal2、arm64 或 x86_64 wheel。记录解释器和扩展模块架构，不只记录 `python3 --version`。

### Node

```bash
node -p 'process.arch'
npm config get arch
printenv npm_config_arch 2>/dev/null || true
```

`node-gyp`、sharp、canvas、SQLite 等原生模块经常因架构不一致而失败。删掉 `node_modules` 后在原生 arm64 下重装，不要在不同架构间复制缓存。

### Java

```bash
/usr/libexec/java_home -V
java -XshowSettings:properties -version 2>&1 | grep -E 'os.arch|java.home'
```

JDK、JNI 库和容器基础镜像必须同架构。只替换 `JAVA_HOME` 而不重装 JNI 依赖，可能仍然加载错误的 `.dylib`。

### 动态库

```bash
file <binary-or-dylib>
lipo -info <binary-or-dylib>
otool -L <binary-or-dylib>
```

修改 dylib 后要重新签名；`DYLD_LIBRARY_PATH` 在受保护进程或 SIP 场景中可能被忽略。不要把“注入环境变量”当作跨版本兼容的长期方案。

## 14. Xcode、Command Line Tools 与 SDK

**现象：** `xcode-select -p` 指向 CLT，但项目需要完整 Xcode；或者装了多个 Xcode，`xcodebuild` 使用了错误版本；CLT license 未接受，构建在 CI 中无提示失败。

```bash
xcode-select -p
xcodebuild -version
xcrun --show-sdk-path
sudo xcodebuild -license check
```

记录 Xcode、SDK、CLT 和目标 `MACOSX_DEPLOYMENT_TARGET`。不要在未说明影响时执行 `sudo xcode-select -s` 或 `xcodebuild -runFirstLaunch`。Apple Silicon 上要显式检查目标架构和签名设置，不能只看“编译成功”。

## 15. 性能与资源基线不要跨世代照搬

M1 到 M6 的 CPU/GPU 核心数、统一内存带宽和 Neural Engine 规模差异很大。把 M1 上的固定线程数、连接池、并行测试 worker 数、Docker CPU 限制直接搬到 M5/M6，可能造成资源争抢、超时或假性能回归。

```bash
sysctl -n hw.ncpu
sysctl -n hw.memsize
vm_stat
sysctl -n machdep.cpu.brand_string
```

性能结论必须绑定芯片、内存、macOS、Xcode/SDK、负载和并发度。CI 只能证明功能和基本回归，不能替代 M6 或 M5 Ultra 的硬件性能测试。

## 16. GitHub macOS runner 不是“最新 Mac”

GitHub 免费 Apple Silicon runner 当前是 **M1、3 CPU、7 GB 内存**，系统为 **macOS 26.7.2**；`macos-latest` 是 arm64，但**不是 M6，也不是 macOS 27**。另外还存在 `macos-15-intel`、`macos-26-intel` 等 Intel 标签。

**审计规则：**

- workflow 必须固定 `runs-on: macos-latest` 或明确的 arm64 标签，并在第一步执行 `uname -m` / `arch` 硬门禁。
- 报告写明 runner 的芯片世代、macOS 版本、Xcode 版本和内存；不要把 CI 通过写成“所有 M 系列通过”。
- GPU/Metal、Neural Engine、视频编码、超大统一内存、M6 新特性和 macOS 27 专属行为，必须在对应真机补测或明确列为未覆盖。

## 17. 常见假绿清单

- 终端在 Rosetta，但只看了 `python3 --version`，没看 `platform.machine()`。
- `brew`、`python3`、`node` 分别来自不同 Homebrew 前缀，架构混用。
- Linux 脚本在开发者机器上通过，因为本地装了 GNU 工具，CI 干净 Mac 上失败。
- 用默认大小写不敏感 APFS 验证跨平台路径，未发现大小写冲突。
- 用 `xattr -d` 去掉 quarantine 后判定“应用可运行”。
- Docker 镜像能启动，就假设架构和宿主一致。
- CI 在 M1/macOS 26 上通过，就宣称 M6/macOS 27 通过。

## 18. 来源

以下为本文主要一手来源；命令行为仍以当前 Mac 的 `man` 页面和实际执行为准：

- Apple Newsroom, “Apple introduces M6 and M5 Ultra for a big leap in performance and AI compute”: <https://www.apple.com/newsroom/2026/08/apple-introduces-m6-and-m5-ultra-for-a-big-leap-in-performance-and-ai-compute/>
- Apple Newsroom, “Apple introduces the new 14-inch MacBook Pro with M6” (macOS 27): <https://www.apple.com/newsroom/2026/10/apple-introduces-the-new-14-inch-macbook-pro-with-m6/>
- Apple Newsroom, M5 Pro/Max MacBook Pro: <https://www.apple.com.cn/newsroom/2026/03/apple-introduces-macbook-pro-with-all-new-m5-pro-and-m5-max/>
- Apple Developer Documentation, “About the Rosetta translation environment”: <https://developer.apple.com/documentation/apple-silicon/about-the-rosetta-translation-environment>
- GitHub Docs, “GitHub-hosted runners” (macOS arm64 and Intel labels): <https://docs.github.com/en/actions/reference/runners/github-hosted-runners>
- GitHub Actions runner image, macOS 26 arm64: <https://github.com/actions/runner-images/blob/main/images/macos/macos-26-arm64-Readme.md>
- Homebrew Documentation, “Installation” (prefix and supported macOS versions): <https://docs.brew.sh/Installation>
- Docker Docs, “Networking on Docker Desktop”: <https://docs.docker.com/desktop/features/networking/>
- Git documentation, `core.precomposeUnicode`: <https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreprecomposeUnicode>
- Apple Platform Security, Gatekeeper and runtime protection: <https://support.apple.com/guide/security/gatekeeper-and-runtime-protection-sec5599b66df/web>
- Apple Platform Security, System Integrity Protection: <https://support.apple.com/guide/security/system-integrity-protection-secb7ea06b49/web>
