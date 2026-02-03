#!/usr/bin/env python
"""Django'nun yönetim görevleri için komut satırı yardımcı programı."""
import os
import sys


def main():
    """Yönetim görevlerini çalıştır."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studytracker.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django import edilemedi. Django'nun kurulu olduğundan ve "
            "PYTHONPATH ortam değişkeninde mevcut olduğundan emin misiniz? "
            "Sanal ortamı etkinleştirmeyi unuttunuz mu?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
