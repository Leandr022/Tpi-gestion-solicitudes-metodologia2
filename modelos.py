class Estudiante:
    def __init__(self, legajo, nombre, email):
        self.legajo = legajo
        self.nombre = nombre
        self.email = email


class Responsable:
    def __init__(self, id, nombre, area):
        self.id = id
        self.nombre = nombre
        self.area = area


class Solicitud:
    def __init__(self, id, legajo, tipo, prioridad, estado, descripcion, fecha, vence, responsable_id):
        self.id = id
        self.legajo = legajo
        self.tipo = tipo
        self.prioridad = prioridad
        self.estado = estado
        self.descripcion = descripcion
        self.fecha = fecha
        self.vence = vence
        self.responsable_id = responsable_id
