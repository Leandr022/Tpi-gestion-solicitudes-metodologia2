"""Pruebas de caracterización (caja negra) del comportamiento externo.

Ejecutan la aplicación como lo haría un usuario (línea de comandos) y verifican
salida estándar, código de salida y contenido del archivo de datos. No dependen
de la estructura interna, por lo que se ejecutan SIN modificaciones tanto sobre
`estado-inicial` como sobre `estado-refactorizado`.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MAIN = RAIZ / "main.py"
GOLDEN = Path(__file__).parent / "golden" / "escenario_completo.txt"


def ejecutar(cwd, *args):
    entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
    r = subprocess.run(
        [sys.executable, str(MAIN), *map(str, args)],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8", env=entorno,
    )
    return r.returncode, r.stdout.splitlines()


def leer_datos(cwd):
    return json.loads((Path(cwd) / "datos.json").read_text(encoding="utf-8"))


def registrar(cwd, legajo="1001", nombre="Ana Gómez", email="ana@example.com",
              tipo="CERTIFICADO", prioridad="MEDIA",
              descripcion="Certificado de alumno regular", fecha="2026-11-02"):
    return ejecutar(cwd, "registrar", "--legajo", legajo, "--nombre", nombre,
                    "--email", email, "--tipo", tipo, "--prioridad", prioridad,
                    "--descripcion", descripcion, "--fecha", fecha)


def alta_responsable(cwd, nombre="Marta Ruiz", area="Secretaría Académica"):
    return ejecutar(cwd, "alta-responsable", "--nombre", nombre, "--area", area)


def asignar(cwd, id_solicitud, id_responsable):
    return ejecutar(cwd, "asignar", "--id", id_solicitud, "--responsable-id", id_responsable)


def cambiar_estado(cwd, id_solicitud, estado):
    return ejecutar(cwd, "cambiar-estado", "--id", id_solicitud, "--estado", estado)


# --------------------------------------------------------------------------
# Registrar solicitud
# --------------------------------------------------------------------------
def test_registrar_solicitud_valida(tmp_path):
    codigo, salida = registrar(tmp_path)
    assert codigo == 0
    assert salida == [
        "Solicitud #1 registrada (tipo=CERTIFICADO, prioridad=MEDIA, vence=2026-11-07)",
        "[NOTIFICACIÓN] Email a ana@example.com: su solicitud #1 fue registrada",
    ]
    datos = leer_datos(tmp_path)
    assert datos["ultimo_id"] == 1
    assert datos["estudiantes"] == [
        {"legajo": "1001", "nombre": "Ana Gómez", "email": "ana@example.com"}]
    assert datos["solicitudes"] == [{
        "id": 1, "legajo": "1001", "tipo": "CERTIFICADO", "prioridad": "MEDIA",
        "estado": "PENDIENTE", "descripcion": "Certificado de alumno regular",
        "fecha": "2026-11-02", "vence": "2026-11-07", "responsable_id": None}]


@pytest.mark.parametrize("tipo, prioridad, vence", [
    ("CERTIFICADO", "ALTA", "2026-11-04"), ("CERTIFICADO", "MEDIA", "2026-11-07"),
    ("CERTIFICADO", "BAJA", "2026-11-12"),
    ("EQUIVALENCIA", "ALTA", "2026-11-09"), ("EQUIVALENCIA", "MEDIA", "2026-11-17"),
    ("EQUIVALENCIA", "BAJA", "2026-11-22"),
    ("REINCORPORACION", "ALTA", "2026-11-07"), ("REINCORPORACION", "MEDIA", "2026-11-12"),
    ("REINCORPORACION", "BAJA", "2026-11-17"),
    ("CONSULTA", "ALTA", "2026-11-03"), ("CONSULTA", "MEDIA", "2026-11-05"),
    ("CONSULTA", "BAJA", "2026-11-10"),
])
def test_plazo_de_vencimiento_segun_tipo_y_prioridad(tmp_path, tipo, prioridad, vence):
    codigo, _ = registrar(tmp_path, tipo=tipo, prioridad=prioridad)
    assert codigo == 0
    assert leer_datos(tmp_path)["solicitudes"][0]["vence"] == vence


@pytest.mark.parametrize("argumentos, mensaje", [
    ({"legajo": "abc"}, "ERROR: legajo inválido"),
    ({"legajo": ""}, "ERROR: legajo inválido"),
    ({"nombre": "   "}, "ERROR: nombre obligatorio"),
    ({"email": "no-es-un-email"}, "ERROR: email inválido"),
    ({"tipo": "OTRO"}, "ERROR: tipo inválido: OTRO"),
    ({"prioridad": "URGENTE"}, "ERROR: prioridad inválida: URGENTE"),
    ({"descripcion": "corta"}, "ERROR: la descripción debe tener al menos 10 caracteres"),
    ({"descripcion": "x" * 201}, "ERROR: la descripción no puede superar 200 caracteres"),
    ({"fecha": "02/11/2026"}, "ERROR: fecha inválida (use AAAA-MM-DD)"),
])
def test_registrar_rechaza_datos_invalidos(tmp_path, argumentos, mensaje):
    codigo, salida = registrar(tmp_path, **argumentos)
    assert codigo == 1
    assert salida == [mensaje]
    assert not (tmp_path / "datos.json").exists()


def test_ids_secuenciales_y_estudiante_reutilizado(tmp_path):
    registrar(tmp_path)
    registrar(tmp_path, tipo="CONSULTA", descripcion="Consulta sobre correlativas")
    registrar(tmp_path, legajo="1002", nombre="Luis Pérez", email="luis@example.com")
    datos = leer_datos(tmp_path)
    assert [s["id"] for s in datos["solicitudes"]] == [1, 2, 3]
    assert [e["legajo"] for e in datos["estudiantes"]] == ["1001", "1002"]


def test_estudiante_existente_conserva_sus_datos_y_recibe_la_notificacion(tmp_path):
    registrar(tmp_path)
    _, salida = registrar(tmp_path, nombre="Otro Nombre", email="otro@example.com")
    assert salida[1] == "[NOTIFICACIÓN] Email a ana@example.com: su solicitud #2 fue registrada"
    assert leer_datos(tmp_path)["estudiantes"][0]["nombre"] == "Ana Gómez"


def test_descripcion_se_guarda_sin_espacios_laterales(tmp_path):
    registrar(tmp_path, descripcion="   Certificado de alumno regular   ")
    assert leer_datos(tmp_path)["solicitudes"][0]["descripcion"] == "Certificado de alumno regular"


# --------------------------------------------------------------------------
# Alta de responsables y asignación
# --------------------------------------------------------------------------
def test_alta_responsable(tmp_path):
    codigo, salida = alta_responsable(tmp_path)
    assert codigo == 0
    assert salida == ["Responsable #1 creado: Marta Ruiz (Secretaría Académica)"]
    assert leer_datos(tmp_path)["responsables"] == [
        {"id": 1, "nombre": "Marta Ruiz", "area": "Secretaría Académica"}]


def test_alta_responsable_requiere_nombre_y_area(tmp_path):
    codigo, salida = alta_responsable(tmp_path, nombre=" ", area="Bedelía")
    assert (codigo, salida) == (1, ["ERROR: nombre y área son obligatorios"])


def test_asignar_responsable(tmp_path):
    alta_responsable(tmp_path)
    registrar(tmp_path)
    codigo, salida = asignar(tmp_path, 1, 1)
    assert codigo == 0
    assert salida == ["Solicitud #1 asignada a Marta Ruiz (Secretaría Académica)"]
    assert leer_datos(tmp_path)["solicitudes"][0]["responsable_id"] == 1


def test_asignar_con_solicitud_inexistente(tmp_path):
    alta_responsable(tmp_path)
    assert asignar(tmp_path, 9, 1) == (1, ["ERROR: solicitud 9 no encontrada"])


def test_asignar_con_responsable_inexistente(tmp_path):
    registrar(tmp_path)
    assert asignar(tmp_path, 1, 7) == (1, ["ERROR: responsable 7 no encontrado"])


def test_no_se_asigna_responsable_a_solicitud_finalizada(tmp_path):
    alta_responsable(tmp_path)
    registrar(tmp_path)
    cambiar_estado(tmp_path, 1, "RECHAZADA")
    assert asignar(tmp_path, 1, 1) == (
        1, ["ERROR: no se puede asignar responsable a una solicitud RECHAZADA"])


def test_responsable_tiene_maximo_de_tres_solicitudes_activas(tmp_path):
    alta_responsable(tmp_path)
    for _ in range(4):
        registrar(tmp_path)
    for numero in (1, 2, 3):
        assert asignar(tmp_path, numero, 1)[0] == 0
    assert asignar(tmp_path, 4, 1) == (
        1, ["ERROR: el responsable Marta Ruiz alcanzó el máximo de 3 solicitudes activas"])
    # Reasignar una solicitud ya asignada no cuenta contra el límite
    assert asignar(tmp_path, 3, 1)[0] == 0


# --------------------------------------------------------------------------
# Cambio de estado
# --------------------------------------------------------------------------
def test_flujo_completo_de_estados_con_notificaciones(tmp_path):
    alta_responsable(tmp_path)
    registrar(tmp_path)
    asignar(tmp_path, 1, 1)
    esperado = [
        ("EN_PROCESO", "PENDIENTE -> EN_PROCESO"),
        ("RESUELTA", "EN_PROCESO -> RESUELTA"),
        ("CERRADA", "RESUELTA -> CERRADA"),
    ]
    for estado, transicion in esperado:
        codigo, salida = cambiar_estado(tmp_path, 1, estado)
        assert codigo == 0
        assert salida == [
            f"Solicitud #1: {transicion}",
            f"[NOTIFICACIÓN] Email a ana@example.com: su solicitud #1 cambió a {estado}",
        ]
    assert leer_datos(tmp_path)["solicitudes"][0]["estado"] == "CERRADA"


@pytest.mark.parametrize("origen, destino", [
    ("PENDIENTE", "RESUELTA"), ("PENDIENTE", "CERRADA"), ("PENDIENTE", "PENDIENTE"),
])
def test_transiciones_no_permitidas_desde_pendiente(tmp_path, origen, destino):
    registrar(tmp_path)
    codigo, salida = cambiar_estado(tmp_path, 1, destino)
    assert (codigo, salida) == (
        1, [f"ERROR: transición no permitida: {origen} -> {destino}"])
    assert leer_datos(tmp_path)["solicitudes"][0]["estado"] == "PENDIENTE"


def test_en_proceso_requiere_responsable_asignado(tmp_path):
    registrar(tmp_path)
    assert cambiar_estado(tmp_path, 1, "EN_PROCESO") == (
        1, ["ERROR: la solicitud debe tener un responsable asignado para pasar a EN_PROCESO"])


def test_rechazar_no_requiere_responsable(tmp_path):
    registrar(tmp_path)
    codigo, _ = cambiar_estado(tmp_path, 1, "RECHAZADA")
    assert codigo == 0


def test_estado_invalido_y_solicitud_inexistente(tmp_path):
    registrar(tmp_path)
    assert cambiar_estado(tmp_path, 1, "ANULADA") == (1, ["ERROR: estado inválido: ANULADA"])
    assert cambiar_estado(tmp_path, 5, "RECHAZADA") == (1, ["ERROR: solicitud 5 no encontrada"])


# --------------------------------------------------------------------------
# Búsqueda y reporte
# --------------------------------------------------------------------------
@pytest.fixture
def escenario(tmp_path):
    alta_responsable(tmp_path)
    registrar(tmp_path, legajo="1001", tipo="CERTIFICADO", prioridad="ALTA")
    registrar(tmp_path, legajo="1002", nombre="Luis Pérez", email="luis@example.com",
              tipo="EQUIVALENCIA", prioridad="MEDIA", descripcion="Equivalencia de Matemática")
    registrar(tmp_path, legajo="1001", tipo="CONSULTA", prioridad="BAJA",
              descripcion="Consulta sobre correlativas")
    asignar(tmp_path, 1, 1)
    cambiar_estado(tmp_path, 1, "EN_PROCESO")
    cambiar_estado(tmp_path, 3, "RECHAZADA")
    return tmp_path


def test_buscar_sin_filtros_lista_todo_ordenado_por_id(escenario):
    codigo, salida = ejecutar(escenario, "buscar")
    assert codigo == 0
    assert salida == [
        "#1 | CERTIFICADO | ALTA | EN_PROCESO | legajo 1001 | vence 2026-11-04",
        "#2 | EQUIVALENCIA | MEDIA | PENDIENTE | legajo 1002 | vence 2026-11-17",
        "#3 | CONSULTA | BAJA | RECHAZADA | legajo 1001 | vence 2026-11-10",
    ]


@pytest.mark.parametrize("filtros, ids", [
    (["--tipo", "EQUIVALENCIA"], ["#2"]),
    (["--estado", "RECHAZADA"], ["#3"]),
    (["--prioridad", "ALTA"], ["#1"]),
    (["--legajo", "1001"], ["#1", "#3"]),
    (["--legajo", "1001", "--estado", "EN_PROCESO"], ["#1"]),
])
def test_buscar_con_filtros(escenario, filtros, ids):
    _, salida = ejecutar(escenario, "buscar", *filtros)
    assert [linea.split(" | ")[0] for linea in salida] == ids


def test_buscar_sin_resultados(escenario):
    assert ejecutar(escenario, "buscar", "--tipo", "INEXISTENTE") == (0, ["Sin resultados."])


def test_reporte(escenario):
    codigo, salida = ejecutar(escenario, "reporte", "--hoy", "2026-11-10")
    assert codigo == 0
    assert salida == [
        "=== REPORTE DE SOLICITUDES ===",
        "Total: 3",
        "Por estado:",
        "  PENDIENTE: 1",
        "  EN_PROCESO: 1",
        "  RESUELTA: 0",
        "  RECHAZADA: 1",
        "  CERRADA: 0",
        "Por tipo:",
        "  CERTIFICADO: 1",
        "  EQUIVALENCIA: 1",
        "  REINCORPORACION: 0",
        "  CONSULTA: 1",
        "Vencidas al 2026-11-10: 1",
    ]


def test_reporte_con_fecha_invalida(escenario):
    assert ejecutar(escenario, "reporte", "--hoy", "mañana") == (
        1, ["ERROR: fecha inválida (use AAAA-MM-DD)"])


def test_reporte_sin_datos_previos(tmp_path):
    codigo, salida = ejecutar(tmp_path, "reporte", "--hoy", "2026-11-10")
    assert codigo == 0
    assert salida[1] == "Total: 0"
    assert salida[-1] == "Vencidas al 2026-11-10: 0"


# --------------------------------------------------------------------------
# Escenario completo contra un resultado de referencia (golden master)
# --------------------------------------------------------------------------
def test_escenario_completo_coincide_con_resultado_de_referencia(tmp_path):
    comandos = [
        ["alta-responsable", "--nombre", "Marta Ruiz", "--area", "Secretaría Académica"],
        ["alta-responsable", "--nombre", "Jorge Díaz", "--area", "Bedelía"],
        ["registrar", "--legajo", "1001", "--nombre", "Ana Gómez", "--email", "ana@example.com",
         "--tipo", "CERTIFICADO", "--prioridad", "ALTA",
         "--descripcion", "Certificado de alumno regular", "--fecha", "2026-11-02"],
        ["registrar", "--legajo", "1002", "--nombre", "Luis Pérez", "--email", "luis@example.com",
         "--tipo", "EQUIVALENCIA", "--prioridad", "MEDIA",
         "--descripcion", "Equivalencia de Matemática I", "--fecha", "2026-11-03"],
        ["registrar", "--legajo", "1003", "--nombre", "Eva Soto", "--email", "eva@example.com",
         "--tipo", "REINCORPORACION", "--prioridad", "BAJA",
         "--descripcion", "Reincorporación a la carrera", "--fecha", "2026-11-04"],
        ["registrar", "--legajo", "1001", "--nombre", "Ana Gómez", "--email", "ana@example.com",
         "--tipo", "CONSULTA", "--prioridad", "ALTA",
         "--descripcion", "Consulta sobre correlativas", "--fecha", "2026-11-05"],
        ["asignar", "--id", "1", "--responsable-id", "1"],
        ["asignar", "--id", "2", "--responsable-id", "2"],
        ["asignar", "--id", "9", "--responsable-id", "1"],
        ["cambiar-estado", "--id", "1", "--estado", "EN_PROCESO"],
        ["cambiar-estado", "--id", "3", "--estado", "EN_PROCESO"],
        ["cambiar-estado", "--id", "1", "--estado", "RESUELTA"],
        ["cambiar-estado", "--id", "4", "--estado", "RECHAZADA"],
        ["buscar", "--legajo", "1001"],
        ["buscar", "--estado", "PENDIENTE", "--prioridad", "BAJA"],
        ["reporte", "--hoy", "2026-11-12"],
    ]
    bloques = []
    for comando in comandos:
        codigo, salida = ejecutar(tmp_path, *comando)
        bloques.append("\n".join([f"$ {' '.join(comando)}", *salida, f"[codigo={codigo}]"]))
    bloques.append("--- datos.json ---\n" + (tmp_path / "datos.json").read_text(encoding="utf-8"))
    resultado = "\n".join(bloques) + "\n"

    if os.environ.get("ACTUALIZAR_REFERENCIA") == "1":
        GOLDEN.write_text(resultado, encoding="utf-8")
    assert resultado == GOLDEN.read_text(encoding="utf-8")
