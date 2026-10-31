#!/usr/bin/env bash
# Reproduce el code smell CS-09: ¿qué ocurre si datos.json está corrupto y se registra otra solicitud?
# Uso:  bash docs/evidencias/cs09_reproduccion.sh [RAIZ_DEL_PROYECTO]
# Sin argumento usa la copia actual del repositorio; para probar otra versión, pasar la ruta de un
# checkout de esa versión (por ejemplo, un `git worktree` del tag estado-inicial).
set -u
RAIZ="${1:-$(cd "$(dirname "$0")/../.." && pwd)}"
TMP="$(mktemp -d)"; cd "$TMP"

resumen() {
  python3 - <<'PY'
import json
try:
    d = json.load(open("datos.json", encoding="utf-8"))
    print("   archivo legible -> solicitudes (cantidad, ids):", len(d["solicitudes"]), [s["id"] for s in d["solicitudes"]])
except ValueError:
    print("   archivo ilegible (corrupto)")
PY
}

echo "1) Se registra una solicitud (Ana, legajo 1001)"
python3 "$RAIZ/main.py" registrar --legajo 1001 --nombre "Ana Gómez" --email ana@example.com \
  --tipo CERTIFICADO --prioridad ALTA --descripcion "Certificado de alumno regular" --fecha 2026-11-02 | head -1
resumen

echo "2) Se simula un truncamiento del archivo (corrupción)"
head -c 120 datos.json > corrupto.json && mv corrupto.json datos.json
ANTES="$(sha256sum datos.json | cut -d' ' -f1)"
resumen

echo "3) Se intenta registrar otra solicitud (Luis, legajo 1002)"
python3 "$RAIZ/main.py" registrar --legajo 1002 --nombre "Luis Pérez" --email luis@example.com \
  --tipo CONSULTA --prioridad BAJA --descripcion "Consulta sobre correlativas" --fecha 2026-11-02 | head -1
resumen
if [ "$(sha256sum datos.json | cut -d' ' -f1)" = "$ANTES" ]; then
  echo "   contenido original del archivo conservado: SI"
else
  echo "   contenido original del archivo conservado: NO (fue sobrescrito: se perdieron los datos previos)"
fi
