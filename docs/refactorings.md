# Aplicación de SOLID y Clean Code, y refactorings documentados (Etapas 4 y 5)

Cada refactoring se aplicó en un commit propio y se verificó ejecutando las **mismas 50 pruebas de
caracterización** (caja negra, sobre la línea de comandos) antes de confirmarlo. El hito en git es el tag
`etapa-refactoring`.

## 1. Progresión medida por refactoring

Fuente: `docs/evidencias/progresion_por_refactoring.txt` (herramientas `radon` y `pytest`).

| Versión (commit) | CC promedio | CC máxima (bloque) | Bloques con CC ≥ C | Mantenibilidad del peor módulo | SLOC | Pruebas de caracterización |
|---|---|---|---|---|---|---|
| `estado-inicial` (a4f71fc) | 6,5 (B) | 23 | 4 | 17,28 (`gestor.py`, B) | 314 | 50 de 50 |
| R1 Extract Method (2a228ea) | 3,7 (A) | 12 | 2 | 28,26 (`gestor.py`) | 334 | 50 de 50 |
| R2 Introduce Parameter Object (0549435) | 3,5 (A) | 12 | 2 | 28,02 (`gestor.py`) | 359 | 50 de 50 |
| R3 Move Method / Replace Conditional (bf731b8) | 3,0 (A) | 13 | 3 | 35,04 (`gestor.py`) | 413 | 50 de 50 |
| R4 Extract Class / Replace Error Code (1f646f3) | 2,2 (A) | 13 | 2 | 33,60 (`modelos.py`) | 463 | 50 de 50 |

*CC = complejidad ciclomática; SLOC = líneas de código fuente.* La columna de CC máxima cuenta bloques (clases y métodos): el 13 de R3/R4 corresponde a la
clase `DatosSolicitud` y su método `validar` mide 12 (cadena de validaciones, no lógica de negocio); se registra como mejora futura. Los SLOC de R4 (463) corresponden al commit `1f646f3`; el estado final mide 465 por ajustes posteriores. Del mismo modo, la mantenibilidad de `modelos.py` en el commit `1f646f3` es 33,60 (`progresion_por_refactoring.txt`) y en el estado final 33,56 (`metricas_estado-refactorizado.txt`).

**Costo del refactoring.** El código fuente creció de 314 a 465 SLOC en el estado final (≈ +48 %): más archivos, docstrings y
estructuras explícitas. El beneficio no está en tener menos líneas, sino en que cada una es más simple, está
donde corresponde y puede probarse de forma aislada.

---

## 2. Refactorings aplicados (≥ 4 documentados)

### R1 — Extract Method (+ Replace Magic Number with Symbolic Constant + Rename Variable)

**Smells atendidos:** CS-02 (Long Method), CS-04 (código duplicado), CS-05 (números/cadenas mágicas), CS-10 (nombres).
**Principios:** Clean Code — funciones pequeñas y de un solo nivel de abstracción; DRY.

*Antes* (`estado-inicial`, `registrar_solicitud`: 63 líneas, complejidad 23). Validación, cálculo de plazo,
acceso a datos y mensajes en un solo método:

```python
def registrar_solicitud(self, legajo, nombre, email, tipo, prioridad, descripcion, fecha=None):
    # validaciones
    if legajo is None or legajo == "" or not legajo.isdigit():
        print("ERROR: legajo inválido")
        return -1
    ...
    if tipo == "CERTIFICADO":
        plazo = 5
    elif tipo == "EQUIVALENCIA":
        plazo = 15
    ...
    d = self.cargar()
    est = None
    for e in d["estudiantes"]:
        if e.legajo == legajo:
            est = e
```

*Después* (commit R1): el método principal se lee como una secuencia de pasos con nombre.

```python
def registrar_solicitud(self, legajo, nombre, email, tipo, prioridad, descripcion, fecha=None):
    error = self._validar_datos_de_registro(legajo, nombre, email, tipo, prioridad, descripcion)
    if error:
        print(error)
        return -1
    fecha_alta = self._resolver_fecha(fecha)
    ...
    vencimiento = fecha_alta + datetime.timedelta(days=self._calcular_plazo_en_dias(tipo, prioridad))
    datos = self.cargar()
    estudiante = self._obtener_o_crear_estudiante(datos, legajo, nombre, email)
```

