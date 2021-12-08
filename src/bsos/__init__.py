from __future__ import annotations

import defopt

from .util import setup_logging

logger = setup_logging()


def main():
    pass


def cli():
    defopt.run(main)


if __name__ == "__main__":
    cli()
