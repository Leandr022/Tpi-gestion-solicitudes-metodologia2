import json
import os
import re
import datetime

from modelos import Estudiante, Responsable, Solicitud

RUTA = "datos.json"


class GestorSolicitudes:

    def cargar(self):
        vacio = {"ultimo_id": 0, "ultimo_resp": 0, "estudiantes": [], "responsables": [], "solicitudes": []}
        if not os.path.exists(RUTA):
            return vacio
        f = open(RUTA, "r", encoding="utf-8")
        try:
            d = json.load(f)
        except:
            d = vacio
        f.close()
        d["estudiantes"] = [Estudiante(x["legajo"], x["nombre"], x["email"]) for x in d["estudiantes"]]
        d["responsables"] = [Responsable(x["id"], x["nombre"], x["area"]) for x in d["responsables"]]
        d["solicitudes"] = [Solicitud(x["id"], x["legajo"], x["tipo"], x["prioridad"], x["estado"], x["descripcion"], x["fecha"], x["vence"], x["responsable_id"]) for x in d["solicitudes"]]
        return d

    def guardar(self, d):
        out = {
            "ultimo_id": d["ultimo_id"],
            "ultimo_resp": d["ultimo_resp"],
            "estudiantes": [e.__dict__ for e in d["estudiantes"]],
            "responsables": [r.__dict__ for r in d["responsables"]],
            "solicitudes": [s.__dict__ for s in d["solicitudes"]],
        }
        f = open(RUTA, "w", encoding="utf-8")
        f.write(json.dumps(out, indent=2, ensure_ascii=False))
        f.close()

    def registrar_solicitud(self, legajo, nombre, email, tipo, prioridad, descripcion, fecha=None):
        # validaciones
        if legajo is None or legajo == "" or not legajo.isdigit():
            print("ERROR: legajo inválido")
            return -1
        if nombre is None or nombre.strip() == "":
            print("ERROR: nombre obligatorio")
            return -1
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            print("ERROR: email inválido")
            return -1
        if tipo not in ["CERTIFICADO", "EQUIVALENCIA", "REINCORPORACION", "CONSULTA"]:
            print("ERROR: tipo inválido: " + tipo)
            return -1
        if prioridad not in ["ALTA", "MEDIA", "BAJA"]:
            print("ERROR: prioridad inválida: " + prioridad)
            return -1
        if descripcion is None or len(descripcion.strip()) < 10:
            print("ERROR: la descripción debe tener al menos 10 caracteres")
            return -1
        if len(descripcion) > 200:
            print("ERROR: la descripción no puede superar 200 caracteres")
            return -1
        # fecha
        if fecha is None:
            f = datetime.date.today()
        else:
            try:
                f = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
            except:
                print("ERROR: fecha inválida (use AAAA-MM-DD)")
                return -1
        # plazo segun tipo y prioridad
        if tipo == "CERTIFICADO":
            plazo = 5
        elif tipo == "EQUIVALENCIA":
            plazo = 15
        elif tipo == "REINCORPORACION":
            plazo = 10
        elif tipo == "CONSULTA":
            plazo = 3
        if prioridad == "ALTA":
            plazo = plazo // 2
        elif prioridad == "BAJA":
            plazo = plazo + 5
        v = f + datetime.timedelta(days=plazo)
        # persistencia
        d = self.cargar()
        est = None
        for e in d["estudiantes"]:
            if e.legajo == legajo:
                est = e
        if est is None:
            est = Estudiante(legajo, nombre.strip(), email)
            d["estudiantes"].append(est)
        d["ultimo_id"] = d["ultimo_id"] + 1
        nid = d["ultimo_id"]
        s = Solicitud(nid, legajo, tipo, prioridad, "PENDIENTE", descripcion.strip(), f.isoformat(), v.isoformat(), None)
        d["solicitudes"].append(s)
        self.guardar(d)
        print("Solicitud #" + str(nid) + " registrada (tipo=" + tipo + ", prioridad=" + prioridad + ", vence=" + v.isoformat() + ")")
        print("[NOTIFICACIÓN] Email a " + est.email + ": su solicitud #" + str(nid) + " fue registrada")
        return nid

    def alta_responsable(self, nombre, area):
        if nombre is None or nombre.strip() == "" or area is None or area.strip() == "":
            print("ERROR: nombre y área son obligatorios")
            return -1
        d = self.cargar()
        d["ultimo_resp"] = d["ultimo_resp"] + 1
        rid = d["ultimo_resp"]
        r = Responsable(rid, nombre.strip(), area.strip())
        d["responsables"].append(r)
        self.guardar(d)
        print("Responsable #" + str(rid) + " creado: " + r.nombre + " (" + r.area + ")")
        return rid

    def cambiar_estado(self, id, nuevo):
        if nuevo not in ["PENDIENTE", "EN_PROCESO", "RESUELTA", "RECHAZADA", "CERRADA"]:
            print("ERROR: estado inválido: " + nuevo)
            return False
        d = self.cargar()
        s = None
        for x in d["solicitudes"]:
            if x.id == id:
                s = x
        if s is None:
            print("ERROR: solicitud " + str(id) + " no encontrada")
            return False
        viejo = s.estado
        ok = False
        if viejo == "PENDIENTE" and (nuevo == "EN_PROCESO" or nuevo == "RECHAZADA"):
            ok = True
        elif viejo == "EN_PROCESO" and (nuevo == "RESUELTA" or nuevo == "RECHAZADA"):
            ok = True
        elif viejo == "RESUELTA" and nuevo == "CERRADA":
            ok = True
        if not ok:
            print("ERROR: transición no permitida: " + viejo + " -> " + nuevo)
            return False
        if nuevo == "EN_PROCESO" and s.responsable_id is None:
            print("ERROR: la solicitud debe tener un responsable asignado para pasar a EN_PROCESO")
            return False
        s.estado = nuevo
        self.guardar(d)
        print("Solicitud #" + str(id) + ": " + viejo + " -> " + nuevo)
        for e in d["estudiantes"]:
            if e.legajo == s.legajo:
                print("[NOTIFICACIÓN] Email a " + e.email + ": su solicitud #" + str(id) + " cambió a " + nuevo)
        return True

    def asignar_responsable(self, id, rid):
        d = self.cargar()
        s = None
        for x in d["solicitudes"]:
            if x.id == id:
                s = x
        if s is None:
            print("ERROR: solicitud " + str(id) + " no encontrada")
            return 1
        r = None
        for x in d["responsables"]:
            if x.id == rid:
                r = x
        if r is None:
            print("ERROR: responsable " + str(rid) + " no encontrado")
            return 2
        if s.estado == "RESUELTA" or s.estado == "RECHAZADA" or s.estado == "CERRADA":
            print("ERROR: no se puede asignar responsable a una solicitud " + s.estado)
            return 3
        cont = 0
        for x in d["solicitudes"]:
            if x.responsable_id == rid and (x.estado == "PENDIENTE" or x.estado == "EN_PROCESO") and x.id != id:
                cont = cont + 1
        if cont >= 3:
            print("ERROR: el responsable " + r.nombre + " alcanzó el máximo de 3 solicitudes activas")
            return 4
        s.responsable_id = rid
        self.guardar(d)
        print("Solicitud #" + str(id) + " asignada a " + r.nombre + " (" + r.area + ")")
        return 0

    def buscar_por_tipo(self, lst, t):
        res = []
        for x in lst:
            if x.tipo == t:
                res.append(x)
        return res

    def buscar_por_estado(self, lst, e):
        res = []
        for x in lst:
            if x.estado == e:
                res.append(x)
        return res

    def buscar_por_prioridad(self, lst, p):
        res = []
        for x in lst:
            if x.prioridad == p:
                res.append(x)
        return res

    def buscar_por_legajo(self, lst, l):
        res = []
        for x in lst:
            if x.legajo == l:
                res.append(x)
        return res

    def buscar(self, tipo=None, estado=None, prioridad=None, legajo=None):
        d = self.cargar()
        lst = d["solicitudes"]
        if tipo is not None:
            lst = self.buscar_por_tipo(lst, tipo)
        if estado is not None:
            lst = self.buscar_por_estado(lst, estado)
        if prioridad is not None:
            lst = self.buscar_por_prioridad(lst, prioridad)
        if legajo is not None:
            lst = self.buscar_por_legajo(lst, legajo)
        if len(lst) == 0:
            print("Sin resultados.")
            return lst
        for x in lst:
            print("#" + str(x.id) + " | " + x.tipo + " | " + x.prioridad + " | " + x.estado + " | legajo " + x.legajo + " | vence " + x.vence)
        return lst

    def reporte(self, hoy=None):
        if hoy is None:
            h = datetime.date.today()
        else:
            try:
                h = datetime.datetime.strptime(hoy, "%Y-%m-%d").date()
            except:
                print("ERROR: fecha inválida (use AAAA-MM-DD)")
                return -1
        d = self.cargar()
        lst = d["solicitudes"]
        por_estado = {"PENDIENTE": 0, "EN_PROCESO": 0, "RESUELTA": 0, "RECHAZADA": 0, "CERRADA": 0}
        por_tipo = {"CERTIFICADO": 0, "EQUIVALENCIA": 0, "REINCORPORACION": 0, "CONSULTA": 0}
        vencidas = 0
        for x in lst:
            por_estado[x.estado] = por_estado[x.estado] + 1
            por_tipo[x.tipo] = por_tipo[x.tipo] + 1
            if x.estado == "PENDIENTE" or x.estado == "EN_PROCESO":
                if x.vence < h.isoformat():
                    vencidas = vencidas + 1
        print("=== REPORTE DE SOLICITUDES ===")
        print("Total: " + str(len(lst)))
        print("Por estado:")
        for k in por_estado:
            print("  " + k + ": " + str(por_estado[k]))
        print("Por tipo:")
        for k in por_tipo:
            print("  " + k + ": " + str(por_tipo[k]))
        print("Vencidas al " + h.isoformat() + ": " + str(vencidas))
        return 0
