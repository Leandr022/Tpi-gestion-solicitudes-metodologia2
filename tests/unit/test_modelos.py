import datetime

import pytest
from soporte import FECHA, datos

from solicitudes.errores import ErrorDeDominio
from solicitudes.modelos import (CriteriosBusqueda, Estado, Prioridad, RegistroAcademico, Responsable,
                                 Solicitud, Tipo)


# ----------------------------------------------------------------------
# Reglas de plazo (Replace Conditional with Table)
# ----------------------------------------------------------------------
@pytest.mark.parametrize("tipo, plazo", [
    (Tipo.CERTIFICADO, 5), (Tipo.EQUIVALENCIA, 15), (Tipo.REINCORPORACION, 10), (Tipo.CONSULTA, 3)])
def test_plazo_base_por_tipo(tipo, plazo):
    assert tipo.plazo_base_en_dias == plazo


@pytest.mark.parametrize("prioridad, plazo_base, esperado", [
    (Prioridad.ALTA, 5, 2), (Prioridad.ALTA, 15, 7), (Prioridad.ALTA, 3, 1),
    (Prioridad.MEDIA, 10, 10), (Prioridad.BAJA, 10, 15), (Prioridad.BAJA, 3, 8)])
def test_ajuste_de_plazo_por_prioridad(prioridad, plazo_base, esperado):
    assert prioridad.ajustar_plazo(plazo_base) == esperado


# ----------------------------------------------------------------------
# Máquina de estados: se verifican las 25 combinaciones origen/destino
# ----------------------------------------------------------------------
PERMITIDAS = {
    (Estado.PENDIENTE, Estado.EN_PROCESO), (Estado.PENDIENTE, Estado.RECHAZADA),
    (Estado.EN_PROCESO, Estado.RESUELTA), (Estado.EN_PROCESO, Estado.RECHAZADA),
    (Estado.RESUELTA, Estado.CERRADA),
}


@pytest.mark.parametrize("origen", list(Estado))
@pytest.mark.parametrize("destino", list(Estado))
def test_matriz_de_transiciones(origen, destino):
    assert origen.puede_pasar_a(destino) == ((origen, destino) in PERMITIDAS)


@pytest.mark.parametrize("estado, activo, asignable", [
    (Estado.PENDIENTE, True, True), (Estado.EN_PROCESO, True, True), (Estado.RESUELTA, False, False),
    (Estado.RECHAZADA, False, False), (Estado.CERRADA, False, False)])
def test_propiedades_de_estado(estado, activo, asignable):
    assert estado.esta_activo is activo
    assert estado.admite_asignacion is asignable


# ----------------------------------------------------------------------
# Solicitud
# ----------------------------------------------------------------------
def solicitud(**cambios):
    base = Solicitud.nueva(1, datos(descripcion="   Certificado de alumno regular  "), FECHA)
    for atributo, valor in cambios.items():
        setattr(base, atributo, valor)
    return base


def test_nueva_solicitud_nace_pendiente_sin_responsable_y_con_vencimiento():
    s = solicitud()
    assert (s.estado, s.responsable_id) == (Estado.PENDIENTE, None)
    assert s.vence == FECHA + datetime.timedelta(days=5)
    assert s.descripcion == "Certificado de alumno regular"
    assert isinstance(s.tipo, Tipo) and isinstance(s.prioridad, Prioridad)


def test_esta_vencida_solo_si_esta_activa_y_paso_la_fecha():
    s = solicitud()  # vence el 2026-11-07
    assert s.esta_vencida(datetime.date(2026, 11, 8)) is True
    assert s.esta_vencida(datetime.date(2026, 11, 7)) is False
    s.estado = Estado.CERRADA
    assert s.esta_vencida(datetime.date(2026, 12, 31)) is False


def test_pasar_a_con_transicion_valida_y_responsable():
    s = solicitud(responsable_id=1)
    s.pasar_a(Estado.EN_PROCESO)
    assert s.estado == Estado.EN_PROCESO


def test_pasar_a_rechaza_transicion_no_permitida():
    with pytest.raises(ErrorDeDominio, match="transición no permitida: PENDIENTE -> CERRADA"):
        solicitud().pasar_a(Estado.CERRADA)


def test_pasar_a_en_proceso_exige_responsable():
    s = solicitud()
    with pytest.raises(ErrorDeDominio, match="responsable asignado"):
        s.pasar_a(Estado.EN_PROCESO)
    assert s.estado == Estado.PENDIENTE


def test_asignar_a_responsable_con_capacidad():
    s = solicitud()
    s.asignar_a(Responsable(7, "Marta Ruiz", "Bedelía"), solicitudes_activas_del_responsable=2)
    assert s.responsable_id == 7


def test_asignar_a_rechaza_solicitud_finalizada():
    s = solicitud(estado=Estado.RESUELTA)
    with pytest.raises(ErrorDeDominio, match="no se puede asignar responsable a una solicitud RESUELTA"):
        s.asignar_a(Responsable(7, "Marta Ruiz", "Bedelía"), 0)


def test_asignar_a_rechaza_responsable_sin_capacidad():
    with pytest.raises(ErrorDeDominio, match="Marta Ruiz alcanzó el máximo de 3 solicitudes activas"):
        solicitud().asignar_a(Responsable(7, "Marta Ruiz", "Bedelía"), 3)


# ----------------------------------------------------------------------
# Responsable
# ----------------------------------------------------------------------
def test_responsable_nuevo_normaliza_espacios():
    r = Responsable.nuevo(1, "  Marta Ruiz ", " Bedelía  ")
    assert (r.nombre, r.area) == ("Marta Ruiz", "Bedelía")


