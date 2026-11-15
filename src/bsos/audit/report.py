"""Findings, acknowledgements, and the Markdown report."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import tomlkit


@dataclass(frozen=True)
class Finding:
    """One thing the audit noticed.

    *check* and *subject* form the stable :attr:`key` used to acknowledge it
    (``archived:mozilla/bleach``); *detail* is the human explanation and may
    change from run to run. *action* findings need a decision and fail the
    audit; the rest are informational.
    """

    check: str
    subject: str
    detail: str
    action: bool = True

    @property
    def key(self) -> str:
        return f"{self.check}:{self.subject}"


@dataclass(frozen=True)
class Ack:
    """A reviewed finding: why it is acceptable, and until when."""

    reason: str
    until: date


@dataclass
class Report:
    action: list[Finding] = field(default_factory=list)
    info: list[Finding] = field(default_factory=list)
    acknowledged: list[tuple[Finding, Ack]] = field(default_factory=list)


def load_acks(path: Path) -> dict[str, Ack]:
    """Read ``audit-ack.toml``: one table per finding key, each with ``reason`` and ``until``.

    Both fields are required. An acknowledgement without an expiry is a
    finding nobody will ever look at again, which is how lists rot.
    """
    if not path.is_file():
        return {}
    doc: dict[str, Any] = tomlkit.parse(path.read_text(encoding="utf-8")).unwrap()
    acks: dict[str, Ack] = {}
    for key, entry in doc.items():
        reason = entry.get("reason") if isinstance(entry, dict) else None
        until = entry.get("until") if isinstance(entry, dict) else None
        if not isinstance(reason, str) or not reason.strip() or not isinstance(until, date):
            raise ValueError(f'{path}: ["{key}"] needs a non-empty `reason` and an `until` date (e.g. 2027-06-01)')
        acks[key] = Ack(reason.strip(), until)
    return acks


def triage(findings: Iterable[Finding], acks: dict[str, Ack], today: date, *, complete: bool = True) -> Report:
    """Sort *findings* into action / informational / acknowledged.

    An acknowledgement past its ``until`` no longer hides its finding. With
    *complete* (every check ran), an acknowledgement that matches nothing is
    reported so the file does not accumulate dead entries.
    """
    report = Report()
    seen: set[str] = set()
    for finding in sorted(set(findings), key=lambda f: f.key):
        seen.add(finding.key)
        ack = acks.get(finding.key)
        if ack is not None and ack.until >= today:
            report.acknowledged.append((finding, ack))
            continue
        if ack is not None:
            finding = Finding(
                finding.check,
                finding.subject,
                f"{finding.detail} (acknowledgement expired {ack.until}: {ack.reason})",
                finding.action,
            )
        (report.action if finding.action else report.info).append(finding)
    if complete:
        for key in sorted(set(acks) - seen):
            report.info.append(
                Finding("unused-ack", key, "matches no current finding; remove it from the ack file", False)
            )
    return report


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _table(findings: Iterable[Finding]) -> list[str]:
    lines = ["| Finding | Detail |", "|---|---|"]
    lines += [f"| `{_cell(f.key)}` | {_cell(f.detail)} |" for f in findings]
    return lines


def render(report: Report, today: date, *, ack_file: str = "audit-ack.toml") -> str:
    """The audit as Markdown (job summary / terminal)."""
    out = [
        f"# Dependency audit — {today}",
        "",
        f"**{len(report.action)} need a decision**, {len(report.info)} informational, "
        f"{len(report.acknowledged)} acknowledged.",
    ]
    if report.action:
        out += [
            "",
            "## Needs a decision",
            "",
            f'Fix it, or acknowledge it in `{ack_file}` (`["<finding>"]` with a `reason` and an `until` date).',
            "",
            *_table(report.action),
        ]
    if report.info:
        out += ["", "## Informational", "", *_table(report.info)]
    if report.acknowledged:
        out += ["", "## Acknowledged", "", "| Finding | Reason | Until |", "|---|---|---|"]
        out += [f"| `{_cell(f.key)}` | {_cell(a.reason)} | {a.until} |" for f, a in report.acknowledged]
    return "\n".join(out) + "\n"
