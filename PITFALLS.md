# macOS 项目健康检查避坑记录

格式：`YYYY-MM-DD | 标签 | 触发场景 | 错误做法 | 正确做法 | 验证方式`

规则：

- 任务开始时先读与当前任务、macOS 版本、芯片架构和工具相关的条目。
- 先查重；重复的坑只补充原条目，不新增同义条目。
- 不删除旧条目；过时条目标 `[已过时]` 并说明原因。
- 只记录在真实 Mac 或 GitHub macOS runner 上核实过的经验。
- 反复出现两次以上的坑，提升为 `AGENTS.md` 规则、测试或 CI 检查。
- 不写密钥、令牌、个人绝对路径、客户数据或未脱敏日志。

## 常驻隐藏坑绊线

| 绊线 | 隐蔽风险指纹 | 必做动作 |
|---|---|---|
| M-RES-01 | 没有测试用例、只跑部分模块、CI 作业被跳过仍显示全绿 | 检查测试数、原始退出码、required checks 和跳过状态 |
| M-RES-02 | 管道、包装器或格式化工具吞掉真实退出码 | 在过滤前保存 `$?` 或启用 `pipefail` |
| M-RES-03 | 密钥或个人信息进入构建产物、日志、镜像层、备份或 Git 历史 | 扫描位置和键名，不展示值；疑似泄露按需要轮换 |
| M-RES-04 | 租户、资源或账号归属只依赖客户端参数 | 从可信会话取归属，并用跨租户/越权反例确认 |
| M-RES-05 | 备份存在但从未恢复，或迁移没有回滚/补偿 | 在隔离环境实际恢复并演练回滚 |
| M-RES-06 | Rosetta 终端或 x86_64 依赖被当成原生 arm64 结果 | 同时检查 `uname -m`、`arch`、`sysctl.proc_translated`，在原生终端重建依赖 |
| M-RES-07 | 只有 CLT、SDK/license 不匹配，或选了错误 Xcode | 记录 `xcode-select -p`、`xcodebuild -version`、`xcrun --show-sdk-path` 和构建目标 |
| M-RES-08 | Gatekeeper/quarantine、签名或公证失败被当成“恶意”或直接绕过 | 用 `xattr`、`codesign`、`spctl`、`xcrun stapler` 分别取证，不关闭 Gatekeeper/SIP |
| M-RES-09 | 用户显式要求把具体风险升级为常驻 | 必须同时有显式常驻措辞、具体对象、适用范围；缺一先问。记录用户原话摘录、升级时间、范围、完整条目和撤销/降级条件 |

### 常驻记录规则

- 基线 `M-RES-01～08` 与用户升级常驻分开记账；总数超过 12 条时报告容量预警，不硬拒绝。
- 升级只改变常驻入口，不改变是否命中；具体项目仍要标 `已查 / 不适用 / 未覆盖`。
- 用户撤销、范围变更或对应条目失效时复核；连续多次不适用只作为复核建议，不静默自动降级。

## 按需索引

| 族 | 何时打开 | 关联条目 |
|---|---|---|
| ARCH 架构/Rosetta | 架构、原生模块、dylib、Docker 镜像或性能基线可疑 | MAC-H01、M-RES-06 |
| XCODE 工具链 | CLT/Xcode、SDK、license、模拟器或部署目标异常 | MAC-H03、M-RES-07 |
| FS 文件系统/归档 | APFS、大小写、Unicode、扩展属性、资源叉或 zip 异常 | MAC-H06 |
| NET 网络/权限 | 端口、localhost、IPv4/IPv6、TCC 或本地网络提示 | MAC-H02 |
| SEC 签名/密钥 | Gatekeeper、quarantine、codesign、公证、密钥或产物泄露 | M-RES-03、M-RES-08 |
| EVIDENCE 假绿 | 测试/CI/runner 覆盖不足，或只看工具存在 | M-RES-01、M-RES-02、MAC-H08 |
| DELIVERY 交付 | 备份、迁移、回滚、交接或部署漂移 | M-RES-05 |

## 条目

