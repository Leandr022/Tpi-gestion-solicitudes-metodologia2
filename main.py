import sys

if sys.version_info < (3, 11):
    sys.exit("Este sistema requiere Python 3.11 o superior (usa enum.StrEnum).")

from solicitudes.cli import main  # noqa: E402  (la verificación de versión debe ir primero)

if __name__ == "__main__":
    sys.exit(main())
