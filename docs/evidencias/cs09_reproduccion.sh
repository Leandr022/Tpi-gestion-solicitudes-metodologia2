#!/usr/bin/env bash
# Reproduce el code smell CS-09: un datos.json corrupto provoca pérdida silenciosa de información.
# Uso: bash docs/evidencias/cs09_reproduccion.sh   (desde la raíz del repositorio)
set -u
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"; cd "$TMP"
cuenta() { python3 -c "import json;d=json.load(open('datos.json'));print(len(d['solicitudes']), [s['id'] for s in d['solicitudes']])"; }

echo "1) Se registra una solicitud (Ana, legajo 1001)"
python3 "$RAIZ/main.py" registrar --legajo 1001 --nombre "Ana Gómez" --email ana@example.com \
  --tipo CERTIFICADO --prioridad ALTA --descripcion "Certificado de alumno regular" --fecha 2026-11-02 | head -1
echo "   solicitudes en el archivo (cantidad, ids): $(cuenta)"

echo "2) Se simula un truncamiento del archivo (corrupción)"
head -c 120 datos.json > corrupto.json && mv corrupto.json datos.json

echo "3) Se registra otra solicitud (Luis, legajo 1002)"
python3 "$RAIZ/main.py" registrar --legajo 1002 --nombre "Luis Pérez" --email luis@example.com \
  --tipo CONSULTA --prioridad BAJA --descripcion "Consulta sobre correlativas" --fecha 2026-11-02 | head -1
echo "   solicitudes en el archivo (cantidad, ids): $(cuenta)"
