"""Notificaciones: abstracción e implementación por consola."""
from abc import ABC, abstractmethod

from .modelos import Notificacion
from .presentacion import formatear_notificacion


class Notificador(ABC):
    """Puerto de notificación: permite reemplazar la consola por correo real sin tocar el servicio."""

    @abstractmethod
    def notificar(self, notificacion: Notificacion) -> None:
        """Envía la notificación al estudiante."""


class NotificadorConsola(Notificador):
    def notificar(self, notificacion):
        print(formatear_notificacion(notificacion))