Métodos extraídos: `_validar_datos_de_registro`, `_calcular_plazo_en_dias`, `_resolver_fecha` (elimina la
duplicación entre *registrar* y *reporte*), `_buscar_solicitud` / `_buscar_responsable` / `_buscar_estudiante`
(eliminan los bucles repetidos), `_filtrar_por` (reemplaza los cuatro métodos `buscar_por_*`),
`_transicion_permitida`, `_contar_por`, `_imprimir_reporte`.
Las cadenas y números literales pasaron a constantes con nombre (`MAX_SOLICITUDES_ACTIVAS`,
`PLAZO_BASE_EN_DIAS`, `ESTADOS_ACTIVOS`, …) y las variables de una letra (`d`, `x`, `e`, `s`) a nombres que
revelan intención (`datos`, `solicitud`, `estudiante`).

**Resultado medido:** complejidad máxima 23 → 12; mantenibilidad de `gestor.py` 17,28 → 28,26.
**Verificación:** 50/50 pruebas de caracterización en verde.

---

### R2 — Introduce Parameter Object

**Smell atendido:** CS-03 (Long Parameter List / Data Clump). **Principio:** Clean Code — pocos parámetros.

*Antes:* `registrar_solicitud(legajo, nombre, email, tipo, prioridad, descripcion, fecha)` (7 parámetros
sueltos) y `buscar(tipo, estado, prioridad, legajo)` (4 filtros sueltos).

*Después:* se crean los objetos inmutables `DatosSolicitud` y `CriteriosBusqueda`.

```python
@dataclass(frozen=True)
class DatosSolicitud:
    legajo: str
    nombre: str
    email: str
    tipo: str
    prioridad: str
    descripcion: str
    fecha: Optional[str] = None

def registrar_solicitud(self, datos_solicitud): ...
def buscar(self, criterios): ...
```

**Beneficio:** el grupo de datos que siempre viaja junto tiene un nombre y un lugar para alojar su
comportamiento (en R3 se le incorpora la validación). **Verificación:** 50/50 pruebas en verde.

---

### R3 — Move Method (+ Replace Conditional with Table + enumeraciones)

