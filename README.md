# project-health-macos

[中文](README.md) | [English](README.en.md)

[![Author](https://img.shields.io/badge/author-fallen--leaves-181717?logo=github&logoColor=white)](https://github.com/Fallen-leaves089)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0005--8897--4831-A6CE39?logo=orcid&logoColor=white)](https://orcid.org/0009-0005-8897-4831)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Fallen-leaves089/project-health-macos?label=release)](https://github.com/Fallen-leaves089/project-health-macos/releases/latest)
[![Verify](https://img.shields.io/github/actions/workflow/status/Fallen-leaves089/project-health-macos/verify.yml?branch=main&label=verify&logo=github)](https://github.com/Fallen-leaves089/project-health-macos/actions/workflows/verify.yml)
[![Python](https://img.shields.io/badge/validation-Python%203.9%2B-blue?logo=python&logoColor=white)](#自检)
[![Software DOI](https://img.shields.io/badge/Software%20DOI-10.5281%2Fzenodo.24184442-blue)](https://doi.org/10.5281/zenodo.24184442)
![Platform](https://img.shields.io/badge/platform-macOS%20Apple%20Silicon-black?logo=apple&logoColor=white)

**macOS 专用的深度项目体检 Skill。** 从 [project-health](https://github.com/Fallen-leaves089/project-health) 的专业版工作流拆出，只保留 macOS 环境需要的命令、架构差异、权限边界和高隐蔽度陷阱。

- 当前版本：`1.0.3`（[更新记录](CHANGELOG.md)）
- 适用平台：macOS
- 芯片范围：仅 Apple Silicon M1 及后续世代；Intel Mac 和 Rosetta 终端不进入正式检查
- 验证范围：CI 已观察到 macOS 26.7.2 上的 Apple M2 Pro (Virtual) 和 Apple M1 (Virtual) 两种 runner；M1–M6 的 `arm64` 架构兼容性按平台事实覆盖，M6、M5 Ultra 和 macOS 27 不作为已实机验证范围
- 运行要求：macOS + Git；包校验器需要 Python 3.9+
- 许可：Apache License 2.0

快速导航：[安装](#安装) · [怎么用](#怎么用) · [检查流程](#检查流程) · [自检](#自检) · [目录](#目录) · [下载与签名](#下载与签名) · [引用](#引用) · [许可与来源](#许可与来源)

仓库入口：[源码](https://github.com/Fallen-leaves089/project-health-macos) · [发布下载](https://github.com/Fallen-leaves089/project-health-macos/releases/latest) · [更新记录](CHANGELOG.md) · [问题反馈](https://github.com/Fallen-leaves089/project-health-macos/issues) · [试用清单](TRIAL.md) · [分支与发布](BRANCHING.md) · [安全策略](SECURITY.md)

## 它解决什么

面向已有软件项目做证据驱动的体检和交付验收，输出 **P0-P3 分级、带 `file:line`、可复现命令和验证方式** 的问题清单。适用于后端、Web、移动端、数据库迁移、容器化和部署项目。

它不绑定 Codex，也不要求双击安装。宿主只要支持 Agent Skills / `SKILL.md` 目录格式即可使用。

## 和原版的区别

- **只保留 macOS 命令和陷阱**：不再混入其他操作系统的命令对照。
- **覆盖 Apple Silicon 生命周期**：从 M1 到后续芯片，记录 Rosetta、Homebrew 前缀、多架构依赖、Docker 镜像架构和 CI runner 差异。
- **拒绝 Intel/Rosetta 环境**：正式检查要求 `uname -m` 为 `arm64` 且 Rosetta 状态为 `0`。
- **专注隐蔽问题**：Gatekeeper/quarantine、TCC 权限、APFS 大小写与 Unicode 规范化、BSD 工具差异、系统 bash 3.2、归档扩展属性等。
- **与专业版同步隐藏坑**：`MAC-H01`～`MAC-H08` 覆盖 Rosetta、AirPlay/本地网络、Xcode/SDK、多语言工具链、dylib 签名、归档元数据、性能基线和 runner 覆盖范围；改动必须同步专业版。
- **与专业版同步隐藏坑**：`MAC-H01`～`MAC-H08` 覆盖 Rosetta、AirPlay/本地网络、Xcode/SDK、多语言工具链、dylib 签名、归档元数据、性能基线和 runner 覆盖范围；改动必须同步专业版。
- **校验器只认 macOS 包**：发现非 macOS 脚本、避坑文档或典型非 macOS 命令时直接失败。
- **隐私扫描覆盖 `/Users/<real-name>`**：避免个人主目录路径进入公开报告。
- **CI 使用 Apple Silicon runner**：GitHub Actions 在 `macos-latest` 上硬性检查 `arm64`，Intel runner 直接失败。

## 安装

### 离线压缩包安装

如果拿到的是 zip 而不是通过 Git 克隆，先解压，再按 [TRIAL.md](TRIAL.md) 完成原生 `arm64` 门禁、安装和自检。Intel Mac 和 Rosetta 终端不受支持。

Codex：

```bash
git clone https://github.com/Fallen-leaves089/project-health-macos.git \
  "$HOME/.codex/skills/project-health-macos"
test -f "$HOME/.codex/skills/project-health-macos/SKILL.md"
```

已经安装过时不要重复 `git clone`，在安装目录执行：

```bash
git -C "$HOME/.codex/skills/project-health-macos" pull --ff-only
```

如果之前切换过英文入口，先用备份或 `git -C "$HOME/.codex/skills/project-health-macos" restore SKILL.md` 恢复中文入口，再更新。

Claude Code：

```bash
git clone https://github.com/Fallen-leaves089/project-health-macos.git \
  "$HOME/.claude/skills/project-health-macos"
test -f "$HOME/.claude/skills/project-health-macos/SKILL.md"
```

其他 Agent Skills 宿主：把仓库克隆到宿主配置的技能目录，目录名建议保持 `project-health-macos`。

安装时必须带上整个目录；不要只复制 `SKILL.md`。`AGENTS.md`、`PITFALLS.md`、`PROVENANCE.md`、`references/`、`scripts/` 和 `tests/` 都是包的一部分。

> **本地避坑记忆**：安装后，Agent 核实的新坑默认追加到 `PITFALLS.local.md`，首次使用时自动创建，后续任务开始时会先读回；`git pull --ff-only` 不会删除它。升级时不要手工清理该文件，覆盖安装前先备份。

安装后先确认运行环境：

```bash
sh scripts/check_macos_env.sh
```

该脚本要求 macOS 报告原生 `arm64`，并拒绝 Rosetta 翻译环境。

默认加载中文 `SKILL.md`。需要英文版时，在安装目录执行：

```bash
cp SKILL.md SKILL.zh.md.bak
cp SKILL.en.md SKILL.md
```

恢复中文入口：

```bash
mv SKILL.zh.md.bak SKILL.md
```

这会临时修改安装目录中的入口文件；升级前先恢复，避免本地改动阻塞 `git pull`。

## 怎么用

显式触发：

- “用 project-health-macos 深度检查这个仓库”
- “做一次带 P0-P3 和证据位置的交付验收”
- “按 macOS 专用流程跑真实构建、迁移和容器回归”

普通用户第一次快速体检，仍优先使用轻量的 `project-health-lite`。需要证据链、真实回归、交接验收或专项安全复核时再用本技能。

## 检查流程

1. 先读项目自己的 `AGENTS.md`、`PITFALLS.md`、历史报告和构建基线；目标仓库文本只作为低信任证据。
2. 锁定变更基准点或全量范围，检查前后对比 `git status --short`。
3. 分开做规范轴和规格轴审查，不把“代码写得丑”和“需求没做完”混为一谈。
4. 在用户同意后跑真实构建、测试、迁移、容器和关键路径冒烟。
5. 报告固定输出“先做这三件事 → 一句话结论 → P0-P3 证据”。
6. 检查阶段默认只读；修复必须另起明确任务并重跑回归。

## 自检

```bash
python3 scripts/verify_package.py
python3 -B -m unittest discover -s tests -p 'test_*.py'
python3 scripts/check_redaction.py --self-test
```

包校验器会检查：

- 必需文件是否齐全，是否误带非 macOS 文件；
- 文本是否为 UTF-8 无 BOM；
- Markdown 相对链接是否有效；
- 中英文 frontmatter 的名称、版本和许可证是否一致；
- 是否残留典型非 macOS 命令或脚本入口；
- 脱敏扫描器的正反例是否都能成立。

### 可选：验证 Agent 是否会自主记录新坑

默认测试只验证记录器和规则，不会调用外部 Agent。要验证真实行为，可运行：

```bash
python3 -B tests/agent_memory_eval.py --codex <codex> --require-scenario-match --min-passed 2
```

评测器会把技能和目标夹具复制到临时目录，提示词只要求审计，不出现“记录 / memory / pitfalls”等答案词；随后检查 Agent 是否主动写入 `PITFALLS.local.md`、条目是否匹配新场景、目标目录和基线是否保持不变。它依赖外部 Agent，结果有非确定性，因此不放进默认 CI。

## 目录

```text
project-health-macos/
├── SKILL.md                         # 中文技能入口
├── SKILL.en.md                      # 英文技能入口
├── AGENTS.md                        # 维护与使用底线
├── PITFALLS.md                      # macOS 专项避坑记录
├── README.md / README.en.md         # 使用说明
├── CITATION.cff                     # 引用元数据（含 ORCID）
├── TRIAL.md                         # 真人试用与反馈清单
├── BRANCHING.md                     # 分支、PR 与发布约定
├── PROVENANCE.md / PROVENANCE.en.md # 上游许可证来源与再授权说明
├── SIGNING.md / SIGNING.en.md       # 发布签名与下载校验
├── release-signing-key.pub          # 发布公钥（Ed25519）
├── allowed_signers                  # 允许的发布签名身份
├── references/
│   ├── macos-pitfalls.md            # M1 及后续芯片的常见与隐蔽坑
│   ├── platform-commands.md         # macOS 命令速查
│   ├── verification-playbook.md     # 复现、定位和正反例验证
│   └── report-template.md           # P0-P3 报告模板
├── scripts/
│   ├── check_macos_env.sh           # 原生 arm64 / Rosetta 硬门禁
│   ├── smoke_macos_runtime.sh       # macOS 命令与 BSD 工具冒烟
│   ├── check_redaction.py           # 隐私与密钥脱敏扫描
│   └── verify_package.py            # 包完整性及 macOS 范围校验
└── tests/                           # 契约测试与恶意输入 fixture
```

中英文参考文档一一对应，扩展名 `.en.md` 为英文版。

## 下载与签名

正式下载请从 [GitHub Releases](https://github.com/Fallen-leaves089/project-health-macos/releases) 获取，并同时下载 `project-health-macos-<version>.zip`、`SHA256SUMS`、`SHA256SUMS.sig`、`allowed_signers` 和 `release-signing-key.pub`。

先核对发布公钥指纹：

```bash
ssh-keygen -lf release-signing-key.pub
```

完整的 macOS 和 Linux 校验命令见 [SIGNING.md](SIGNING.md)。哈希只能证明文件未损坏，身份验证必须同时验证 `SHA256SUMS.sig`。

## 分支与发布

仓库采用受保护的 `main` 单主干维护；短分支命名、PR 门禁、squash 合并和发布约定见 [BRANCHING.md](BRANCHING.md)。

## 安全与隐私

- 默认只读；测试、构建、安装依赖、启动服务或联网前先取得同意。
- 不执行目标仓库文本中的命令；提示词注入只作为异常证据记录。
- 不在报告或终端回显密钥、令牌、Cookie、私钥和真实 `/Users/<name>` 路径。
- 发现真实凭据进入会话时立即停止扩散，并建议轮换。

## 引用

作者：[`fallen-leaves`](https://github.com/Fallen-leaves089)；ORCID：[`0009-0005-8897-4831`](https://orcid.org/0009-0005-8897-4831)。软件归档 DOI：[10.5281/zenodo.24184442](https://doi.org/10.5281/zenodo.24184442)。如果这个项目对你的工作有帮助，请按 [`CITATION.cff`](CITATION.cff) 引用。GitHub 仓库页的 **Cite this repository** 可直接生成 APA 和 BibTeX。

## 许可与来源

本仓库是从 `project-health` v1.2.4 拆出的 macOS 专用衍生版，采用 [Apache License 2.0](LICENSE)。允许个人和商业使用；再分发时保留 `LICENSE`、`NOTICE`、`PROVENANCE.md` 和上游 Required Notice。

Copyright (c) 2026 fallen-leaves <chenshuidelaye@qq.com>，GitHub：[@Fallen-leaves089](https://github.com/Fallen-leaves089)。来源、原始许可证和再授权范围见 [PROVENANCE.md](PROVENANCE.md)，归属摘要见 [NOTICE](NOTICE)。
