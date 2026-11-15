"""Dependency audit: abandoned upstreams and rotting pins, across package managers.

"Not updated in a year" is a poor test for abandonment — ``bzip2`` and
``make`` are old and fine. The checks here use signals that do not need a
time threshold to mean something:

* explicit declarations someone else curates — a repository archived on
  GitHub, a cask Homebrew deprecated, an app delisted from the App Store;
* failure to keep up with the ecosystem — no build for a Python that has been
  out for a year, a pin that holds a dependency back, a compiled build years
  older than the libraries it links against.

Findings come in two kinds. *Action* findings need a decision (fix it, or
acknowledge it in ``audit-ack.toml``) and make the audit exit non-zero;
*informational* ones are context. So a green audit means nothing new.

Run it with ``pixi run audit``; CI runs it weekly (``.github/workflows/audit.yml``).
"""
