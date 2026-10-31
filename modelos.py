"""Modelo de dominio: entidades con comportamiento, enumeraciones y objetos de parámetro."""
import datetime
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Optional

PATRON_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
LARGO_MINIMO_DESCRIPCION = 10
LARGO_MAXIMO_DESCRIPCION = 200
DIVISOR_PLAZO_PRIORIDAD_ALTA = 2
DIAS_ADICIONALES_PRIORIDAD_BAJA = 5


# ----------------------------------------------------------------------
# Enumeraciones (reemplazan cadenas "mágicas" y cadenas de if/elif)
# ----------------------------------------------------------------------
class Tipo(StrEnum):
    CERTIFICADO = "CERTIFICADO"
    EQUIVALENCIA = "EQUIVALENCIA"
    REINCORPORACION = "REINCORPORACION"
    CONSULTA = "CONSULTA"

    @property
    def plazo_base_en_dias(self):
        return _PLAZO_BASE_EN_DIAS[self]


class Prioridad(StrEnum):
    ALTA = "ALTA"
    MEDIA = "MEDIA"
    BAJA = "BAJA"

    def ajustar_plazo(self, plazo_base_en_dias):
        return _AJUSTES_DE_PLAZO[self](plazo_base_en_dias)


class Estado(StrEnum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    RESUELTA = "RESUELTA"
    RECHAZADA = "RECHAZADA"
    CERRADA = "CERRADA"

    @property
    def esta_activo(self):
        return self in (Estado.PENDIENTE, Estado.EN_PROCESO)

    @property
    def admite_asignacion(self):
        return self not in (Estado.RESUELTA, Estado.RECHAZADA, Estado.CERRADA)

    def puede_pasar_a(self, estado_nuevo):
        return estado_nuevo in _TRANSICIONES_PERMITIDAS[self]


# Tablas de reglas: para agregar un tipo, una prioridad o una transición se agrega
# una entrada; no hay que modificar ninguna cadena condicional (Open/Closed).
_PLAZO_BASE_EN_DIAS = {
    Tipo.CERTIFICADO: 5,
    Tipo.EQUIVALENCIA: 15,
    Tipo.REINCORPORACION: 10,
    Tipo.CONSULTA: 3,
}
_AJUSTES_DE_PLAZO = {
    Prioridad.ALTA: lambda plazo: plazo // DIVISOR_PLAZO_PRIORIDAD_ALTA,
    Prioridad.MEDIA: lambda plazo: plazo,
    Prioridad.BAJA: lambda plazo: plazo + DIAS_ADICIONALES_PRIORIDAD_BAJA,
}
_TRANSICIONES_PERMITIDAS = {
    Estado.PENDIENTE: (Estado.EN_PROCESO, Estado.RECHAZADA),
    Estado.EN_PROCESO: (Estado.RESUELTA, Estado.RECHAZADA),
    Estado.RESUELTA: (Estado.CERRADA,),
    Estado.RECHAZADA: (),
    Estado.CERRADA: (),
}


def _valores(enumeracion):
    return [miembro.value for miembro in enumeracion]


# ----------------------------------------------------------------------
# Objetos de parámetro
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class DatosSolicitud:
    """Parameter Object: datos necesarios para registrar una solicitud."""
    legajo: str
    nombre: str
    email: str
    tipo: str
    prioridad: str
    descripcion: str
    fecha: Optional[str] = None

    def primer_error(self):
        """Devuelve el mensaje de la primera regla incumplida, o None si los datos son válidos."""
        if self.legajo is None or self.legajo == "" or not self.legajo.isdigit():
            return "ERROR: legajo inválido"
        if self.nombre is None or self.nombre.strip() == "":
            return "ERROR: nombre obligatorio"
        if not re.match(PATRON_EMAIL, self.email):
            return "ERROR: email inválido"
        if self.tipo not in _valores(Tipo):
            return "ERROR: tipo inválido: " + self.tipo
        if self.prioridad not in _valores(Prioridad):
            return "ERROR: prioridad inválida: " + self.prioridad
        if self.descripcion is None or len(self.descripcion.strip()) < LARGO_MINIMO_DESCRIPCION:
            return "ERROR: la descripción debe tener al menos " + str(LARGO_MINIMO_DESCRIPCION) + " caracteres"
        if len(self.descripcion) > LARGO_MAXIMO_DESCRIPCION:
            return "ERROR: la descripción no puede superar " + str(LARGO_MAXIMO_DESCRIPCION) + " caracteres"
        return None


@dataclass(frozen=True)
class CriteriosBusqueda:
    """Parameter Object: filtros opcionales de una búsqueda."""
    tipo: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    legajo: Optional[str] = None


# ----------------------------------------------------------------------
# Entidades
# ----------------------------------------------------------------------
@dataclass
class Estudiante:
    legajo: str
    nombre: str
    email: str


@dataclass
class Responsable:
    id: int
    nombre: str
    area: str

    MAX_SOLICITUDES_ACTIVAS = 3

    def tiene_capacidad(self, solicitudes_activas):
        return solicitudes_activas < self.MAX_SOLICITUDES_ACTIVAS


@dataclass
class Solicitud:
    id: int
    legajo: str
    tipo: Tipo
    prioridad: Prioridad
    estado: Estado
    descripcion: str
    fecha: datetime.date
    vence: datetime.date
    responsable_id: Optional[int] = None

    @classmethod
    def nueva(cls, id, datos, fecha_alta):
        tipo = Tipo(datos.tipo)
        prioridad = Prioridad(datos.prioridad)
        plazo = cls.calcular_plazo_en_dias(tipo, prioridad)
        return cls(id=id, legajo=datos.legajo, tipo=tipo, prioridad=prioridad, estado=Estado.PENDIENTE,
                   descripcion=datos.descripcion.strip(), fecha=fecha_alta,
                   vence=fecha_alta + datetime.timedelta(days=plazo))

    @staticmethod
    def calcular_plazo_en_dias(tipo, prioridad):
        return prioridad.ajustar_plazo(tipo.plazo_base_en_dias)

    @property
    def esta_activa(self):
        return self.estado.esta_activo

    @property
    def admite_asignacion(self):
        return self.estado.admite_asignacion

    def esta_vencida(self, fecha_corte):
        return self.esta_activa and self.vence < fecha_corte

    def puede_pasar_a(self, estado_nuevo):
        return self.estado.puede_pasar_a(estado_nuevo)

    def falta_responsable_para(self, estado_nuevo):
        return estado_nuevo == Estado.EN_PROCESO and self.responsable_id is None

    def pasar_a(self, estado_nuevo):
        self.estado = estado_nuevo

    def asignar_a(self, id_responsable):
        self.responsable_id = id_responsable
