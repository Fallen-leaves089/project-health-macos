from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCHEMA = json.loads(
    (ROOT / "scripts" / "structure-schema.json").read_text(encoding="utf-8")
)


def read_text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


class StructuralExperienceContractTests(unittest.TestCase):
    def test_blank_manual_and_macos_rules_are_wired(self) -> None:
        chinese = read_text("references/structural-experience.md")
        english = read_text("references/structural-experience.en.md")
        for content in (chinese, english):
            self.assertIn("schema-version: 1", content)
            self.assertIn("no fixed depth limit" if content is english else "不设固定层数", content)
        for chapter in SCHEMA["chapter_ids"]:
            self.assertIn(f"### {chapter}.", chinese)
            self.assertIn(f"### {chapter}.", english)

        skill = read_text("SKILL.md")
        agents = read_text("AGENTS.md")
        for phrase in ("M-RES-01～09", "A-F", "record_structure.py", "祖先"):
            self.assertIn(phrase, skill)
        self.assertIn("结构经验", agents)
        self.assertIn("M-RES-01～08", agents)
        self.assertIn("总数超过 12", agents)

    def test_report_templates_include_resident_and_structure_sections(self) -> None:
        for relative, resident, structure in (
            (
                "references/report-template.md",
                "常驻隐藏坑覆盖",
                "结构经验回收",
            ),
            (
                "references/report-template.en.md",
                "Resident hidden-pitfall coverage",
                "Structural experience harvest",
            ),
        ):
            content = read_text(relative)
            self.assertIn(resident, content)
            self.assertIn(structure, content)
            for chapter in ("A", "B", "C", "D", "E", "F"):
                self.assertIn(f"| {chapter} |", content)

    def test_structural_entries_follow_schema(self) -> None:
        segment = str(SCHEMA["branch_segment_pattern"]).strip("^$")
        branch = rf"[A-F]/{segment}(?:/{segment})+"
        status_labels = sorted(
            (
                label
                for key in SCHEMA["status_keys"]
                for label in SCHEMA["status_labels"][key]
            ),
            key=len,
            reverse=True,
        )
        injection_labels = sorted(
            (
                label
                for key in SCHEMA["injection_keys"]
                for label in SCHEMA["injection_labels"][key]
            ),
            key=len,
            reverse=True,
        )
        entry_re = re.compile(
            rf"^- (S-([A-F])-\d{{3}}) \| "
            rf"({'|'.join(re.escape(label) for label in status_labels)}) \| "
            rf"({'|'.join(re.escape(label) for label in injection_labels)}) \| "
            rf"({branch}) \| "
            rf"({branch}(?:; {branch})*|无|none) \| "
            rf"([^|\n]+) \| ([^|\n]+) \| ([^|\n]+) \| ([^|\n]+) \| ([^|\n]+)$"
        )
        pending = set(SCHEMA["status_labels"]["pending"])
        detailed = set(SCHEMA["injection_labels"]["detailed"])
        for relative in (
            "references/structural-experience.md",
            "references/structural-experience.en.md",
        ):
            current = None
            seen = set()
            lines = read_text(relative).splitlines()
            for index, line in enumerate(lines, start=1):
                match = re.match(r"^### ([A-F])\.", line)
                if match:
                    current = match.group(1)
                    continue
                if not line.startswith("- S-"):
                    continue
                entry = entry_re.match(line)
                self.assertIsNotNone(entry, msg=f"{relative}:{index}: malformed entry")
                if entry is None:
                    continue
                entry_id, chapter, status, injection = entry.groups()[:4]
                self.assertNotIn(entry_id, seen)
                seen.add(entry_id)
                self.assertEqual(chapter, current)
                if status in pending:
                    self.assertNotIn(injection, detailed)


if __name__ == "__main__":
    unittest.main()
