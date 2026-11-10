#!/usr/bin/env python3
"""Verify the macOS-only skill package.

Checks:
  * required files and bilingual companions are present
  * text files are UTF-8 without BOM
  * relative Markdown links resolve
  * both SKILL frontmatters share the expected name, version, and license
  * language links are present in the README and SKILL files
  * non-macOS trap files and commands have not leaked into the package
  * the redaction scanner passes its self-test and a package scan

Exit codes:
  0 = package passed
  1 = one or more checks failed
  2 = usage error
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


SCRIPT_PATH = Path(__file__).resolve()
DEFAULT_ROOT = SCRIPT_PATH.parent.parent
SCANNER = SCRIPT_PATH.parent / "check_redaction.py"

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".env",
    ".sh",
    ".zsh",
    ".js",
    ".ts",
    ".py",
    ".swift",
    ".plist",
    ".pbxproj",
    ".xcconfig",
    ".entitlements",
    ".fixture",
    ".xml",
    ".properties",
    ".pub",
    "",
}

SKIP_DIRS = {
    ".git",
    "node_modules",
    "bin",
    "obj",
    "dist",
    "build",
    ".build",
    "DerivedData",
    "Pods",
    "Carthage",
    ".venv",
    "__pycache__",
    ".idea",
}

REQUIRED_FILES = [
    "SKILL.md",
    "SKILL.en.md",
    "AGENTS.md",
    "PITFALLS.md",
    "README.md",
    "README.en.md",
    "TRIAL.md",
    "LICENSE",
    "LICENSE.zh-CN.md",
    "NOTICE",
    "SIGNING.md",
    "SIGNING.en.md",
    "allowed_signers",
    "release-signing-key.pub",
    "SECURITY.md",
    "CHANGELOG.md",
    ".gitattributes",
    ".gitignore",
    ".editorconfig",
    ".github/workflows/verify.yml",
    "references/platform-commands.md",
    "references/platform-commands.en.md",
    "references/macos-pitfalls.md",
    "references/macos-pitfalls.en.md",
    "references/verification-playbook.md",
    "references/verification-playbook.en.md",
    "references/report-template.md",
    "references/report-template.en.md",
    "scripts/check_redaction.py",
    "scripts/verify_package.py",
    "scripts/check_macos_env.sh",
    "scripts/smoke_macos_runtime.sh",
    "tests/test_contract.py",
    "tests/fixtures/malicious-target/malicious-agents.fixture",
]

LANGUAGE_LINKS = {
    "README.md": ("[中文](README.md)", "[English](README.en.md)"),
    "README.en.md": ("[中文](README.md)", "[English](README.en.md)"),
    "SKILL.md": ("[中文](SKILL.md)", "[English](SKILL.en.md)"),
    "SKILL.en.md": ("[中文](SKILL.md)", "[English](SKILL.en.md)"),
}

LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def _is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def _iter_text_files(root: Path) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in relative_parts):
            continue
        if _is_text_file(path):
            yield path


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _read_frontmatter(path: Path) -> Dict[str, str]:
    lines = _read_text(path).splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    fields: Dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return {}


def _check_encoding(files: Iterable[Path], root: Path) -> List[str]:
    failures: List[str] = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            failures.append(f"UTF-8 BOM found: {relative}")
        try:
            data.decode("utf-8")
        except UnicodeDecodeError:
            failures.append(f"Not valid UTF-8: {relative}")
    return failures


def _check_links(root: Path) -> Tuple[List[str], int]:
    failures: List[str] = []
    markdown_files = [path for path in _iter_text_files(root) if path.suffix.lower() == ".md"]

    for markdown in markdown_files:
        relative = markdown.relative_to(root).as_posix()
        for line_number, line in enumerate(_read_text(markdown).splitlines(), start=1):
            for match in LINK_RE.finditer(line):
                target = match.group(1).strip()
                if target.startswith("<") and target.endswith(">"):
                    target = target[1:-1].strip()
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = target.split("#", 1)[0].strip()
                if not target:
                    continue
                target = target.replace("\\", "/")
                candidate = (markdown.parent / target).resolve()
                if not candidate.exists():
                    failures.append(f"Broken relative link: {relative}:{line_number} -> {target}")

    return failures, len(markdown_files)


def _check_language_links(root: Path) -> List[str]:
    failures: List[str] = []
    for relative, links in LANGUAGE_LINKS.items():
        path = root / relative
        if not path.exists():
            continue
        content = _read_text(path)
        for link in links:
            if link not in content:
                failures.append(f"Missing language link in {relative}: {link}")
    return failures


def _check_frontmatter(root: Path) -> List[str]:
    failures: List[str] = []
    expected_name = "project-health-macos"
    expected_license = "Apache-2.0"
    versions: Dict[str, str] = {}

    for relative in ("SKILL.md", "SKILL.en.md"):
        path = root / relative
        if not path.exists():
            continue
        fields = _read_frontmatter(path)
        if not fields:
            failures.append(f"Missing or invalid frontmatter: {relative}")
            continue
        if fields.get("name") != expected_name:
            failures.append(f"Frontmatter name mismatch in {relative}: {fields.get('name', '<missing>')}")
        if fields.get("license") != expected_license:
            failures.append(
                f"Frontmatter license mismatch in {relative}: {fields.get('license', '<missing>')}"
            )
        version = fields.get("version", "")
        if not re.fullmatch(r"\d+\.\d+\.\d+", version):
            failures.append(f"Frontmatter version missing or invalid in {relative}: {version or '<missing>'}")
        else:
            versions[relative] = version

    if len(set(versions.values())) > 1:
        failures.append("SKILL.md and SKILL.en.md versions do not match: " + ", ".join(
            f"{name}={version}" for name, version in sorted(versions.items())
        ))

    license_text = _read_text(root / "LICENSE")
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        failures.append("LICENSE does not contain the Apache License 2.0 text")

    public_key = _read_text(root / "release-signing-key.pub").strip()
    allowed_signers = _read_text(root / "allowed_signers").strip()
    if not allowed_signers.startswith("project-health-macos-release "):
        failures.append("allowed_signers has an unexpected signing principal")
    if public_key not in allowed_signers:
        failures.append("allowed_signers does not match release-signing-key.pub")

    return failures


def _check_macos_scope(root: Path) -> List[str]:
    failures: List[str] = []
    forbidden_suffixes = {".ps1", ".psm1", ".cmd", ".bat"}
    forbidden_name_parts = ("windows-pitfalls", "windows-powershell")

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if path.suffix.lower() in forbidden_suffixes:
            failures.append(f"Non-macOS script artifact found: {relative}")
        lowered = relative.lower()
        if any(part in lowered for part in forbidden_name_parts):
            failures.append(f"Non-macOS trap document found: {relative}")

    forbidden_tokens = (
        "powershell",
        "get-nettcpconnection",
        "windows-pitfalls",
        "wsl.exe",
        "mvnw.cmd",
        "gradlew.bat",
        "copy-item",
        "get-childitem",
    )
    windows_word = re.compile(r"\bWindows\b", re.IGNORECASE)
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative.startswith(("tests/", "scripts/verify_package.py")):
            continue
        if path.suffix.lower() not in {".md", ".yml", ".yaml"}:
            continue
        content = _read_text(path)
        lowered = content.lower()
        for token in forbidden_tokens:
            if token in lowered:
                failures.append(f"Non-macOS command or artifact reference in {relative}: {token}")
        if windows_word.search(content):
            failures.append(f"Non-macOS platform reference in {relative}: Windows")

    return failures


def _run_scanner(root: Path) -> Tuple[List[str], str]:
    failures: List[str] = []
    if not SCANNER.exists():
        return [f"Missing redaction scanner: {SCANNER.name}"], ""

    self_test = subprocess.run(
        [sys.executable, str(SCANNER), "--self-test"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if self_test.returncode != 0:
        failures.append("Redaction scanner self-test failed.")

    package_scan = subprocess.run(
        [sys.executable, str(SCANNER), "--path", str(root), "--quiet"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if package_scan.returncode != 0:
        failures.append("Redaction package scan reported findings or failed.")
        if package_scan.stdout.strip():
            failures.extend(
                f"Redaction finding: {line.strip()}"
                for line in package_scan.stdout.splitlines()
                if line.strip()
            )

    return failures, package_scan.stdout.strip()


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--path",
        type=Path,
        default=DEFAULT_ROOT,
        help="package root (default: parent of the scripts directory)",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    root = args.path.resolve()

    if not root.exists():
        print(f"ERROR: path not found: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print("ERROR: path must be a directory.", file=sys.stderr)
        return 2

    failures: List[str] = []

    for relative in REQUIRED_FILES:
        if not (root / relative).exists():
            failures.append(f"Missing required file: {relative}")

    text_files = list(_iter_text_files(root))
    failures.extend(_check_encoding(text_files, root))
    link_failures, markdown_count = _check_links(root)
    failures.extend(link_failures)
    failures.extend(_check_frontmatter(root))
    failures.extend(_check_language_links(root))
    failures.extend(_check_macos_scope(root))

    scanner_failures, _ = _run_scanner(root)
    failures.extend(scanner_failures)

    print(f"Checked {len(text_files)} text file(s), {markdown_count} Markdown file(s).")
    if failures:
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        print("PACKAGE VERIFY FAILED.", file=sys.stderr)
        return 1

    print("PACKAGE VERIFY PASSED.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
