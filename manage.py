#!/usr/bin/env python
"""Tiện ích dòng lệnh của Django."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Không import được Django. Bạn đã cài đặt và kích hoạt môi trường ảo chưa?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
