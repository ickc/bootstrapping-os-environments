from __future__ import annotations

import defopt

from .util import setup_logging

__version__: str = "0.1.0"

logger = setup_logging()


def main():
    pass


def cli():
    defopt.run(main)


if __name__ == "__main__":
    cli()
