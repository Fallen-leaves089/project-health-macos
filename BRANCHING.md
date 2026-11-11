# 分支与发布维护

本仓库采用**单主干维护**：`main` 始终保持可发布，所有改动通过短分支和 Pull Request 回到 `main`。

## 长期分支

- `main`：唯一长期分支，必须保持可发布。
- 不设长期 `develop` 分支，避免双主干漂移和重复合并。

## 短分支

从 `main` 创建，完成后通过 PR 回到 `main`：

- `feat/<topic>`：新功能；
- `fix/<topic>`：缺陷修复；
- `docs/<topic>`：文档；
- `test/<topic>`：测试和验证；
- `chore/<topic>`：维护、CI、依赖和发布流程；
- `release/<version>`：仅在维护旧版本补丁时，从对应 tag 创建。

合并方式使用 squash merge，合并后自动删除 head 分支。

## PR 门禁

- GitHub Actions 必须通过 `macOS Apple Silicon / Python 3.9` 和 `macOS Apple Silicon / Python 3.12`；
- 本地自检必须通过包校验、契约测试和脱敏自检；
- 用户可见改动必须同步更新 `CHANGELOG.md` 和版本号；
- 许可证、来源或归属变更必须同步更新 `PROVENANCE.md`、`NOTICE` 和契约测试；
- PR 中不得包含密钥、令牌、客户数据或真实 `/Users/<name>` 路径。

## 发布约定

- 版本 tag 使用 `vX.Y.Z`，打在 `main` 的发布提交上；
- 已发布的 tag 和 Release 资产不移动、不覆盖；
- 旧版本需要补丁时，从对应 tag 创建 `release/X.Y.x`，发布补丁版本后把必要修复回合 `main`；
- 发布包继续使用 OpenSSH Ed25519 签名，并保留 `PROVENANCE.md` 和上游 Required Notice。

## 清理规则

- 合并后的短分支自动删除；
- 未合并分支超过 30 天，先确认是否仍有用途，再决定关闭或删除；
- 不删除已发布 tag，不强制推送 `main`。

## English summary

- `main` is the only long-lived branch and must stay release-ready.
- Create short-lived `feat/`, `fix/`, `docs/`, `test/`, `chore/`, or `release/` branches from `main`, then open a PR back to `main`.
- Use squash merge and auto-delete the head branch. Do not add a long-lived `develop` branch.
- `main` requires the macOS CI checks, blocks force-pushes and deletion, and accepts changes through pull requests.
- Published tags and release assets are immutable. Create `release/X.Y.x` only when an older release line needs a patch.
