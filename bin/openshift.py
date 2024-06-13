#!/venv/bin python
import os
import sys

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "signbank.settings.openshift")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)