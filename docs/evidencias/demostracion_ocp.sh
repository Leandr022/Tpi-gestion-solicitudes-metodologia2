#!/usr/bin/env bash
# Demostración del principio Abierto/Cerrado (OCP): agregar un tipo de solicitud nuevo (BECA)
# modificando SOLO 2 líneas, en una COPIA temporal del proyecto (el repositorio no se altera).
# Uso:  bash docs/evidencias/demostracion_ocp.sh
set -u
RAIZ="$(cd "$(dirname "$0")/../.." && pwd)"
COPIA="$(mktemp -d)/proyecto"; cp -r "$RAIZ" "$COPIA"; rm -rf "$COPIA/.git"

sed -i 's/^    CONSULTA = "CONSULTA"$/    CONSULTA = "CONSULTA"\n    BECA = "BECA"/' "$COPIA/solicitudes/modelos.py"
sed -i 's/^    Tipo.CONSULTA: 3,$/    Tipo.CONSULTA: 3,\n    Tipo.BECA: 8,/' "$COPIA/solicitudes/modelos.py"

echo "# Cambio realizado (líneas agregadas respecto del código original):"
diff "$RAIZ/solicitudes/modelos.py" "$COPIA/solicitudes/modelos.py" | grep '^>'

DATOS="$(mktemp -d)"; cd "$DATOS"
echo; echo '$ registrar --tipo BECA --prioridad MEDIA --fecha 2026-11-02'
python3 "$COPIA/main.py" registrar --legajo 1001 --nombre "Ana Gómez" --email ana@example.com \
  --tipo BECA --prioridad MEDIA --descripcion "Solicitud de beca de apuntes" --fecha 2026-11-02
echo; echo '$ registrar --tipo BECA --prioridad ALTA --fecha 2026-11-02'
python3 "$COPIA/main.py" registrar --legajo 1002 --nombre "Luis Pérez" --email luis@example.com \
  --tipo BECA --prioridad ALTA --descripcion "Solicitud de beca de transporte" --fecha 2026-11-02
echo; echo '$ reporte --hoy 2026-11-20   (se muestran las líneas de tipos)'
python3 "$COPIA/main.py" reporte --hoy 2026-11-20 | sed -n '1,2p;10,16p'
echo; echo '$ registrar --tipo INEXISTENTE   (la validación sigue funcionando)'
python3 "$COPIA/main.py" registrar --legajo 1003 --nombre "Eva Soto" --email eva@example.com \
  --tipo INEXISTENTE --prioridad ALTA --descripcion "Tipo que no existe" --fecha 2026-11-02

echo; echo "# Suite completa sobre la copia modificada."
echo "# Resultado esperado: solo fallan las 2 pruebas que fijan el TEXTO LITERAL del reporte, porque el"
echo "# reporte ahora incluye legítimamente la línea 'BECA: 0'. No hay regresiones en la lógica de negocio."
cd "$COPIA" && python3 -m pytest -q -p no:cacheprovider -rf 2>&1 | grep -E "^FAILED|passed|failed" | cut -c1-120
