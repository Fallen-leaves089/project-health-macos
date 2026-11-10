# Changelog

## 1.0.0 - 2026-11-10

- Extracted a macOS-only deep project-health skill from `project-health` v1.2.4.
- Removed non-macOS trap documents and shell-specific verification paths.
- Added Apple Silicon coverage from M1 onward, including Rosetta, Homebrew prefixes, multi-architecture dependencies, and Docker image architecture.
- Added macOS command references for BSD userland differences, Gatekeeper/quarantine, launchd, APFS, TCC, and local container storage.
- Added `/Users/<real-name>` detection to the redaction scanner.
- Added package-scope checks that fail when non-macOS artifacts or commands leak back into the repository.
- Added macOS GitHub Actions verification.
- Added a bilingual human-trial guide with a native Apple Silicon gate, installation steps, self-check commands, and a feedback template.
- Recorded the GitHub macOS runner as a changing Apple Silicon pool instead of hard-coding M1; the first private CI run observed macOS 26.7.2 on Apple M2 Pro (Virtual).
