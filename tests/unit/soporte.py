"""Dobles de prueba y fábricas compartidas por las pruebas unitarias."""
import datetime

from solicitudes.modelos import DatosSolicitud, RegistroAcademico
from solicitudes.notificador import Notificador
from solicitudes.repositorio import RepositorioDeRegistro

FECHA = datetime.date(2026, 11, 2)


class RepositorioEnMemoria(RepositorioDeRegistro):
    """Doble de prueba del repositorio: evidencia que el servicio depende de la abstracción (DIP)."""

    def __init__(self):
        self.registro = RegistroAcademico()
        self.cantidad_de_guardados = 0

    def cargar(self):
        return self.registro

    def guardar(self, registro):
        self.registro = registro
        self.cantidad_de_guardados += 1


class NotificadorEnMemoria(Notificador):
    def __init__(self):
        self.enviadas = []

    def notificar(self, notificacion):
        self.enviadas.append(notificacion)


def datos(**cambios):
    base = dict(legajo="1001", nombre="Ana Gómez", email="ana@example.com", tipo="CERTIFICADO",
                prioridad="MEDIA", descripcion="Certificado de alumno regular", fecha="2026-11-02")
    base.update(cambios)
    return DatosSolicitud(**base)