@pytest.mark.parametrize("nombre, area", [("", "Bedelía"), ("  ", "Bedelía"), ("Marta", ""), ("Marta", " "),
                                          (None, "Bedelía"), ("Marta", None)])
def test_responsable_nuevo_exige_nombre_y_area(nombre, area):
    with pytest.raises(ErrorDeDominio, match="nombre y área son obligatorios"):
        Responsable.nuevo(1, nombre, area)


@pytest.mark.parametrize("activas, capacidad", [(0, True), (2, True), (3, False), (4, False)])
def test_capacidad_del_responsable(activas, capacidad):
    assert Responsable(1, "A", "B").tiene_capacidad(activas) is capacidad


# ----------------------------------------------------------------------
# Validación de los datos de registro (Move Method desde el gestor)
# ----------------------------------------------------------------------
def test_datos_validos_no_lanzan_error():
    datos().validar()


@pytest.mark.parametrize("cambios, mensaje", [
    ({"legajo": "abc"}, "legajo inválido"),
    ({"legajo": ""}, "legajo inválido"),
    ({"legajo": None}, "legajo inválido"),
    ({"nombre": "  "}, "nombre obligatorio"),
    ({"email": "sin-arroba"}, "email inválido"),
    ({"tipo": "OTRO"}, "tipo inválido: OTRO"),
    ({"prioridad": "URGENTE"}, "prioridad inválida: URGENTE"),
    ({"descripcion": "corta"}, "la descripción debe tener al menos 10 caracteres"),
    ({"descripcion": "x" * 201}, "la descripción no puede superar 200 caracteres"),
])
def test_validacion_de_datos_de_registro(cambios, mensaje):
    with pytest.raises(ErrorDeDominio) as error:
        datos(**cambios).validar()
    assert str(error.value) == mensaje


def test_la_validacion_informa_primero_la_regla_que_aparece_antes():
    with pytest.raises(ErrorDeDominio, match="legajo inválido"):
        datos(legajo="x", nombre="", tipo="OTRO").validar()


def test_descripcion_de_largo_limite_es_valida():
    datos(descripcion="x" * 10).validar()
    datos(descripcion="x" * 200).validar()


# ----------------------------------------------------------------------
# Criterios de búsqueda
# ----------------------------------------------------------------------
def test_criterios_vacios_coinciden_con_todo():
    assert CriteriosBusqueda().coincide_con(solicitud()) is True


@pytest.mark.parametrize("criterios, coincide", [
    (CriteriosBusqueda(tipo="CERTIFICADO"), True), (CriteriosBusqueda(tipo="CONSULTA"), False),
    (CriteriosBusqueda(estado="PENDIENTE", prioridad="MEDIA"), True),
    (CriteriosBusqueda(estado="PENDIENTE", prioridad="ALTA"), False),
    (CriteriosBusqueda(legajo="1001"), True), (CriteriosBusqueda(legajo="9999"), False)])
def test_criterios_combinados_con_y_logico(criterios, coincide):
    assert criterios.coincide_con(solicitud()) is coincide


# ----------------------------------------------------------------------
# Registro académico (agregado)
# ----------------------------------------------------------------------
def test_ids_secuenciales_y_estudiante_reutilizado():
    registro = RegistroAcademico()
    for _ in range(2):
        registro.obtener_o_crear_estudiante(datos())
        registro.agregar_solicitud(datos(), FECHA)
    assert [s.id for s in registro.solicitudes] == [1, 2]
    assert len(registro.estudiantes) == 1


def test_estudiante_existente_conserva_sus_datos():
    registro = RegistroAcademico()
    registro.obtener_o_crear_estudiante(datos())
    reutilizado = registro.obtener_o_crear_estudiante(datos(nombre="Otro", email="otro@example.com"))
    assert (reutilizado.nombre, reutilizado.email) == ("Ana Gómez", "ana@example.com")


def test_ids_de_responsables_son_secuenciales():
    registro = RegistroAcademico()
    ids = [registro.agregar_responsable(n, "Bedelía").id for n in ("A", "B", "C")]
    assert ids == [1, 2, 3]


def test_conteo_de_solicitudes_activas_excluye_finalizadas_y_la_indicada():
    registro = RegistroAcademico()
    for _ in range(4):
        registro.agregar_solicitud(datos(), FECHA)
    for s in registro.solicitudes:
        s.responsable_id = 1
    registro.solicitudes[0].estado = Estado.CERRADA
    assert registro.contar_solicitudes_activas(1, id_solicitud_excluida=2) == 2
    assert registro.contar_solicitudes_activas(99, id_solicitud_excluida=0) == 0


def test_busquedas_por_id_devuelven_none_si_no_existen():
    registro = RegistroAcademico()
    assert registro.buscar_solicitud(1) is None
    assert registro.buscar_responsable(1) is None
    assert registro.buscar_estudiante("1") is None


def test_reporte_cuenta_todos_los_estados_y_tipos_incluso_en_cero():
    registro = RegistroAcademico()
    registro.agregar_solicitud(datos(tipo="CONSULTA"), FECHA)
    registro.agregar_solicitud(datos(), FECHA)
    registro.solicitudes[1].estado = Estado.RECHAZADA
    reporte = registro.generar_reporte(datetime.date(2026, 11, 20))
    assert reporte.total == 2
    assert list(reporte.por_estado) == list(Estado)
    assert reporte.por_estado[Estado.PENDIENTE] == 1 and reporte.por_estado[Estado.CERRADA] == 0
    assert reporte.por_tipo[Tipo.CONSULTA] == 1 and reporte.por_tipo[Tipo.EQUIVALENCIA] == 0
    assert reporte.vencidas == 1  # la rechazada no cuenta como vencida
