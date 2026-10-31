"""Presentación: convierte resultados del dominio en texto para el usuario (sin lógica de negocio)."""


def formatear_registro(solicitud):
    return (f"Solicitud #{solicitud.id} registrada (tipo={solicitud.tipo}, prioridad={solicitud.prioridad}, "
            f"vence={solicitud.vence.isoformat()})")


def formatear_alta_responsable(responsable):
    return f"Responsable #{responsable.id} creado: {responsable.nombre} ({responsable.area})"


def formatear_cambio_estado(id_solicitud, estado_anterior, estado_nuevo):
    return f"Solicitud #{id_solicitud}: {estado_anterior} -> {estado_nuevo}"


def formatear_asignacion(solicitud, responsable):
    return f"Solicitud #{solicitud.id} asignada a {responsable.nombre} ({responsable.area})"


def formatear_fila(solicitud):
    return (f"#{solicitud.id} | {solicitud.tipo} | {solicitud.prioridad} | {solicitud.estado} | "
            f"legajo {solicitud.legajo} | vence {solicitud.vence.isoformat()}")


def formatear_notificacion(notificacion):
    return f"[NOTIFICACIÓN] Email a {notificacion.email}: {notificacion.mensaje}"


def formatear_reporte(reporte):
    lineas = ["=== REPORTE DE SOLICITUDES ===", f"Total: {reporte.total}", "Por estado:"]
    lineas += [f"  {estado}: {cantidad}" for estado, cantidad in reporte.por_estado.items()]
    lineas.append("Por tipo:")
    lineas += [f"  {tipo}: {cantidad}" for tipo, cantidad in reporte.por_tipo.items()]
    lineas.append(f"Vencidas al {reporte.fecha_corte.isoformat()}: {reporte.vencidas}")
    return lineas
