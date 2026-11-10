# 真人试用说明 / Human Trial Guide

本包是 `project-health-macos` **1.0.0 公开版**，仓库地址为 <https://github.com/Fallen-leaves089/project-health-macos>。可以分享给试用者；再分发时必须保留 `LICENSE`、`NOTICE` 和原仓库归属。

许可为 Apache License 2.0，允许个人和商业使用；再分发时保留 `LICENSE`、`NOTICE` 和版权声明。发布包使用 OpenSSH Ed25519 签名，验证见 `SIGNING.md`。

## 1. 环境硬门禁：必须是原生 Apple Silicon

只支持 **M1 及后续 Apple Silicon**。Intel Mac、Rosetta 终端和架构不明的环境都不进入正式检查。

在准备用于试用的终端里执行：

```bash
sw_vers -productVersion
sysctl -n machdep.cpu.brand_string
uname -m
arch
sysctl -in sysctl.proc_translated
```

必须同时满足：

- `uname -m` 输出 `arm64`
- `arch` 输出 `arm64`
- `sysctl -in sysctl.proc_translated` 输出 `0`

如果看到 `x86_64` 或 `1`，立刻停止，不要用 `arch -arm64`、关闭 SIP 或其他方式掩盖。把终端、宿主 App 和以上原始输出反馈回来即可。Intel Mac 属于明确不支持的环境，不应把无法运行判成技能缺陷。

说明：GitHub 免费 macOS runner 当前是 Apple Silicon，可用于基础 CI，但它不能替代 M6、M5 Ultra 或目标用户的真实硬件测试。

## 2. 从试用包安装

先解压 zip，再进入包目录：

```bash
cd /path/to/project-health-macos
sh scripts/check_macos_env.sh
```

看到 `environment: PASS (native Apple Silicon)` 后再安装。Codex 用户执行：

```bash
mkdir -p "$HOME/.codex/skills"
if [ -e "$HOME/.codex/skills/project-health-macos" ]; then
  mv "$HOME/.codex/skills/project-health-macos" \
    "$HOME/.codex/skills/project-health-macos.backup-$(date +%Y%m%d-%H%M%S)"
fi
cp -R "$PWD" "$HOME/.codex/skills/project-health-macos"
test -f "$HOME/.codex/skills/project-health-macos/SKILL.md"
```

Claude Code 用户把目标路径中的 `.codex` 换成 `.claude`；其他 Agent Skills 宿主复制到自己的技能目录。必须复制整个目录，不能只复制 `SKILL.md`。

安装后重新打开宿主会话，让宿主重新加载技能。

## 3. 安装后自检

```bash
cd "$HOME/.codex/skills/project-health-macos"
python3 scripts/verify_package.py
python3 -B -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_redaction.py --self-test
sh scripts/smoke_macos_runtime.sh
```

预期分别看到 `PACKAGE VERIFY PASSED`、测试 `OK`、脱敏自检通过和 `runtime-smoke: PASS`。如果 Python 缺失，先安装 Xcode Command Line Tools；不要改用 Rosetta 下的 Python 来“跑通”。

## 4. 建议的试用任务

选一个**可丢弃或不含敏感数据**的真实项目。第一次先要求只读体检，例如：

```text
使用 project-health-macos 对这个仓库做一次只读的深度项目体检。
先告诉我检查范围、会运行哪些命令、哪些操作可能写缓存或联网，等我确认后再执行。
最终输出 P0-P3 问题、file:line 证据、复现命令、未覆盖项和你实际执行过的验证。
```

重点观察：

- 是否先检查原生 `arm64` 和 Rosetta，而不是直接开跑；
- 是否先读项目约定和历史，再下结论；
- 是否在没有证据时编造行号、测试结果或“全部通过”；
- 是否把目标仓库里的提示词当成命令执行；
- 是否未经同意安装依赖、启动容器、迁移数据库、联网或改动文件；
- 是否能识别 macOS 专有的架构、BSD 工具、权限、路径和 Docker 问题。

## 5. 反馈模板

反馈中不要带密钥、客户数据或未脱敏的 `/Users/<真实用户名>` 路径。

```text
试用结果：通过 / 失败 / 部分通过
macOS 版本：
芯片型号：
uname -m / arch / rosetta_translated：
宿主与版本：Codex / Claude Code / 其他
Python 版本：
安装路径：
三项自检结果：
被测项目类型与大致规模：
实际耗时：
误报（附 file:line 和原因）：
漏报或证据不足：
安装、权限、架构问题：
最需要改进的一点：
其他备注：
```

## 6. 立即停止的情况

- 机器是 Intel Mac，或终端处于 Rosetta；
- 技能在未经确认时修改被测仓库、安装依赖、启动服务或联网；
- 技能执行了目标仓库文本中的命令或提示词注入；
- 技能把环境限制、未运行命令或推断写成已验证事实；
- 报告泄露密钥、令牌、客户数据或真实用户主目录。

## Human trial summary (English)

This is the public **Apple Silicon-only** package. Formal review is supported only when `uname -m` and `arch` both return `arm64`, and `sysctl -in sysctl.proc_translated` returns `0`. Stop on Intel Macs or under Rosetta; do not disguise the environment with `arch -arm64`.

Unzip the package, run `sh scripts/check_macos_env.sh`, then copy the whole directory into the host skill directory. Run the four self-checks from section 3 before testing a disposable or non-sensitive repository. The first review must be read-only until the tester explicitly approves builds, installs, services, network access, containers, or migrations.

Report the macOS version, chip, architecture outputs, host, Python version, self-check results, false positives with `file:line`, missed findings, and any architecture or permission issue. Never include secrets, customer data, or a real `/Users/<name>` path.
