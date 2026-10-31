"""Persistencia: abstracción del repositorio e implementación en archivo JSON."""
import datetime
import json
import os
from abc import ABC, abstractmethod

from .errores import ErrorDeDominio
from .modelos import Estado, Estudiante, Prioridad, RegistroAcademico, Responsable, Solicitud, Tipo


class RepositorioDeRegistro(ABC):
    """Puerto de persistencia: el servicio depende de esta abstracción (DIP)."""

    @abstractmethod
    def cargar(self) -> RegistroAcademico:
        """Devuelve el registro completo (vacío si todavía no existe)."""

    @abstractmethod
    def guardar(self, registro: RegistroAcademico) -> None:
        """Persiste el registro completo."""


class RepositorioJSON(RepositorioDeRegistro):
    """Guarda el registro en un archivo JSON, con el mismo formato que la versión inicial."""

    def __init__(self, ruta):
        self._ruta = str(ruta)

    def cargar(self):
        if not os.path.exists(self._ruta):
            return RegistroAcademico()
        try:
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                return self._desde_dict(json.load(archivo))
        except (ValueError, KeyError, TypeError) as causa:
            # Mejora respecto de la versión inicial (CS-09): un archivo corrupto ya no se
            # reemplaza en silencio por uno vacío; se informa y se conservan los datos.
            raise ErrorDeDominio(f"el archivo de datos está corrupto: {self._ruta}") from causa

    def guardar(self, registro):
        contenido = json.dumps(self._a_dict(registro), indent=2, ensure_ascii=False)
        temporal = self._ruta + ".tmp"
        with open(temporal, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)
        os.replace(temporal, self._ruta)  # escritura atómica: nunca queda un archivo a medias

    @staticmethod
    def _desde_dict(datos):
        return RegistroAcademico(
            ultimo_id=datos["ultimo_id"],
            ultimo_responsable=datos["ultimo_resp"],
            estudiantes=[Estudiante(e["legajo"], e["nombre"], e["email"]) for e in datos["estudiantes"]],
            responsables=[Responsable(r["id"], r["nombre"], r["area"]) for r in datos["responsables"]],
            solicitudes=[
                Solicitud(
                    id=s["id"], legajo=s["legajo"], tipo=Tipo(s["tipo"]), prioridad=Prioridad(s["prioridad"]),
                    estado=Estado(s["estado"]), descripcion=s["descripcion"],
                    fecha=datetime.date.fromisoformat(s["fecha"]), vence=datetime.date.fromisoformat(s["vence"]),
                    responsable_id=s["responsable_id"],
                )
                for s in datos["solicitudes"]
            ],
        )

    @staticmethod
    def _a_dict(registro):
        return {
            "ultimo_id": registro.ultimo_id,
            "ultimo_resp": registro.ultimo_responsable,
            "estudiantes": [vars(e) for e in registro.estudiantes],
            "responsables": [vars(r) for r in registro.responsables],
            "solicitudes": [
                {
                    "id": s.id, "legajo": s.legajo, "tipo": str(s.tipo), "prioridad": str(s.prioridad),
                    "estado": str(s.estado), "descripcion": s.descripcion, "fecha": s.fecha.isoformat(),
                    "vence": s.vence.isoformat(), "responsable_id": s.responsable_id,
                }
                for s in registro.solicitudes
            ],
        }
