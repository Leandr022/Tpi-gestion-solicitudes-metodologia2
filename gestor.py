import json
import os
import re
import datetime

from modelos import Estudiante, Responsable, Solicitud

RUTA_DATOS = "datos.json"
FORMATO_FECHA = "%Y-%m-%d"
PATRON_EMAIL = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
MENSAJE_FECHA_INVALIDA = "ERROR: fecha inválida (use AAAA-MM-DD)"

LARGO_MINIMO_DESCRIPCION = 10
LARGO_MAXIMO_DESCRIPCION = 200
MAX_SOLICITUDES_ACTIVAS = 3

TIPOS_VALIDOS = ["CERTIFICADO", "EQUIVALENCIA", "REINCORPORACION", "CONSULTA"]
PRIORIDADES_VALIDAS = ["ALTA", "MEDIA", "BAJA"]
PRIORIDAD_ALTA = "ALTA"
PRIORIDAD_BAJA = "BAJA"

PENDIENTE = "PENDIENTE"
EN_PROCESO = "EN_PROCESO"
RESUELTA = "RESUELTA"
RECHAZADA = "RECHAZADA"
CERRADA = "CERRADA"
ESTADOS_VALIDOS = [PENDIENTE, EN_PROCESO, RESUELTA, RECHAZADA, CERRADA]
ESTADOS_ACTIVOS = [PENDIENTE, EN_PROCESO]
ESTADOS_NO_ASIGNABLES = [RESUELTA, RECHAZADA, CERRADA]
TRANSICIONES_PERMITIDAS = {
    PENDIENTE: [EN_PROCESO, RECHAZADA],
    EN_PROCESO: [RESUELTA, RECHAZADA],
    RESUELTA: [CERRADA],
}

