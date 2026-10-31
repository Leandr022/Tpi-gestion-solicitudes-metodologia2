import datetime

import pytest
from soporte import FECHA, RepositorioEnMemoria, datos

from solicitudes.errores import ErrorDeDominio
from solicitudes.modelos import CriteriosBusqueda, Estado
from solicitudes.servicio import ServicioSolicitudes


@pytest.fixture
def repositorio():
    return RepositorioEnMemoria()


@pytest.fixture
def servicio(repositorio):
    return ServicioSolicitudes(repositorio, reloj=lambda: FECHA)


# ----------------------------------------------------------------------
# registrar_solicitud
# ----------------------------------------------------------------------
def test_registrar_devuelve_solicitud_y_notificacion_y_persiste_una_vez(servicio, repositorio):
    resultado = servicio.registrar_solicitud(datos())
    assert resultado.solicitud.id == 1
    assert resultado.solicitud.vence == datetime.date(2026, 11, 7)
    assert resultado.notificacion.email == "ana@example.com"
    assert resultado.notificacion.mensaje == "su solicitud #1 fue registrada"
    assert repositorio.cantidad_de_guardados == 1


def test_registrar_sin_fecha_usa_el_reloj_inyectado(servicio):
    resultado = servicio.registrar_solicitud(datos(fecha=None))
    assert resultado.solicitud.fecha == FECHA


def test_registrar_con_datos_invalidos_no_toca_el_repositorio(servicio, repositorio):
    with pytest.raises(ErrorDeDominio, match="legajo inválido"):
        servicio.registrar_solicitud(datos(legajo="x"))
    assert repositorio.cantidad_de_guardados == 0


def test_registrar_con_fecha_invalida(servicio, repositorio):
    with pytest.raises(ErrorDeDominio, match=r"fecha inválida \(use AAAA-MM-DD\)"):
        servicio.registrar_solicitud(datos(fecha="02/11/2026"))
    assert repositorio.cantidad_de_guardados == 0


def test_registrar_valida_los_datos_antes_que_la_fecha(servicio):
    with pytest.raises(ErrorDeDominio, match="tipo inválido: OTRO"):
        servicio.registrar_solicitud(datos(tipo="OTRO", fecha="no-es-fecha"))


# ----------------------------------------------------------------------
# alta_responsable / asignar_responsable
# ----------------------------------------------------------------------
def test_alta_de_responsable_persiste(servicio, repositorio):
    responsable = servicio.alta_responsable("Marta Ruiz", "Bedelía")
    assert responsable.id == 1
    assert repositorio.registro.responsables == [responsable]


def test_alta_de_responsable_invalida_no_persiste(servicio, repositorio):
    with pytest.raises(ErrorDeDominio):
        servicio.alta_responsable(" ", "Bedelía")
    assert repositorio.cantidad_de_guardados == 0


def test_asignar_responsable(servicio, repositorio):
    servicio.alta_responsable("Marta Ruiz", "Bedelía")
    servicio.registrar_solicitud(datos())
    resultado = servicio.asignar_responsable(1, 1)
    assert resultado.solicitud.responsable_id == 1
    assert resultado.responsable.nombre == "Marta Ruiz"


def test_asignar_informa_primero_la_solicitud_inexistente(servicio):
    with pytest.raises(ErrorDeDominio, match="solicitud 9 no encontrada"):
        servicio.asignar_responsable(9, 9)


def test_asignar_a_responsable_inexistente(servicio):
    servicio.registrar_solicitud(datos())
    with pytest.raises(ErrorDeDominio, match="responsable 5 no encontrado"):
        servicio.asignar_responsable(1, 5)


def test_responsable_no_supera_tres_solicitudes_activas(servicio):
    servicio.alta_responsable("Marta Ruiz", "Bedelía")
    for _ in range(4):
        servicio.registrar_solicitud(datos())
    for numero in (1, 2, 3):
        servicio.asignar_responsable(numero, 1)
    with pytest.raises(ErrorDeDominio, match="alcanzó el máximo de 3 solicitudes activas"):
        servicio.asignar_responsable(4, 1)
    servicio.asignar_responsable(3, 1)  # reasignar una ya asignada no cuenta contra el límite


# ----------------------------------------------------------------------
# cambiar_estado
# ----------------------------------------------------------------------
def preparar_solicitud_asignada(servicio):
    servicio.alta_responsable("Marta Ruiz", "Bedelía")
    servicio.registrar_solicitud(datos())
    servicio.asignar_responsable(1, 1)


def test_cambiar_estado_devuelve_estado_anterior_y_notificacion(servicio):
    preparar_solicitud_asignada(servicio)
    resultado = servicio.cambiar_estado(1, "EN_PROCESO")
    assert resultado.estado_anterior == Estado.PENDIENTE
    assert resultado.solicitud.estado == Estado.EN_PROCESO
    assert resultado.notificacion.mensaje == "su solicitud #1 cambió a EN_PROCESO"


def test_cambiar_estado_con_estado_invalido_se_informa_antes_que_la_solicitud_inexistente(servicio):
    with pytest.raises(ErrorDeDominio, match="estado inválido: ANULADA"):
        servicio.cambiar_estado(99, "ANULADA")


def test_cambiar_estado_de_solicitud_inexistente(servicio):
    with pytest.raises(ErrorDeDominio, match="solicitud 99 no encontrada"):
        servicio.cambiar_estado(99, "RECHAZADA")


def test_transicion_invalida_no_persiste_cambios(servicio, repositorio):
    servicio.registrar_solicitud(datos())
    guardados = repositorio.cantidad_de_guardados
    with pytest.raises(ErrorDeDominio, match="transición no permitida"):
        servicio.cambiar_estado(1, "CERRADA")
    assert repositorio.cantidad_de_guardados == guardados


def test_sin_estudiante_registrado_no_hay_notificacion(servicio, repositorio):
    servicio.registrar_solicitud(datos())
    repositorio.registro.estudiantes.clear()
    assert servicio.cambiar_estado(1, "RECHAZADA").notificacion is None


# ----------------------------------------------------------------------
# buscar / generar_reporte
# ----------------------------------------------------------------------
def test_buscar_aplica_los_criterios(servicio):
    servicio.registrar_solicitud(datos(tipo="CONSULTA", descripcion="Consulta sobre correlativas"))
    servicio.registrar_solicitud(datos())
    resultado = servicio.buscar(CriteriosBusqueda(tipo="CONSULTA"))
    assert [s.id for s in resultado] == [1]
    assert servicio.buscar(CriteriosBusqueda(tipo="INEXISTENTE")) == []


def test_reporte_sin_fecha_usa_el_reloj_inyectado(servicio):
    servicio.registrar_solicitud(datos())
    assert servicio.generar_reporte().fecha_corte == FECHA


def test_reporte_con_fecha_explicita_cuenta_vencidas(servicio):
    servicio.registrar_solicitud(datos())  # vence el 2026-11-07
    assert servicio.generar_reporte("2026-11-08").vencidas == 1
    assert servicio.generar_reporte("2026-11-07").vencidas == 0


def test_reporte_con_fecha_invalida(servicio):
    with pytest.raises(ErrorDeDominio, match="fecha inválida"):
        servicio.generar_reporte("mañana")
