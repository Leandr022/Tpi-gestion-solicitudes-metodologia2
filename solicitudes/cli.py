"""Interfaz de línea de comandos: interpreta argumentos, invoca al servicio y muestra los resultados."""
import argparse

from .errores import ErrorDeDominio
from .modelos import CriteriosBusqueda, DatosSolicitud
from .notificador import NotificadorConsola
from .presentacion import (formatear_alta_responsable, formatear_asignacion, formatear_cambio_estado,
                           formatear_fila, formatear_registro, formatear_reporte)
from .repositorio import RepositorioJSON
from .servicio import ServicioSolicitudes

RUTA_DATOS_POR_DEFECTO = "datos.json"


def crear_parser():
    parser = argparse.ArgumentParser(description="Sistema de Gestión de Solicitudes Académicas")
    subcomandos = parser.add_subparsers(dest="comando", required=True)

    registrar = subcomandos.add_parser("registrar")
    for opcion in ("legajo", "nombre", "email", "tipo", "prioridad", "descripcion"):
        registrar.add_argument(f"--{opcion}", required=True)
    registrar.add_argument("--fecha", default=None)

    alta = subcomandos.add_parser("alta-responsable")
    alta.add_argument("--nombre", required=True)
    alta.add_argument("--area", required=True)

    cambio = subcomandos.add_parser("cambiar-estado")
    cambio.add_argument("--id", type=int, required=True)
    cambio.add_argument("--estado", required=True)

    asignacion = subcomandos.add_parser("asignar")
    asignacion.add_argument("--id", type=int, required=True)
    asignacion.add_argument("--responsable-id", type=int, required=True)

    busqueda = subcomandos.add_parser("buscar")
    for opcion in ("tipo", "estado", "prioridad", "legajo"):
        busqueda.add_argument(f"--{opcion}", default=None)

    reporte = subcomandos.add_parser("reporte")
    reporte.add_argument("--hoy", default=None)
    return parser


def _registrar(args, servicio, notificador):
    datos = DatosSolicitud(args.legajo, args.nombre, args.email, args.tipo, args.prioridad,
                           args.descripcion, args.fecha)
    resultado = servicio.registrar_solicitud(datos)
    print(formatear_registro(resultado.solicitud))
    notificador.notificar(resultado.notificacion)


def _alta_responsable(args, servicio, notificador):
    print(formatear_alta_responsable(servicio.alta_responsable(args.nombre, args.area)))


def _cambiar_estado(args, servicio, notificador):
    resultado = servicio.cambiar_estado(args.id, args.estado)
    print(formatear_cambio_estado(args.id, resultado.estado_anterior, resultado.solicitud.estado))
    if resultado.notificacion is not None:
        notificador.notificar(resultado.notificacion)


def _asignar(args, servicio, notificador):
    resultado = servicio.asignar_responsable(args.id, args.responsable_id)
    print(formatear_asignacion(resultado.solicitud, resultado.responsable))


def _buscar(args, servicio, notificador):
    solicitudes = servicio.buscar(CriteriosBusqueda(args.tipo, args.estado, args.prioridad, args.legajo))
    if not solicitudes:
        print("Sin resultados.")
    for solicitud in solicitudes:
        print(formatear_fila(solicitud))


def _reporte(args, servicio, notificador):
    for linea in formatear_reporte(servicio.generar_reporte(args.hoy)):
        print(linea)


COMANDOS = {
    "registrar": _registrar,
    "alta-responsable": _alta_responsable,
    "cambiar-estado": _cambiar_estado,
    "asignar": _asignar,
    "buscar": _buscar,
    "reporte": _reporte,
}


def main(argv=None, ruta_datos=RUTA_DATOS_POR_DEFECTO, notificador=None):
    """Ejecuta un comando y devuelve el código de salida (0 = éxito, 1 = error de dominio)."""
    args = crear_parser().parse_args(argv)
    servicio = ServicioSolicitudes(RepositorioJSON(ruta_datos))
    notificador = notificador or NotificadorConsola()
    try:
        COMANDOS[args.comando](args, servicio, notificador)
    except ErrorDeDominio as error:
        print(f"ERROR: {error}")
        return 1
    return 0
