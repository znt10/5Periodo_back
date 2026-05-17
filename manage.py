#!/usr/bin/env python
import os
from pathlib import Path
import sys


def main():
    sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))
    os.environ["DJANGO_SETTINGS_MODULE"] = "backend.settings"
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
