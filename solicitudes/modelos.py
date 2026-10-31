"""Modelo de dominio: entidades con comportamiento, enumeraciones y objetos de valor."""
import datetime
import re
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Dict, List, Optional

from .errores import ErrorDeDominio

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
# Objetos de valor y de parámetro
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

    def validar(self):
        """Lanza ErrorDeDominio con la primera regla incumplida."""
        if self.legajo is None or self.legajo == "" or not self.legajo.isdigit():
            raise ErrorDeDominio("legajo inválido")
        if self.nombre is None or self.nombre.strip() == "":
            raise ErrorDeDominio("nombre obligatorio")
        if not re.match(PATRON_EMAIL, self.email):
            raise ErrorDeDominio("email inválido")
        if self.tipo not in _valores(Tipo):
            raise ErrorDeDominio(f"tipo inválido: {self.tipo}")
        if self.prioridad not in _valores(Prioridad):
            raise ErrorDeDominio(f"prioridad inválida: {self.prioridad}")
        if self.descripcion is None or len(self.descripcion.strip()) < LARGO_MINIMO_DESCRIPCION:
            raise ErrorDeDominio(f"la descripción debe tener al menos {LARGO_MINIMO_DESCRIPCION} caracteres")
        if len(self.descripcion) > LARGO_MAXIMO_DESCRIPCION:
            raise ErrorDeDominio(f"la descripción no puede superar {LARGO_MAXIMO_DESCRIPCION} caracteres")


@dataclass(frozen=True)
class CriteriosBusqueda:
    """Parameter Object: filtros opcionales de una búsqueda."""
    tipo: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    legajo: Optional[str] = None

    def coincide_con(self, solicitud):
        filtros = (("tipo", self.tipo), ("estado", self.estado),
                   ("prioridad", self.prioridad), ("legajo", self.legajo))
        return all(getattr(solicitud, atributo) == valor for atributo, valor in filtros if valor is not None)


@dataclass(frozen=True)
class Notificacion:
    """Mensaje dirigido a un estudiante; su envío lo resuelve un Notificador."""
    email: str
    mensaje: str


@dataclass(frozen=True)
class Reporte:
    total: int
    por_estado: Dict[Estado, int]
    por_tipo: Dict[Tipo, int]
    fecha_corte: datetime.date
    vencidas: int


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

    @classmethod
    def nuevo(cls, id, nombre, area):
        if nombre is None or nombre.strip() == "" or area is None or area.strip() == "":
            raise ErrorDeDominio("nombre y área son obligatorios")
        return cls(id, nombre.strip(), area.strip())

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

    def esta_vencida(self, fecha_corte):
        return self.esta_activa and self.vence < fecha_corte

    def pasar_a(self, estado_nuevo):
        """Cambia de estado respetando las transiciones permitidas y la regla del responsable."""
        if not self.estado.puede_pasar_a(estado_nuevo):
            raise ErrorDeDominio(f"transición no permitida: {self.estado} -> {estado_nuevo}")
        if estado_nuevo == Estado.EN_PROCESO and self.responsable_id is None:
            raise ErrorDeDominio("la solicitud debe tener un responsable asignado para pasar a EN_PROCESO")
        self.estado = estado_nuevo

    def asignar_a(self, responsable, solicitudes_activas_del_responsable):
        """Asigna un responsable si la solicitud lo admite y el responsable tiene capacidad."""
        if not self.estado.admite_asignacion:
            raise ErrorDeDominio(f"no se puede asignar responsable a una solicitud {self.estado}")
        if not responsable.tiene_capacidad(solicitudes_activas_del_responsable):
            raise ErrorDeDominio(f"el responsable {responsable.nombre} alcanzó el máximo de "
                                 f"{Responsable.MAX_SOLICITUDES_ACTIVAS} solicitudes activas")
        self.responsable_id = responsable.id


# ----------------------------------------------------------------------
# Agregado raíz
# ----------------------------------------------------------------------
@dataclass
class RegistroAcademico:
    """Conjunto de datos del sistema: estudiantes, responsables y solicitudes."""
    ultimo_id: int = 0
    ultimo_responsable: int = 0
    estudiantes: List[Estudiante] = field(default_factory=list)
    responsables: List[Responsable] = field(default_factory=list)
    solicitudes: List[Solicitud] = field(default_factory=list)

    def buscar_solicitud(self, id_solicitud):
        return next((s for s in self.solicitudes if s.id == id_solicitud), None)

    def buscar_responsable(self, id_responsable):
        return next((r for r in self.responsables if r.id == id_responsable), None)

    def buscar_estudiante(self, legajo):
        return next((e for e in self.estudiantes if e.legajo == legajo), None)

    def obtener_o_crear_estudiante(self, datos):
        estudiante = self.buscar_estudiante(datos.legajo)
        if estudiante is None:
            estudiante = Estudiante(datos.legajo, datos.nombre.strip(), datos.email)
            self.estudiantes.append(estudiante)
        return estudiante

    def agregar_solicitud(self, datos, fecha_alta):
        self.ultimo_id += 1
        solicitud = Solicitud.nueva(self.ultimo_id, datos, fecha_alta)
        self.solicitudes.append(solicitud)
        return solicitud

    def agregar_responsable(self, nombre, area):
        responsable = Responsable.nuevo(self.ultimo_responsable + 1, nombre, area)
        self.ultimo_responsable = responsable.id
        self.responsables.append(responsable)
        return responsable

    def contar_solicitudes_activas(self, id_responsable, id_solicitud_excluida):
        return sum(1 for s in self.solicitudes
                   if s.responsable_id == id_responsable and s.esta_activa and s.id != id_solicitud_excluida)

    def filtrar(self, criterios):
        return [s for s in self.solicitudes if criterios.coincide_con(s)]

    def generar_reporte(self, fecha_corte):
        return Reporte(
            total=len(self.solicitudes),
            por_estado=self._contar_por("estado", Estado),
            por_tipo=self._contar_por("tipo", Tipo),
            fecha_corte=fecha_corte,
            vencidas=sum(1 for s in self.solicitudes if s.esta_vencida(fecha_corte)),
        )

    def _contar_por(self, atributo, enumeracion):
        conteo = {miembro: 0 for miembro in enumeracion}
        for solicitud in self.solicitudes:
            conteo[getattr(solicitud, atributo)] += 1
        return conteo
