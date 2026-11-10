# macOS 项目健康检查避坑记录

格式：`YYYY-MM-DD | 标签 | 触发场景 | 错误做法 | 正确做法 | 验证方式`

规则：

- 任务开始时先读与当前任务、macOS 版本、芯片架构和工具相关的条目。
- 先查重；重复的坑只补充原条目，不新增同义条目。
- 不删除旧条目；过时条目标 `[已过时]` 并说明原因。
- 只记录在真实 Mac 或 GitHub macOS runner 上核实过的经验。
- 反复出现两次以上的坑，提升为 `AGENTS.md` 规则、测试或 CI 检查。
- 不写密钥、令牌、个人绝对路径、客户数据或未脱敏日志。

## 条目

- 2026-11-10 | architecture, rosetta | 在 Apple Silicon 上执行正式检查 | 只看 `uname -m`，或在 Rosetta 终端里继续跑依赖与回归 | 同时要求 `uname -m`、`arch` 为 `arm64`，且 `sysctl -in sysctl.proc_translated` 为 `0`；不满足就停止 | GitHub macOS workflow 内置硬门禁；契约测试检查三个条件
- 2026-11-10 | packaging, scope | 从通用 skill 拆出 macOS 专用包 | 只删文档，却保留非 macOS 校验器和命令 | 删除非 macOS 脚本与避坑文件；包校验器按后缀、文件名和正文关键词 fail-closed | `tests/test_contract.py` 的包范围反例和 `scripts/verify_package.py`
- 2026-11-10 | privacy, redaction | 扫描 macOS 主目录路径 | 只匹配 Linux `/home/`，真实 `/Users/<name>` 进入公开报告 | 增加 `/Users/<name>` 模式，同时放行 `/Users/<you>`、`/Users/Shared` 和 `/Users/Guest` | 脱敏扫描器自检及 macOS 路径正反例测试
- 2026-11-10 | architecture, tooling | 混用 Homebrew、Python、Node、JDK 或容器 | 只看命令能启动，不检查二进制架构 | 用 `brew --prefix`、`file`、`lipo -info`、`python3 -c 'import platform; print(platform.machine())'` 和 Docker server arch 交叉确认 | GitHub macOS runner 实际执行环境探测
- 2026-11-10 | filesystem, git | 在大小写不敏感的 APFS 卷上审查路径 | 假设只改文件名大小写一定会被 Git 和构建系统识别 | 用实际目录枚举和 `git status --short` 验证；需要时在大小写敏感卷或 Linux 上复核 | 待 macOS CI 验证测试夹具
- 2026-11-10 | github-actions, architecture, runner | 用 GitHub 免费 macOS runner 验证原生架构 | 把 runner 规格写死为 M1 / 3 CPU / 7 GB，实测却是 Apple M2 Pro (Virtual) / 5 逻辑 CPU / 14 GiB | 只把 `arm64` 和 Rosetta `0` 当硬条件；芯片、CPU、内存和 macOS 版本每次从日志记录，报告不得外推到所有 M 系列 | run 42794677614 的 Python 3.9/3.12 两套 Job 均输出 arm64、Rosetta 0 并 PASS
