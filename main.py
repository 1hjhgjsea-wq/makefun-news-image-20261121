#!/usr/bin/env python3
"""Entrypoint for the news-image-20261121 bounty entry.

Copies the pre-rendered ``entry.png`` sitting next to this file into the
output directory, so the harness always gets exactly the bytes that were
drawn by ``draw_infographic.py``. Standard library only, no network, and
the copy is byte-for-byte identical every run.

Usage:
    MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
    python3 main.py                          # writes /output/entry.png
"""

from __future__ import annotations

import os
import shutil
import sys

SOURCE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"
OUTPUT_ENV_VAR = "MAKEFUN_OUTPUT_DIR"


def resolve_paths() -> tuple[str, str]:
    """Return (source image, destination image) as absolute paths."""
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, SOURCE_NAME)
    out_dir = os.environ.get(OUTPUT_ENV_VAR, DEFAULT_OUTPUT_DIR)
    destination = os.path.join(out_dir, SOURCE_NAME)
    return source, destination


def main() -> int:
    source, destination = resolve_paths()
    if not os.path.isfile(source):
        print(f"error: {source} is missing; run draw_infographic.py first",
              file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    shutil.copyfile(source, destination)
    print(f"Copied {source} -> {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
