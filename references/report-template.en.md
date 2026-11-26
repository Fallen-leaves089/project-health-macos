# <PROJECT> Project Health Check Report

[中文](report-template.md) | **English**

- Check date: `YYYY-MM-DD`
- Reviewer: `<NAME>`
- Review mode: `change review / full review / no-Git snapshot`
- Baseline: `<COMMIT / BRANCH / TAG>`
- Worktree state: `clean / uncommitted changes (describe handling)`
- Rules used: `project conventions / external rule pack / combination`
- Coverage: `backend / frontend / mobile / database / containers / deployment`
- Not covered: `...`

## Three actions to take now

1. `...`
2. `...`
3. `...`

> At most 3 actions the user can take today. If evidence is insufficient, name the verification to add first; do not pad the list.

## Executive summary

- P0: `N`
- P1: `N`
- P2: `N`
- P3: `N`
- Overall decision: `ready to deploy / deploy after P0 and P1 are fixed / not ready`
- One-line risk: `...`

## P0 Will break on deployment day

| ID | Location | Problem | Impact | Recommendation | Verification | Confidence | Status |
|---|---|---|---|---|---|---|---|
| P0-1 | `file:line` | ... | ... | ... | ... | verified / observed / inferred | Open |

## P1 Must be fixed before deployment

| ID | Location | Problem | Impact | Recommendation | Verification | Confidence | Status |
|---|---|---|---|---|---|---|---|
| P1-1 | `file:line` | ... | ... | ... | ... | verified / observed / inferred | Open |

## P2 Recommended before deployment

| ID | Location | Problem | Impact | Recommendation | Verification | Confidence | Status |
|---|---|---|---|---|---|---|---|
| P2-1 | `file:line` | ... | ... | ... | ... | verified / observed / inferred | Open |

## P3 Hygiene and maintainability

| ID | Location | Problem | Recommendation | Confidence | Status |
|---|---|---|---|---|---|
| P3-1 | `file:line` | ... | ... | verified / observed / inferred | Open |

## Verified with no issue

- `<module / check>`: `evidence / command / result`
- ...

## Not covered this round

- `<module / check>`: `reason (environment, permission, time, missing fixture)`
- ...

## Reproduction commands

```bash
# Baseline
git rev-parse <COMMIT>
git diff <COMMIT>...HEAD --stat

# Tests
<command>

# Build
<command>

# Migration/container regression
<command>
```

## Environment and versions

- OS: `macOS <version>`
- Hardware / architecture: `Apple Silicon <generation>`, `arm64`; Rosetta state: `0`
- Shell: `<zsh / bash version>`
- Xcode Command Line Tools: `<version>`
- Node / Java / Python: `<version>`
- Docker / Compose: `<version>`
- Docker image architecture: `<arm64 / amd64>`
- Database: `<version>`
- Browser / emulator: `<version>`

## Evidence and attachments

- Logs: `<path>` (redacted)
- Screenshots: `<path>` (redacted)
- Packet capture: `<path>` (redacted)
- Build artifact: `<path>`

## Fix log

| Date | Item | Change | Regression result | Commit |
|---|---|---|---|---|
| `YYYY-MM-DD` | P0-1 | ... | ... | `<sha>` |

## Resident hidden-pitfall coverage

### Baseline resident set (M-RES-01 through M-RES-08)

| Tripwire | Status | Evidence |
|---|---|---|
| M-RES-01 false green / skipped tests | checked / not applicable / uncovered | `...` |
| M-RES-02 swallowed exit code | checked / not applicable / uncovered | `...` |
| M-RES-03 secrets/personal data in artifacts | checked / not applicable / uncovered | `...` |
| M-RES-04 ownership supplied by the client | checked / not applicable / uncovered | `...` |
| M-RES-05 backup/restore/rollback not exercised | checked / not applicable / uncovered | `...` |
| M-RES-06 Rosetta treated as native | checked / not applicable / uncovered | `...` |
| M-RES-07 Xcode/CLT and SDK mismatch | checked / not applicable / uncovered | `...` |
| M-RES-08 Gatekeeper/signing/notarization failure | checked / not applicable / uncovered | `...` |

### User-promoted resident set (M-RES-09)

| URES ID | Source entry | Minimal user quote | Upgraded at | Scope | Revocation/downgrade condition | Current status |
|---|---|---|---|---|---|---|
| none | - | - | - | - | - | M-RES-09 not triggered |

- M-RES-09 promotion control: not triggered / applied / not applicable / uncovered
- Resident capacity: baseline 8 + user-promoted `N` = `M`; when `M > 12`, recommend reviewing downgrade candidates

> All eight baseline rows, M-RES-09 control, and every user-promoted entry need a status. `uncovered` must never be reported as passed.

## Structural experience harvest

| Primary chapter | Deepest path | Chapter coverage | Branch result | Entry matched | Entry status | Injection | Evidence |
|---|---|---|---|---|---|---|---|
| A | `A/<slug>/...` | opened / no signal / not applicable / cross-chapter reference / unclassified | leaf match / ancestor match / explored with no match (report only) / insufficient granularity / conflict (group not injected) | none / `S-...` | none / `verified / pending verification / obsolete` | none / `detailed / brief / soft hint` | `...` |
| B | ... | ... | ... | ... | ... | ... | `...` |
| C | ... | ... | ... | ... | ... | ... | `...` |
| D | ... | ... | ... | ... | ... | ... | `...` |
| E | ... | ... | ... | ... | ... | ... | `...` |
| F | ... | ... | ... | ... | ... | ... | `...` |

> Keep one row for every A-F chapter. Sibling depth is a warning only.

- Entries matched: none / `S-...` (primary `X`; primary branch `...`; related branches `...`)
- Conflict group: none / `S-..., S-...`
- Current-project verification: none / `evidence and result`
- Added: none / `N` (`references/structural-experience.en.md` or `STRUCTURE.local.md`)
- Recording action: automatically written / no additions / write failed (`reason and pending content`)

## Notes

- Secrets, tokens, cookies, client names, real domains, and private IPs in this report have been redacted.
- Line numbers refer to the baseline; recheck them after fixes.
