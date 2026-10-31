import json
import os
import datetime

from modelos import Estado, Estudiante, Prioridad, Responsable, Solicitud, Tipo

RUTA_DATOS = "datos.json"
FORMATO_FECHA = "%Y-%m-%d"
MENSAJE_FECHA_INVALIDA = "ERROR: fecha inválida (use AAAA-MM-DD)"


class GestorSolicitudes:

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def cargar(self):
        vacio = {"ultimo_id": 0, "ultimo_resp": 0, "estudiantes": [], "responsables": [], "solicitudes": []}
        if not os.path.exists(RUTA_DATOS):
            return vacio
        archivo = open(RUTA_DATOS, "r", encoding="utf-8")
        try:
            datos = json.load(archivo)
        except:
            datos = vacio
        archivo.close()
        datos["estudiantes"] = [Estudiante(e["legajo"], e["nombre"], e["email"]) for e in datos["estudiantes"]]
        datos["responsables"] = [Responsable(r["id"], r["nombre"], r["area"]) for r in datos["responsables"]]
        datos["solicitudes"] = [self._desde_registro(s) for s in datos["solicitudes"]]
        return datos

    def _desde_registro(self, registro):
        return Solicitud(
            id=registro["id"], legajo=registro["legajo"], tipo=Tipo(registro["tipo"]),
            prioridad=Prioridad(registro["prioridad"]), estado=Estado(registro["estado"]),
            descripcion=registro["descripcion"], fecha=datetime.date.fromisoformat(registro["fecha"]),
            vence=datetime.date.fromisoformat(registro["vence"]), responsable_id=registro["responsable_id"],
        )

    def _a_registro(self, solicitud):
        return {
            "id": solicitud.id, "legajo": solicitud.legajo, "tipo": str(solicitud.tipo),
            "prioridad": str(solicitud.prioridad), "estado": str(solicitud.estado),
            "descripcion": solicitud.descripcion, "fecha": solicitud.fecha.isoformat(),
            "vence": solicitud.vence.isoformat(), "responsable_id": solicitud.responsable_id,
        }

    def guardar(self, datos):
        salida = {
            "ultimo_id": datos["ultimo_id"],
            "ultimo_resp": datos["ultimo_resp"],
            "estudiantes": [vars(e) for e in datos["estudiantes"]],
            "responsables": [vars(r) for r in datos["responsables"]],
            "solicitudes": [self._a_registro(s) for s in datos["solicitudes"]],
        }
        archivo = open(RUTA_DATOS, "w", encoding="utf-8")
        archivo.write(json.dumps(salida, indent=2, ensure_ascii=False))
        archivo.close()

    # ------------------------------------------------------------------
    # Consultas auxiliares
    # ------------------------------------------------------------------
    def _buscar_solicitud(self, datos, id_solicitud):
        encontrada = None
        for solicitud in datos["solicitudes"]:
            if solicitud.id == id_solicitud:
                encontrada = solicitud
        return encontrada

    def _buscar_responsable(self, datos, id_responsable):
        encontrado = None
        for responsable in datos["responsables"]:
            if responsable.id == id_responsable:
                encontrado = responsable
        return encontrado

    def _buscar_estudiante(self, datos, legajo):
        encontrado = None
        for estudiante in datos["estudiantes"]:
            if estudiante.legajo == legajo:
                encontrado = estudiante
        return encontrado

    def _resolver_fecha(self, texto):
        """Devuelve la fecha indicada, la fecha actual si no se indicó, o None si es inválida."""
        if texto is None:
            return datetime.date.today()
        try:
            return datetime.datetime.strptime(texto, FORMATO_FECHA).date()
        except ValueError:
            return None

    # ------------------------------------------------------------------
    # Registrar solicitud
    # ------------------------------------------------------------------
    def _obtener_o_crear_estudiante(self, datos, datos_solicitud):
        estudiante = self._buscar_estudiante(datos, datos_solicitud.legajo)
        if estudiante is None:
            estudiante = Estudiante(datos_solicitud.legajo, datos_solicitud.nombre.strip(), datos_solicitud.email)
            datos["estudiantes"].append(estudiante)
        return estudiante

    def registrar_solicitud(self, datos_solicitud):
        error = datos_solicitud.primer_error()
        if error:
            print(error)
            return -1
        fecha_alta = self._resolver_fecha(datos_solicitud.fecha)
        if fecha_alta is None:
            print(MENSAJE_FECHA_INVALIDA)
            return -1

        datos = self.cargar()
        estudiante = self._obtener_o_crear_estudiante(datos, datos_solicitud)
        datos["ultimo_id"] = datos["ultimo_id"] + 1
        solicitud = Solicitud.nueva(datos["ultimo_id"], datos_solicitud, fecha_alta)
        datos["solicitudes"].append(solicitud)
        self.guardar(datos)

        print("Solicitud #" + str(solicitud.id) + " registrada (tipo=" + solicitud.tipo + ", prioridad="
              + solicitud.prioridad + ", vence=" + solicitud.vence.isoformat() + ")")
        print("[NOTIFICACIÓN] Email a " + estudiante.email + ": su solicitud #" + str(solicitud.id)
              + " fue registrada")
        return solicitud.id

    # ------------------------------------------------------------------
    # Responsables
    # ------------------------------------------------------------------
    def alta_responsable(self, nombre, area):
        if nombre is None or nombre.strip() == "" or area is None or area.strip() == "":
            print("ERROR: nombre y área son obligatorios")
            return -1
        datos = self.cargar()
        datos["ultimo_resp"] = datos["ultimo_resp"] + 1
        responsable = Responsable(datos["ultimo_resp"], nombre.strip(), area.strip())
        datos["responsables"].append(responsable)
        self.guardar(datos)
        print("Responsable #" + str(responsable.id) + " creado: " + responsable.nombre
              + " (" + responsable.area + ")")
        return responsable.id

    def _contar_solicitudes_activas(self, datos, id_responsable, id_solicitud_excluida):
        cantidad = 0
        for solicitud in datos["solicitudes"]:
            if (solicitud.responsable_id == id_responsable and solicitud.esta_activa
                    and solicitud.id != id_solicitud_excluida):
                cantidad = cantidad + 1
        return cantidad

    def asignar_responsable(self, id_solicitud, id_responsable):
        datos = self.cargar()
        solicitud = self._buscar_solicitud(datos, id_solicitud)
        if solicitud is None:
            print("ERROR: solicitud " + str(id_solicitud) + " no encontrada")
            return 1
        responsable = self._buscar_responsable(datos, id_responsable)
        if responsable is None:
            print("ERROR: responsable " + str(id_responsable) + " no encontrado")
            return 2
        if not solicitud.admite_asignacion:
            print("ERROR: no se puede asignar responsable a una solicitud " + solicitud.estado)
            return 3
        activas = self._contar_solicitudes_activas(datos, id_responsable, id_solicitud)
        if not responsable.tiene_capacidad(activas):
            print("ERROR: el responsable " + responsable.nombre + " alcanzó el máximo de "
                  + str(Responsable.MAX_SOLICITUDES_ACTIVAS) + " solicitudes activas")
            return 4
        solicitud.asignar_a(id_responsable)
        self.guardar(datos)
        print("Solicitud #" + str(id_solicitud) + " asignada a " + responsable.nombre
              + " (" + responsable.area + ")")
        return 0

    # ------------------------------------------------------------------
    # Cambio de estado
    # ------------------------------------------------------------------
    def cambiar_estado(self, id_solicitud, texto_estado):
        try:
            estado_nuevo = Estado(texto_estado)
        except ValueError:
            print("ERROR: estado inválido: " + texto_estado)
            return False
        datos = self.cargar()
        solicitud = self._buscar_solicitud(datos, id_solicitud)
        if solicitud is None:
            print("ERROR: solicitud " + str(id_solicitud) + " no encontrada")
            return False
        estado_anterior = solicitud.estado
        if not solicitud.puede_pasar_a(estado_nuevo):
            print("ERROR: transición no permitida: " + estado_anterior + " -> " + estado_nuevo)
            return False
        if solicitud.falta_responsable_para(estado_nuevo):
            print("ERROR: la solicitud debe tener un responsable asignado para pasar a EN_PROCESO")
            return False
        solicitud.pasar_a(estado_nuevo)
        self.guardar(datos)
        print("Solicitud #" + str(id_solicitud) + ": " + estado_anterior + " -> " + estado_nuevo)
        estudiante = self._buscar_estudiante(datos, solicitud.legajo)
        if estudiante is not None:
            print("[NOTIFICACIÓN] Email a " + estudiante.email + ": su solicitud #" + str(id_solicitud)
                  + " cambió a " + estado_nuevo)
        return True

    # ------------------------------------------------------------------
    # Búsqueda
    # ------------------------------------------------------------------
    def _filtrar_por(self, solicitudes, atributo, valor):
        return [s for s in solicitudes if getattr(s, atributo) == valor]

    def _formatear_linea(self, solicitud):
        return ("#" + str(solicitud.id) + " | " + solicitud.tipo + " | " + solicitud.prioridad + " | "
                + solicitud.estado + " | legajo " + solicitud.legajo + " | vence "
                + solicitud.vence.isoformat())

    def buscar(self, criterios):
        resultado = self.cargar()["solicitudes"]
        filtros = (("tipo", criterios.tipo), ("estado", criterios.estado),
                   ("prioridad", criterios.prioridad), ("legajo", criterios.legajo))
        for atributo, valor in filtros:
            if valor is not None:
                resultado = self._filtrar_por(resultado, atributo, valor)
        if len(resultado) == 0:
            print("Sin resultados.")
            return resultado
        for solicitud in resultado:
            print(self._formatear_linea(solicitud))
        return resultado

    # ------------------------------------------------------------------
    # Reporte
    # ------------------------------------------------------------------
    def _contar_por(self, solicitudes, atributo, claves):
        conteo = {clave: 0 for clave in claves}
        for solicitud in solicitudes:
            conteo[getattr(solicitud, atributo)] = conteo[getattr(solicitud, atributo)] + 1
        return conteo

    def _imprimir_reporte(self, total, por_estado, por_tipo, fecha_corte, vencidas):
        print("=== REPORTE DE SOLICITUDES ===")
        print("Total: " + str(total))
        print("Por estado:")
        for estado in por_estado:
            print("  " + estado + ": " + str(por_estado[estado]))
        print("Por tipo:")
        for tipo in por_tipo:
            print("  " + tipo + ": " + str(por_tipo[tipo]))
        print("Vencidas al " + fecha_corte.isoformat() + ": " + str(vencidas))

    def reporte(self, hoy=None):
        fecha_corte = self._resolver_fecha(hoy)
        if fecha_corte is None:
            print(MENSAJE_FECHA_INVALIDA)
            return -1
        solicitudes = self.cargar()["solicitudes"]
        vencidas = len([s for s in solicitudes if s.esta_vencida(fecha_corte)])
        self._imprimir_reporte(
            len(solicitudes),
            self._contar_por(solicitudes, "estado", list(Estado)),
            self._contar_por(solicitudes, "tipo", list(Tipo)),
            fecha_corte,
            vencidas,
        )
        return 0
