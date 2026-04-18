#!/usr/bin/env python
"""Utilitaire en ligne de commande Django."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def main():
    """Exécute les tâches d'administration."""
    load_dotenv(Path(__file__).resolve().parent / '.env')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Impossible d'importer Django. L'environnement virtuel est-il "
            'activé et Django installé ?'
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
