# Changelog

## 1.0.1 - 2026-11-11

- Documented the upstream `project-health` v1.2.4 PolyForm Noncommercial provenance and the maintainer's Apache-2.0 relicensing in `PROVENANCE.md` and `PROVENANCE.en.md`.
- Preserved the upstream Required Notice and added package-verifier and contract-test checks for the provenance chain.
- Clarified that M1-M6 `arm64` compatibility is a platform fact, while CI hardware validation remains limited to the observed Apple M2 Pro (Virtual) runner.
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
