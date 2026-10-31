from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DatosSolicitud:
    """Parameter Object: agrupa los datos necesarios para registrar una solicitud."""
    legajo: str
    nombre: str
    email: str
    tipo: str
    prioridad: str
    descripcion: str
    fecha: Optional[str] = None


@dataclass(frozen=True)
class CriteriosBusqueda:
    """Parameter Object: agrupa los filtros opcionales de una búsqueda."""
    tipo: Optional[str] = None
    estado: Optional[str] = None
    prioridad: Optional[str] = None
    legajo: Optional[str] = None


class Estudiante:
    def __init__(self, legajo, nombre, email):
        self.legajo = legajo
        self.nombre = nombre
        self.email = email


class Responsable:
    def __init__(self, id, nombre, area):
        self.id = id
        self.nombre = nombre
        self.area = area


class Solicitud:
    def __init__(self, id, legajo, tipo, prioridad, estado, descripcion, fecha, vence, responsable_id):
        self.id = id
        self.legajo = legajo
        self.tipo = tipo
        self.prioridad = prioridad
        self.estado = estado
        self.descripcion = descripcion
        self.fecha = fecha
        self.vence = vence
        self.responsable_id = responsable_id
