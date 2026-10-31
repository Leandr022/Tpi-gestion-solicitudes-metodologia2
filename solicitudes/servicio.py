"""Servicio de aplicación: orquesta los casos de uso sin entrada/salida ni detalles de persistencia."""
import datetime
from dataclasses import dataclass
from typing import Optional

from .errores import ErrorDeDominio
from .modelos import Estado, Notificacion, Responsable, Solicitud

FORMATO_FECHA = "%Y-%m-%d"


@dataclass(frozen=True)
class ResultadoRegistro:
    solicitud: Solicitud
    notificacion: Notificacion


@dataclass(frozen=True)
class ResultadoCambioDeEstado:
    solicitud: Solicitud
    estado_anterior: Estado
    notificacion: Optional[Notificacion]


@dataclass(frozen=True)
class ResultadoAsignacion:
    solicitud: Solicitud
    responsable: Responsable


class ServicioSolicitudes:
    def __init__(self, repositorio, reloj=datetime.date.today):
        self._repositorio = repositorio
        self._reloj = reloj

    def registrar_solicitud(self, datos):
        datos.validar()
        fecha_alta = self._resolver_fecha(datos.fecha)
        registro = self._repositorio.cargar()
        estudiante = registro.obtener_o_crear_estudiante(datos)
        solicitud = registro.agregar_solicitud(datos, fecha_alta)
        self._repositorio.guardar(registro)
        notificacion = Notificacion(estudiante.email, f"su solicitud #{solicitud.id} fue registrada")
        return ResultadoRegistro(solicitud, notificacion)

    def alta_responsable(self, nombre, area):
        registro = self._repositorio.cargar()
        responsable = registro.agregar_responsable(nombre, area)
        self._repositorio.guardar(registro)
        return responsable

    def asignar_responsable(self, id_solicitud, id_responsable):
        registro = self._repositorio.cargar()
        solicitud = self._obtener_solicitud(registro, id_solicitud)
        responsable = registro.buscar_responsable(id_responsable)
        if responsable is None:
            raise ErrorDeDominio(f"responsable {id_responsable} no encontrado")
        activas = registro.contar_solicitudes_activas(id_responsable, id_solicitud)
        solicitud.asignar_a(responsable, activas)
        self._repositorio.guardar(registro)
        return ResultadoAsignacion(solicitud, responsable)

    def cambiar_estado(self, id_solicitud, texto_estado):
        estado_nuevo = self._interpretar_estado(texto_estado)
        registro = self._repositorio.cargar()
        solicitud = self._obtener_solicitud(registro, id_solicitud)
        estado_anterior = solicitud.estado
        solicitud.pasar_a(estado_nuevo)
        self._repositorio.guardar(registro)
        estudiante = registro.buscar_estudiante(solicitud.legajo)
        notificacion = None
        if estudiante is not None:
            notificacion = Notificacion(estudiante.email,
                                        f"su solicitud #{id_solicitud} cambió a {estado_nuevo}")
        return ResultadoCambioDeEstado(solicitud, estado_anterior, notificacion)

    def buscar(self, criterios):
        return self._repositorio.cargar().filtrar(criterios)

    def generar_reporte(self, texto_fecha_corte=None):
        fecha_corte = self._resolver_fecha(texto_fecha_corte)
        return self._repositorio.cargar().generar_reporte(fecha_corte)

    # ------------------------------------------------------------------
    def _resolver_fecha(self, texto):
        """Devuelve la fecha indicada o la actual si no se indicó; lanza ErrorDeDominio si es inválida."""
        if texto is None:
            return self._reloj()
        try:
            return datetime.datetime.strptime(texto, FORMATO_FECHA).date()
        except ValueError as causa:
            raise ErrorDeDominio("fecha inválida (use AAAA-MM-DD)") from causa

    @staticmethod
    def _interpretar_estado(texto):
        try:
            return Estado(texto)
        except ValueError as causa:
            raise ErrorDeDominio(f"estado inválido: {texto}") from causa

    @staticmethod
    def _obtener_solicitud(registro, id_solicitud):
        solicitud = registro.buscar_solicitud(id_solicitud)
        if solicitud is None:
            raise ErrorDeDominio(f"solicitud {id_solicitud} no encontrada")
        return solicitud
