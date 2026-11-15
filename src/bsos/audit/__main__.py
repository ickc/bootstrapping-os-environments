"""Run the dependency audit and print it as Markdown."""

from __future__ import annotations

import os
import sys
from datetime import date
from pathlib import Path
from typing import Callable

import defopt

from bsos.audit import conda, darwin, upstream
from bsos.audit.report import Finding, load_acks, render, triage

CHECKS: dict[str, Callable[[Path, date], list[Finding]]] = {
    "conda": lambda root, today: conda.audit(root / "conda", today),
    "upstream": lambda root, today: upstream.audit(root / "conda", today),
    "darwin": lambda root, today: darwin.audit(root / "nix", today),
}


def audit(
    *,
    root: Path = Path("."),
    ack: Path = Path("audit-ack.toml"),
    checks: list[str] = list(CHECKS),
) -> None:
    """Audit the pinned environments and package lists for abandoned or rotting dependencies.

    Exits 1 when something needs a decision, so a green run means nothing new.
    The report also goes to the GitHub Actions job summary when run there.

    :param root: repository root
    :param ack: acknowledged findings (relative to root)
    :param checks: which checks to run (conda, upstream, darwin); default all
    """
    unknown = sorted(set(checks) - set(CHECKS))
    if unknown:
        sys.exit(f"unknown check(s): {', '.join(unknown)}; choose from {', '.join(CHECKS)}")
    today = date.today()
    findings: list[Finding] = []
    for name in checks:
        try:
            findings += CHECKS[name](root, today)
        except Exception as exc:
            # A check that could not run is itself something to look at —
            # never a silent pass.
            findings.append(Finding("check-failed", name, f"{type(exc).__name__}: {exc}"))
    acks = load_acks(root / ack)
    report = triage(findings, acks, today, complete=set(checks) == set(CHECKS))
    text = render(report, today, ack_file=str(ack))
    print(text, end="")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(text)
    sys.exit(1 if report.action else 0)


if __name__ == "__main__":
    defopt.run(audit)