- 2026-11-10 | architecture, rosetta | 在 Apple Silicon 上执行正式检查 | 只看 `uname -m`，或在 Rosetta 终端里继续跑依赖与回归 | 同时要求 `uname -m`、`arch` 为 `arm64`，且 `sysctl -in sysctl.proc_translated` 为 `0`；不满足就停止 | GitHub macOS workflow 内置硬门禁；契约测试检查三个条件
- 2026-11-10 | packaging, scope | 从通用 skill 拆出 macOS 专用包 | 只删文档，却保留非 macOS 校验器和命令 | 删除非 macOS 脚本与避坑文件；包校验器按后缀、文件名和正文关键词 fail-closed | `tests/test_contract.py` 的包范围反例和 `scripts/verify_package.py`
- 2026-11-10 | privacy, redaction | 扫描 macOS 主目录路径 | 只匹配 Linux `/home/`，真实 `/Users/<name>` 进入公开报告 | 增加 `/Users/<name>` 模式，同时放行 `/Users/<you>`、`/Users/Shared` 和 `/Users/Guest` | 脱敏扫描器自检及 macOS 路径正反例测试
- 2026-11-10 | architecture, tooling | 混用 Homebrew、Python、Node、JDK 或容器 | 只看命令能启动，不检查二进制架构 | 用 `brew --prefix`、`file`、`lipo -info`、`python3 -c 'import platform; print(platform.machine())'` 和 Docker server arch 交叉确认 | GitHub macOS runner 实际执行环境探测
- 2026-11-10 | filesystem, git | 在大小写不敏感的 APFS 卷上审查路径 | 假设只改文件名大小写一定会被 Git 和构建系统识别 | 用实际目录枚举和 `git status --short` 验证；需要时在大小写敏感卷或 Linux 上复核 | 2026-11-11 起由 `smoke_macos_runtime.sh` 在 GitHub macOS runner 探测当前卷大小写行为；区分大小写 APFS 卷仍需人工复核
- 2026-11-10 | github-actions, architecture, runner | 用 GitHub 免费 macOS runner 验证原生架构 | 把 runner 规格写死为 M1 / 3 CPU / 7 GB，实测却是 Apple M2 Pro (Virtual) / 5 逻辑 CPU / 14 GiB；2026-11-11 同一工作流又分配到 Apple M1 (Virtual) | 只把 `arm64` 和 Rosetta `0` 当硬条件；芯片、CPU、内存和 macOS 版本每次从日志记录，报告不得外推到所有 M 系列 | run 42794677614（M2 Pro）与 run 42945341701（M1）的 Python 3.9/3.12 两套 Job 均输出 macOS 26.7.2、arm64、Rosetta 0 并 PASS
- 2026-11-13 | ports, networking, tcc | macOS 服务连接失败或端口检查异常 | 只跑 `lsof` 看到一个端口占用，就关闭 AirPlay、默认 `sudo` 或强杀系统进程；只测 `localhost`，没有区分 IPv4/IPv6 | 先查 5000/7000 与 `ControlCenter`，分别用 `curl -4`/`curl -6`；记录本地网络/TCC 权限和会话类型，不把权限拒绝误判成服务崩溃 | 监听者、IPv4/IPv6 结果和权限记录齐全
- 2026-11-13 | xcode, sdk, license | 工程能编译但不确定是否用了完整 Xcode | 看到 `xcode-select -p` 有输出就认为完整 Xcode、SDK、license 和部署目标都正确 | 记录 `xcodebuild -version`、`xcrun --show-sdk-path`、`xcodebuild -showsdks`、`MACOSX_DEPLOYMENT_TARGET`；CLT-only 不能证明完整 Xcode 工程通过 | Xcode 路径、SDK、license 和构建日志一致
- 2026-11-13 | toolchain, dylib, signing | Python/Node/Java 原生模块或 dylib 能加载 | 只检查版本号，或注入 `DYLD_LIBRARY_PATH` 后看到能跑就判定兼容；修改 dylib 后不重签名 | 用 `file`、`lipo -info`、`platform.machine()`、`process.arch`、`java -XshowSettings`、`otool -L` 交叉确认；修改后重新签名并检查 entitlement | 解释器、原生模块、dylib 架构和签名一致
- 2026-11-13 | performance, baseline | 用 M1 的并发/线程数评估 M5/M6 性能 | 把固定 worker 数、连接池或 Docker CPU 限制跨世代照搬 | 记录芯片、核心、内存、`vm_stat` 和负载参数；按目标世代重建基线；`powermetrics` 不能默认可用 | 硬件信息、负载和性能结果绑定
- 2026-11-13 | docs, sync | 更新隐藏坑清单 | 只改专用版或只改中文，专业版/英文版漏同步 | 用 `MAC-H01`～`MAC-H08` 共享编号同时更新两仓库中英文参考、SKILL 表和契约测试 | 两个仓库的契约测试均检查编号和关键证据
2026-11-13 | testing, macos, paths | 在 macOS 上比较临时目录路径时直接比较未规范化的 Path | 把 /var 与 /private/var 当作不同目录，导致契约测试假失败 | 比较前对两边调用 resolve()，或使用 samefile；不要硬编码私有前缀 | GitHub macOS runner 上 Python 3.9/3.12 契约测试通过
