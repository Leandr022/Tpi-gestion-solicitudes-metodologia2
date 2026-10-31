import datetime

import pytest
from soporte import NotificadorEnMemoria

from solicitudes.cli import main
from solicitudes.modelos import Estado, Notificacion, Reporte, Tipo
from solicitudes.notificador import NotificadorConsola
from solicitudes.presentacion import formatear_notificacion, formatear_reporte


def ejecutar(tmp_path, capsys, *argumentos, notificador=None):
    codigo = main(list(argumentos), ruta_datos=tmp_path / "datos.json",
                  notificador=notificador if notificador is not None else NotificadorEnMemoria())
    return codigo, capsys.readouterr().out.splitlines()


def registrar(tmp_path, capsys, notificador=None, **cambios):
    campos = dict(legajo="1001", nombre="Ana Gómez", email="ana@example.com", tipo="CERTIFICADO",
                  prioridad="MEDIA", descripcion="Certificado de alumno regular", fecha="2026-11-02")
    campos.update(cambios)
    argumentos = ["registrar"] + [valor for clave, v in campos.items() for valor in (f"--{clave}", v)]
    return ejecutar(tmp_path, capsys, *argumentos, notificador=notificador)


def test_el_notificador_es_intercambiable_sin_tocar_el_resto(tmp_path, capsys):
    notificador = NotificadorEnMemoria()
    codigo, salida = registrar(tmp_path, capsys, notificador=notificador)
    assert codigo == 0
    assert salida == ["Solicitud #1 registrada (tipo=CERTIFICADO, prioridad=MEDIA, vence=2026-11-07)"]
    assert notificador.enviadas == [Notificacion("ana@example.com", "su solicitud #1 fue registrada")]


def test_notificador_de_consola_imprime_la_notificacion(capsys):
    NotificadorConsola().notificar(Notificacion("ana@example.com", "hola"))
    assert capsys.readouterr().out == "[NOTIFICACIÓN] Email a ana@example.com: hola\n"


def test_error_de_dominio_devuelve_codigo_1_con_prefijo_error(tmp_path, capsys):
    codigo, salida = registrar(tmp_path, capsys, legajo="abc")
    assert (codigo, salida) == (1, ["ERROR: legajo inválido"])


def test_error_por_archivo_corrupto_se_informa_sin_perder_datos(tmp_path, capsys):
    (tmp_path / "datos.json").write_text("{ roto", encoding="utf-8")
    codigo, salida = registrar(tmp_path, capsys)
    assert codigo == 1 and "corrupto" in salida[0]
    assert (tmp_path / "datos.json").read_text(encoding="utf-8") == "{ roto"


def test_comando_inexistente_o_ausente_termina_con_codigo_2_de_argparse(tmp_path):
    for argumentos in ([], ["inexistente"]):
        with pytest.raises(SystemExit) as salida:
            main(argumentos, ruta_datos=tmp_path / "datos.json")
        assert salida.value.code == 2


def test_flujo_completo_por_la_cli(tmp_path, capsys):
    notificador = NotificadorEnMemoria()
    registrar(tmp_path, capsys, notificador=notificador)
    assert ejecutar(tmp_path, capsys, "alta-responsable", "--nombre", "Marta Ruiz", "--area", "Bedelía")[1] == [
        "Responsable #1 creado: Marta Ruiz (Bedelía)"]
    assert ejecutar(tmp_path, capsys, "asignar", "--id", "1", "--responsable-id", "1")[1] == [
        "Solicitud #1 asignada a Marta Ruiz (Bedelía)"]
    assert ejecutar(tmp_path, capsys, "cambiar-estado", "--id", "1", "--estado", "EN_PROCESO",
                    notificador=notificador)[1] == ["Solicitud #1: PENDIENTE -> EN_PROCESO"]
    assert notificador.enviadas[-1].mensaje == "su solicitud #1 cambió a EN_PROCESO"
    assert ejecutar(tmp_path, capsys, "buscar", "--estado", "EN_PROCESO")[1] == [
        "#1 | CERTIFICADO | MEDIA | EN_PROCESO | legajo 1001 | vence 2026-11-07"]
    assert ejecutar(tmp_path, capsys, "buscar", "--estado", "CERRADA")[1] == ["Sin resultados."]
    salida = ejecutar(tmp_path, capsys, "reporte", "--hoy", "2026-11-08")[1]
    assert salida[0] == "=== REPORTE DE SOLICITUDES ===" and salida[-1] == "Vencidas al 2026-11-08: 1"


def test_formato_del_reporte():
    reporte = Reporte(0, {e: 0 for e in Estado}, {t: 0 for t in Tipo}, datetime.date(2026, 11, 2), 0)
    lineas = formatear_reporte(reporte)
    assert len(lineas) == 14
    assert lineas[3] == "  PENDIENTE: 0" and lineas[9] == "  CERTIFICADO: 0"


def test_formato_de_notificacion():
    assert formatear_notificacion(Notificacion("a@b.co", "texto")) == "[NOTIFICACIÓN] Email a a@b.co: texto"
