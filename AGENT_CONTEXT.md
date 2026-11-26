# Agent Context

- **Repository role**: macOS-only derivative of `project-health`, focused on Apple Silicon, Xcode/SDK, Rosetta, Homebrew, signing, Gatekeeper/TCC, launchd, APFS, and macOS CI differences.
- **Shared semantics**: common safety, versioning, memory, and redaction behavior should track the canonical `project-health` source.
- **Platform boundary**: do not copy general professional rules over macOS-specific checks or weaken the native arm64 requirement.
- **Public contract**: the installed Skill must remain self-contained.
- **Start with**: `AGENTS.md`, `SKILL.md`, `CHANGELOG.md`, then the relevant macOS scripts and tests.