PLAZO_BASE_EN_DIAS = {"CERTIFICADO": 5, "EQUIVALENCIA": 15, "REINCORPORACION": 10, "CONSULTA": 3}
DIVISOR_PLAZO_PRIORIDAD_ALTA = 2
DIAS_ADICIONALES_PRIORIDAD_BAJA = 5


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
        datos["solicitudes"] = [
            Solicitud(s["id"], s["legajo"], s["tipo"], s["prioridad"], s["estado"], s["descripcion"],
                      s["fecha"], s["vence"], s["responsable_id"])
            for s in datos["solicitudes"]
        ]
        return datos

    def guardar(self, datos):
        salida = {
            "ultimo_id": datos["ultimo_id"],
            "ultimo_resp": datos["ultimo_resp"],
            "estudiantes": [e.__dict__ for e in datos["estudiantes"]],
            "responsables": [r.__dict__ for r in datos["responsables"]],
            "solicitudes": [s.__dict__ for s in datos["solicitudes"]],
        }
        archivo = open(RUTA_DATOS, "w", encoding="utf-8")
        archivo.write(json.dumps(salida, indent=2, ensure_ascii=False))
        archivo.close()

    # ------------------------------------------------------------------
    # Consultas auxiliares (antes duplicadas en cada operación)
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
    def _validar_datos_de_registro(self, legajo, nombre, email, tipo, prioridad, descripcion):
        """Devuelve el mensaje de error de la primera regla incumplida, o None si todo es válido."""
        if legajo is None or legajo == "" or not legajo.isdigit():
            return "ERROR: legajo inválido"
        if nombre is None or nombre.strip() == "":
            return "ERROR: nombre obligatorio"
        if not re.match(PATRON_EMAIL, email):
            return "ERROR: email inválido"
        if tipo not in TIPOS_VALIDOS:
            return "ERROR: tipo inválido: " + tipo
        if prioridad not in PRIORIDADES_VALIDAS:
            return "ERROR: prioridad inválida: " + prioridad
        if descripcion is None or len(descripcion.strip()) < LARGO_MINIMO_DESCRIPCION:
            return "ERROR: la descripción debe tener al menos " + str(LARGO_MINIMO_DESCRIPCION) + " caracteres"
        if len(descripcion) > LARGO_MAXIMO_DESCRIPCION:
            return "ERROR: la descripción no puede superar " + str(LARGO_MAXIMO_DESCRIPCION) + " caracteres"
        return None

    def _calcular_plazo_en_dias(self, tipo, prioridad):
        plazo = PLAZO_BASE_EN_DIAS[tipo]
        if prioridad == PRIORIDAD_ALTA:
            plazo = plazo // DIVISOR_PLAZO_PRIORIDAD_ALTA
        elif prioridad == PRIORIDAD_BAJA:
            plazo = plazo + DIAS_ADICIONALES_PRIORIDAD_BAJA
        return plazo

    def _obtener_o_crear_estudiante(self, datos, legajo, nombre, email):
        estudiante = self._buscar_estudiante(datos, legajo)
        if estudiante is None:
            estudiante = Estudiante(legajo, nombre.strip(), email)
            datos["estudiantes"].append(estudiante)
        return estudiante

    def registrar_solicitud(self, legajo, nombre, email, tipo, prioridad, descripcion, fecha=None):
        error = self._validar_datos_de_registro(legajo, nombre, email, tipo, prioridad, descripcion)
        if error:
            print(error)
            return -1
        fecha_alta = self._resolver_fecha(fecha)
        if fecha_alta is None:
            print(MENSAJE_FECHA_INVALIDA)
            return -1
        vencimiento = fecha_alta + datetime.timedelta(days=self._calcular_plazo_en_dias(tipo, prioridad))

        datos = self.cargar()
        estudiante = self._obtener_o_crear_estudiante(datos, legajo, nombre, email)
        datos["ultimo_id"] = datos["ultimo_id"] + 1
        solicitud = Solicitud(datos["ultimo_id"], legajo, tipo, prioridad, PENDIENTE, descripcion.strip(),
                              fecha_alta.isoformat(), vencimiento.isoformat(), None)
        datos["solicitudes"].append(solicitud)
        self.guardar(datos)

        print("Solicitud #" + str(solicitud.id) + " registrada (tipo=" + tipo + ", prioridad=" + prioridad
              + ", vence=" + solicitud.vence + ")")
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
            if (solicitud.responsable_id == id_responsable and solicitud.estado in ESTADOS_ACTIVOS
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
        if solicitud.estado in ESTADOS_NO_ASIGNABLES:
            print("ERROR: no se puede asignar responsable a una solicitud " + solicitud.estado)
            return 3
        if self._contar_solicitudes_activas(datos, id_responsable, id_solicitud) >= MAX_SOLICITUDES_ACTIVAS:
            print("ERROR: el responsable " + responsable.nombre + " alcanzó el máximo de "
                  + str(MAX_SOLICITUDES_ACTIVAS) + " solicitudes activas")
            return 4
        solicitud.responsable_id = id_responsable
        self.guardar(datos)
        print("Solicitud #" + str(id_solicitud) + " asignada a " + responsable.nombre
              + " (" + responsable.area + ")")
        return 0

    # ------------------------------------------------------------------
    # Cambio de estado
    # ------------------------------------------------------------------
    def _transicion_permitida(self, estado_actual, estado_nuevo):
        return estado_nuevo in TRANSICIONES_PERMITIDAS.get(estado_actual, [])

    def cambiar_estado(self, id_solicitud, estado_nuevo):
        if estado_nuevo not in ESTADOS_VALIDOS:
            print("ERROR: estado inválido: " + estado_nuevo)
            return False
        datos = self.cargar()
        solicitud = self._buscar_solicitud(datos, id_solicitud)
        if solicitud is None:
            print("ERROR: solicitud " + str(id_solicitud) + " no encontrada")
            return False
        estado_anterior = solicitud.estado
        if not self._transicion_permitida(estado_anterior, estado_nuevo):
            print("ERROR: transición no permitida: " + estado_anterior + " -> " + estado_nuevo)
            return False
        if estado_nuevo == EN_PROCESO and solicitud.responsable_id is None:
            print("ERROR: la solicitud debe tener un responsable asignado para pasar a EN_PROCESO")
            return False
        solicitud.estado = estado_nuevo
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
                + solicitud.estado + " | legajo " + solicitud.legajo + " | vence " + solicitud.vence)

    def buscar(self, tipo=None, estado=None, prioridad=None, legajo=None):
        resultado = self.cargar()["solicitudes"]
        filtros = (("tipo", tipo), ("estado", estado), ("prioridad", prioridad), ("legajo", legajo))
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

    def _contar_vencidas(self, solicitudes, fecha_corte):
        cantidad = 0
        for solicitud in solicitudes:
            if solicitud.estado in ESTADOS_ACTIVOS and solicitud.vence < fecha_corte.isoformat():
                cantidad = cantidad + 1
        return cantidad

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
        self._imprimir_reporte(
            len(solicitudes),
            self._contar_por(solicitudes, "estado", ESTADOS_VALIDOS),
            self._contar_por(solicitudes, "tipo", TIPOS_VALIDOS),
            fecha_corte,
            self._contar_vencidas(solicitudes, fecha_corte),
        )
        return 0
