"""Errores del dominio de la aplicación."""


class ErrorDeDominio(Exception):
    """Regla de negocio o dato de entrada incumplido.

    Su mensaje está pensado para mostrarse al usuario (sin el prefijo "ERROR: ").
    Reemplaza a los códigos de retorno heterogéneos (-1, False, 1..4) de la versión inicial.
    """