**Smells atendidos:** CS-05, CS-06 (cadenas condicionales, viola OCP), CS-07 (Feature Envy / modelo anémico).
**Principios:** OCP, cohesión («Tell, Don't Ask»).

*Antes* — el gestor «le pregunta» al estado y decide por la solicitud:

```python
viejo = s.estado
ok = False
if viejo == "PENDIENTE" and (nuevo == "EN_PROCESO" or nuevo == "RECHAZADA"):
    ok = True
elif viejo == "EN_PROCESO" and (nuevo == "RESUELTA" or nuevo == "RECHAZADA"):
    ok = True
elif viejo == "RESUELTA" and nuevo == "CERRADA":
    ok = True
```

*Después* — la regla vive en el dominio como una tabla, y la solicitud se responsabiliza de su propio cambio:

```python
_TRANSICIONES_PERMITIDAS = {
    Estado.PENDIENTE: (Estado.EN_PROCESO, Estado.RECHAZADA),
    Estado.EN_PROCESO: (Estado.RESUELTA, Estado.RECHAZADA),
    Estado.RESUELTA: (Estado.CERRADA,),
    Estado.RECHAZADA: (),
    Estado.CERRADA: (),
}

class Estado(StrEnum):
    def puede_pasar_a(self, estado_nuevo):
        return estado_nuevo in _TRANSICIONES_PERMITIDAS[self]
```

Movimientos realizados: validación de datos → `DatosSolicitud`; cálculo del plazo → `Tipo` / `Prioridad`;
transiciones y vencimiento → `Estado` / `Solicitud`; capacidad del responsable → `Responsable`.
Los literales de cadena se reemplazaron por las enumeraciones `Tipo`, `Prioridad` y `Estado`.

**Defecto detectado en la auto-revisión previa al commit:** la carga desde archivo dejaba `prioridad` como
`str` en lugar de `Prioridad`. Las pruebas de caja negra no podían advertirlo (la salida era idéntica);
se corrigió antes de confirmar.
**Verificación:** 50/50 pruebas en verde. Demostración de OCP: ver Sección 6.

---

### R4 — Extract Class (+ Replace Error Code with Exception)

**Smells atendidos:** CS-01 (God Class), CS-08 (E/S mezclada con lógica; acoplamiento a la infraestructura),
CS-09 (manejo de errores). **Principios:** SRP, DIP.

La clase `GestorSolicitudes` se dividió en módulos con una única responsabilidad (ver
`docs/diagramas/arquitectura_refactorizada.png`):

| Módulo | Responsabilidad única |
|---|---|
| `modelos.py` | Reglas y datos del dominio |
| `servicio.py` | Casos de uso (orquestación), sin entrada/salida |
| `repositorio.py` | Persistencia (contrato `RepositorioDeRegistro` + implementación JSON) |
| `notificador.py` | Notificaciones (contrato `Notificador` + implementación por consola) |
| `presentacion.py` | Formato de texto para el usuario |
| `cli.py` | Interpretación de argumentos, composición de dependencias y códigos de salida |
| `errores.py` | `ErrorDeDominio` |

Los códigos de retorno heterogéneos (`-1`, `False`, `0..4`) se reemplazaron por excepciones:

```python
# Antes
if s is None:
    print("ERROR: solicitud " + str(id) + " no encontrada")
    return 1
...
# Después (servicio.py)
raise ErrorDeDominio(f"solicitud {id_solicitud} no encontrada")
# cli.py: captura el error y lo traduce a "ERROR: ..." y código de salida 1
```

**Cambio de comportamiento deliberado (único).** Los `except:` genéricos hacían que un `datos.json`
corrupto se reemplazara en silencio por un registro vacío (pérdida de datos, comprobada en
`docs/evidencias/cs09_salida_estado-inicial.txt`). Ahora se informa
`ERROR: el archivo de datos está corrupto` y el archivo se conserva intacto
(`docs/evidencias/cs09_salida_estado-refactorizado.txt`). Es una *mejora* del comportamiento externo, no
cubierta por las pruebas de caracterización porque el comportamiento original era un defecto. Además la
escritura pasó a ser atómica (archivo temporal + `os.replace`).

**Verificación:** 50/50 pruebas de caracterización en verde sobre la nueva estructura (salida, códigos de
salida y contenido de `datos.json` idénticos al resultado de referencia).

---

### Otras técnicas aplicadas

| Técnica | Dónde |
|---|---|
| Replace Magic Number with Symbolic Constant | R1 (constantes) y R3 (tablas y enumeraciones) |
| Rename Variable / Rename Method | R1 |
| Replace Conditional with Table (polimorfismo por datos) | R3: `_PLAZO_BASE_EN_DIAS`, `_AJUSTES_DE_PLAZO`, `_TRANSICIONES_PERMITIDAS` |
| Replace Error Code with Exception | R4 |
| Introduce Factory Method (estático) | `Solicitud.nueva`, `Responsable.nuevo` |

---

## 3. Aplicación de los principios SOLID

| Principio | Aplicación en el sistema | Evidencia |
|---|---|---|
| **SRP** | La God Class (5 responsabilidades mezcladas) se dividió en 7 módulos con un único motivo de cambio cada uno. | Diagrama de arquitectura; R4 |
| **OCP** | Los plazos, ajustes por prioridad y transiciones son **tablas de datos**. Agregar un tipo de solicitud (`BECA`) requirió modificar **2 líneas** (un miembro de la enumeración y una entrada de la tabla) y fue reconocido por la validación, el registro y el reporte sin tocar lógica. | `docs/evidencias/demostracion_ocp.sh` y `demostracion_ocp_salida.txt` |
| **LSP** | `RepositorioJSON` y `RepositorioEnMemoria` (doble de prueba) son intercambiables como `RepositorioDeRegistro` para el servicio; lo mismo ocurre con `NotificadorConsola` y `NotificadorEnMemoria` como `Notificador`. | `tests/unit/test_servicio.py`, `test_cli_y_presentacion.py` |
| **ISP** | Los contratos son mínimos: `RepositorioDeRegistro` (`cargar`, `guardar`) y `Notificador` (`notificar`). Los clientes ya no dependen de una clase con 12 métodos. | `repositorio.py`, `notificador.py` |
| **DIP** | `servicio.py` no importa ningún módulo de infraestructura: recibe el repositorio por inyección. Solo `cli.py` (raíz de composición) conoce las implementaciones concretas. | Diagrama; `servicio.py` |

**Alcance honesto.** LSP e ISP se aplican a los dos contratos del sistema; no hay jerarquías de herencia entre
entidades, por lo que no se fuerzan ejemplos adicionales. Limitación de DIP: el servicio usa el repositorio
mediante *duck typing* (Python no obliga a importar la abstracción); el contrato se hace explícito con la
clase abstracta `RepositorioDeRegistro`.

## 4. Aplicación de Clean Code

| Práctica | Evidencia |
|---|---|
| Nombres que revelan intención | `datos`, `solicitud`, `estado_anterior`, `contar_solicitudes_activas`; `flake8` pasó de 9 advertencias a 0 |
| Funciones pequeñas | Complejidad promedio 6,5 → 2,2; CC máxima 23 → 12 |
| Sin números ni cadenas mágicas | Enumeraciones y tablas en `modelos.py` |
| Manejo de errores con excepciones | `ErrorDeDominio`; sin `except:` genéricos |
| Separación entre lógica y presentación | `presentacion.py`; el servicio no imprime |
| Pocos parámetros | Parameter Objects (R2) |
| Comentarios que explican el porqué | Docstrings de contratos y de decisiones (p. ej. precondición de `Solicitud.nueva`) |
