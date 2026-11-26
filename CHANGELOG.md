# Changelog

## 1.1.1 - 2026-11-26

### 中文

- 修正结构经验写入范围：Git 克隆安装到 `skills/project-health-macos` 时改为写 `STRUCTURE.local.md`，不再修改随包维护的中文结构手册。
- 修复英文结构经验写入和仓库英文手册选择；本地条目语言与章节标题语言解耦，并允许全新安装的默认检查报告“尚无本地手册”。
- 收紧状态规则：`已过时` 条目只允许软提示，禁止使用详细注入。
- 扩展 macOS 脱敏扫描：新增 `Authorization: Bearer`、长值 Cookie 头和 JWT 的正反例。
- 更新 `1.1.1` 版本、引文和试用说明；GitHub CI 结果需在推送后补录。

### English

- Fix structural-experience write scope: Git clones installed under `skills/project-health-macos` now write `STRUCTURE.local.md` instead of modifying the maintained Chinese structural manual.
- Fix English structural writes and selection of the English repository manual; local entry language is decoupled from chapter-heading language, and a fresh-install default check can report that no local manual exists yet.
- Tighten status rules so `obsolete` entries may only use soft hints and cannot use detailed injection.
- Extend the macOS redaction scanner with positive and negative cases for `Authorization: Bearer`, long Cookie-header values, and JWTs.
- Update the `1.1.1` version, citation, and trial guide. GitHub CI evidence must be added after pushing.

## 1.1.0 - 2026-11-24

- 增加 macOS 专用常驻隐藏坑绊线、按需索引、空白结构经验手册、扁平 schema 和仅 macOS 的受控写入器；同步报告覆盖、核验脚本和契约测试。

## 1.0.4 - 2026-11-18

- Clarified that package verification, contract tests, the macOS smoke test, and CI do not validate real agent behavior; real behavior evaluation is separate and is not a release gate.
- Added the model, host, permission mode, date, evidence, and uncovered-scope record fields to the validation guidance.
- Synced version metadata, READMEs, SKILL files, CITATION, trial guide, and contract tests.
- Documented the single-trunk branch policy and added a pull-request checklist.

## 1.0.3 - 2026-11-13

- Added `scripts/record_pitfall.py` with fail-closed path handling, exact deduplication, history preservation, and checks for separators, newlines, secrets, and personal paths.
- Installed skills now use `PITFALLS.local.md`; maintainers use `PITFALLS.md`. The local file is created on first use and preserved across upgrades.
- Added the autonomous memory checkpoint, parent-ID rule for new mechanisms under an existing class, reusable project failure-mode scope, and the memory result in the final report.
- Added recorder tests, evaluator tests, and two baseline-unseen false-green scenarios. The real agent evaluation is optional and is not invoked by default CI.
- Documented local memory in the README and preservation during upgrades.
- Fixed false path-assertion failures caused by the `/var` to `/private/var` symlink on macOS; normalize paths before cross-platform comparisons.

## 1.0.2 - 2026-11-13

- Added the shared `MAC-H01` through `MAC-H08` hidden-pitfall baseline with the professional `project-health` edition.
- Documented AirPlay Receiver on ports 5000/7000, `localhost` resolving to `::1`, macOS local-network/TCC prompts, and safe port diagnosis.
- Expanded toolchain guidance for universal2 wheels, Node native modules, JNI/dylib architecture, `DYLD_*` under SIP, entitlements, and re-signing.
- Clarified Command Line Tools versus full Xcode, Xcode selection, SDK/deployment-target checks, and read-only license verification.
- Added performance-baseline warnings across M1-M6 and new false-pass cases for Xcode, dylibs, ports, and runner coverage.
- Updated README, TRIAL, CITATION, SKILL, and contract tests to version `1.0.2`; both Chinese and English references now carry the shared IDs.

## 1.0.1 - 2026-11-11

- Documented the upstream `project-health` v1.2.4 PolyForm Noncommercial provenance and the maintainer's Apache-2.0 relicensing in `PROVENANCE.md` and `PROVENANCE.en.md`.
- Recorded the maintainer's confirmation that the upstream work was independently created with no other human authors.
- Preserved the upstream Required Notice and added package-verifier and contract-test checks for the provenance chain.
- Clarified that M1-M6 `arm64` compatibility is a platform fact, while CI hardware validation remains limited to the observed runner pool (Apple M2 Pro and M1 virtual runners, both macOS 26.7.2).
- Added an APFS case-behavior probe to the macOS smoke test and recorded the remaining case-sensitive-volume limitation.
- Fixed the trial feedback count, added upgrade guidance, and documented how to restore the entry file after switching languages.

## 1.0.0 - 2026-11-10

- Extracted a macOS-only deep project-health skill from `project-health` v1.2.4.
- Removed non-macOS trap documents and shell-specific verification paths.
- Added Apple Silicon coverage from M1 onward, including Rosetta, Homebrew prefixes, multi-architecture dependencies, and Docker image architecture.
- Added macOS command references for BSD userland differences, Gatekeeper/quarantine, launchd, APFS, TCC, and local container storage.
- Added `/Users/<real-name>` detection to the redaction scanner.
- Added package-scope checks that fail when non-macOS artifacts or commands leak back into the repository.
- Added macOS GitHub Actions verification.
- Added a bilingual human-trial guide with a native Apple Silicon gate, installation steps, self-check commands, and a feedback template.
- Recorded the GitHub macOS runner as a changing Apple Silicon pool instead of hard-coding M1; GitHub CI observed macOS 26.7.2, Xcode 26.6, SDK 26.5, Apple M2 Pro (Virtual), 5 logical CPUs, and 14 GiB memory.
- Relicensed the project under Apache License 2.0 with copyright attributed to fallen-leaves (GitHub: Fallen-leaves089).
- Added an OpenSSH Ed25519 release-signing key, allowed-signers file, and bilingual verification instructions.
