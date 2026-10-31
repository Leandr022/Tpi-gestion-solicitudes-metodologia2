import sys
import argparse

from gestor import GestorSolicitudes
from modelos import CriteriosBusqueda, DatosSolicitud


def main():
    p = argparse.ArgumentParser(description="Sistema de Gestión de Solicitudes Académicas")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("registrar")
    a.add_argument("--legajo", required=True)
    a.add_argument("--nombre", required=True)
    a.add_argument("--email", required=True)
    a.add_argument("--tipo", required=True)
    a.add_argument("--prioridad", required=True)
    a.add_argument("--descripcion", required=True)
    a.add_argument("--fecha", default=None)

    b = sub.add_parser("alta-responsable")
    b.add_argument("--nombre", required=True)
    b.add_argument("--area", required=True)

    c = sub.add_parser("cambiar-estado")
    c.add_argument("--id", type=int, required=True)
    c.add_argument("--estado", required=True)

    e = sub.add_parser("asignar")
    e.add_argument("--id", type=int, required=True)
    e.add_argument("--responsable-id", type=int, required=True)

    f = sub.add_parser("buscar")
    f.add_argument("--tipo", default=None)
    f.add_argument("--estado", default=None)
    f.add_argument("--prioridad", default=None)
    f.add_argument("--legajo", default=None)

    g = sub.add_parser("reporte")
    g.add_argument("--hoy", default=None)

    x = p.parse_args()
    gs = GestorSolicitudes()

    if x.cmd == "registrar":
        datos_solicitud = DatosSolicitud(x.legajo, x.nombre, x.email, x.tipo, x.prioridad, x.descripcion, x.fecha)
        r = gs.registrar_solicitud(datos_solicitud)
        if r == -1:
            sys.exit(1)
    elif x.cmd == "alta-responsable":
        r = gs.alta_responsable(x.nombre, x.area)
        if r == -1:
            sys.exit(1)
    elif x.cmd == "cambiar-estado":
        r = gs.cambiar_estado(x.id, x.estado)
        if r == False:
            sys.exit(1)
    elif x.cmd == "asignar":
        r = gs.asignar_responsable(x.id, x.responsable_id)
        if r != 0:
            sys.exit(1)
    elif x.cmd == "buscar":
        gs.buscar(CriteriosBusqueda(x.tipo, x.estado, x.prioridad, x.legajo))
    elif x.cmd == "reporte":
        r = gs.reporte(x.hoy)
        if r == -1:
            sys.exit(1)


if __name__ == "__main__":
    main()
