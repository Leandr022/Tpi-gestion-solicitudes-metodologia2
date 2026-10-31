# Diagnóstico de calidad del sistema base (`estado-inicial`)

Metodología de Sistemas II — TPI. Sistema de Gestión de Solicitudes Académicas.

## 1. Calidad externa vs. calidad interna

### 1.1 Calidad externa (lo que percibe el usuario)

Desde la perspectiva del usuario, la versión inicial **funciona correctamente**: las 50 pruebas de
caracterización automatizadas se ejecutan en verde (`docs/evidencias/pruebas_estado-inicial.txt`) y
cubren las seis operaciones del sistema (registrar, alta de responsable, asignar, cambiar estado,
buscar/filtrar y reportar), las reglas de negocio (plazos por tipo y prioridad, máquina de estados,
límite de tres solicitudes activas por responsable) y los mensajes de error.

### 1.2 Calidad interna (lo que percibe el equipo que mantiene el código)

La estructura interna, en cambio, dificulta la evolución del sistema. Las métricas medidas con
`radon` y `flake8` (`docs/evidencias/metricas_estado-inicial.txt` y `flake8_estado-inicial.txt`) lo
evidencian:

| Indicador | Valor medido | Lectura |
|---|---|---|
| Complejidad ciclomática de `registrar_solicitud` | **23 (rango D)** | Método difícil de entender y de probar |
| Complejidad ciclomática de `cambiar_estado` / `asignar_responsable` | 18 (C) / 16 (C) | Lógica de reglas entremezclada |
| Complejidad promedio | 6,5 (B) | Distribución desigual: concentrada en una sola clase |
| Índice de mantenibilidad de `gestor.py` | **17,28 (rango B)** | Un solo archivo concentra el 73 % del código |
| Líneas de código (`gestor.py`) | 257 de 351 totales | Clase con exceso de responsabilidades |
| Advertencias `flake8` | 9 (3 × E722, 4 × E501, 1 × E741, 1 × E712) | Excepciones genéricas, líneas largas y nombres ambiguos |

**Relación con la evolución futura.** Agregar un nuevo tipo de solicitud, cambiar la política de
plazos, reemplazar el archivo JSON por una base de datos o enviar notificaciones reales por correo
electrónico exigiría modificar `gestor.py` en múltiples puntos (violación de OCP y DIP), con alto
riesgo de regresiones. La calidad externa actual es, por lo tanto, *frágil*: depende de una
estructura interna que encarece cada cambio.

## 2. Registro de deuda técnica y code smells

**Criterio de priorización.** *Impacto* (efecto sobre la mantenibilidad) y *riesgo* (probabilidad de
defectos o pérdida de datos al modificar) se combinan en una prioridad de corrección:
**Alta** (corregir en esta iteración), **Media** (corregir si el esfuerzo es razonable), **Baja**.

| ID | Code smell / debilidad | Evidencia y ubicación | Impacto | Riesgo de mantenimiento | Prioridad |
|---|---|---|---|---|---|
| CS-01 | **Large Class / God Class** (viola SRP) | `GestorSolicitudes` (`gestor.py:11-256`) reúne persistencia, validación, reglas de negocio, notificaciones y presentación por consola en 12 métodos | Alto: cualquier cambio toca la misma clase | Alto: efectos colaterales entre funcionalidades | **Alta** |
| CS-02 | **Long Method** | `registrar_solicitud` (`gestor.py:40-102`): 63 líneas, complejidad 23 (D), con validación, cálculo de plazo, acceso a datos, persistencia y mensajes | Alto: difícil de leer y probar | Alto | **Alta** |
| CS-03 | **Long Parameter List** / Data Clump | `registrar_solicitud` recibe 7 parámetros (`gestor.py:40`); `Solicitud.__init__` recibe 9 (`modelos.py:16`); `buscar` recibe 4 filtros sueltos (`gestor.py:210`) | Medio: llamadas propensas a errores de orden | Medio | **Alta** |
| CS-04 | **Duplicated Code** | (a) Búsqueda de una solicitud por id repetida en `gestor.py:122-125` y `153-156`; (b) cuatro métodos `buscar_por_*` casi idénticos (`gestor.py:182-208`); (c) análisis de fecha duplicado (`gestor.py:66-71` y `231-236`) | Medio: un error se corrige en varios sitios | Medio-Alto | **Alta** |
| CS-05 | **Magic Numbers / Magic Strings** | Plazos `5, 15, 10, 3` (`gestor.py:73-80`), límite `3` (`gestor.py:174`), y los literales de estado (`"PENDIENTE"`, `"CERRADA"`, etc.) repetidos 27 veces en `gestor.py` | Medio: un error tipográfico no se detecta hasta ejecutar | Alto: cambios silenciosos | **Alta** |
| CS-06 | **Switch Statements / cadenas condicionales** (viola OCP) | Plazos por tipo y prioridad (`gestor.py:73-84`); transiciones de estado (`gestor.py:131-136`) | Alto: agregar un tipo o estado obliga a editar código existente | Alto | **Alta** |
| CS-07 | **Feature Envy + modelo de dominio anémico** | El gestor lee y modifica `s.estado`, `s.responsable_id`, `x.vence` (`gestor.py:116-179`, `242-246`); las clases de `modelos.py` solo contienen atributos y ningún comportamiento | Alto: la lógica de dominio no está donde corresponde | Medio | **Alta** |
| CS-08 | **Mezcla de entrada/salida con lógica y acoplamiento a la infraestructura** (viola SRP y DIP) | `print` dentro de la lógica (`gestor.py:43-101`, `145-148`, `248-256`); archivo fijo mediante constante global `RUTA` (`gestor.py:8`) y notificación fija por consola | Alto: imposible probar o reemplazar la persistencia/notificación sin tocar la lógica | Alto | **Alta** |
| CS-09 | **Manejo de errores deficiente** | Códigos de retorno heterogéneos (`-1`, `False`, `0..4`) y tres `except:` genéricos (`gestor.py:20`, `69`, `234`). Si `datos.json` está corrupto, `cargar()` devuelve datos vacíos y la siguiente operación **sobrescribe el archivo**, con pérdida silenciosa de información | Alto | **Alto (integridad de datos)** | **Alta** |
| CS-10 | **Nombres poco expresivos / Primitive Obsession** | Variables `d`, `x`, `e`, `s`, `r`, `f`, `v`, `h`, `lst`, `cont`, y el parámetro `l` (flake8 E741); fechas manipuladas como cadenas ISO y comparadas como texto (`gestor.py:246`) | Medio: reduce la legibilidad | Medio | Media |

**Observaciones adicionales (deuda aceptada).** (i) La escritura de `datos.json` no es atómica
(`gestor.py:28-37`): una interrupción durante el guardado podría truncar el archivo; (ii) no existe
protección frente a ejecuciones concurrentes; (iii) el archivo se lee y reescribe completo en cada
operación. Estos puntos se documentan como mejoras futuras, ya que exceden el alcance acotado del
trabajo.

## 3. Trazabilidad: diagnóstico → principio → refactoring

| Smell | Principio / práctica asociada | Refactoring previsto |
|---|---|---|
| CS-01, CS-08 | SRP, DIP | **Extract Class** (repositorio, notificador, presentación, servicio) |
| CS-02 | Clean Code: funciones pequeñas y de un solo nivel de abstracción | **Extract Method** |
| CS-03 | Clean Code: pocos parámetros | **Introduce Parameter Object** |
| CS-04 | DRY | **Extract Method** / unificación mediante criterios de búsqueda |
| CS-05 | Clean Code: constantes con nombre | **Replace Magic Number with Symbolic Constant** / enumeraciones |
| CS-06 | OCP | **Replace Conditional with Table / Polymorphism** |
| CS-07 | Cohesión (Tell, Don't Ask) | **Move Method** |
| CS-09 | Clean Code: excepciones en lugar de códigos de error | **Replace Error Code with Exception** |
| CS-10 | Clean Code: nombres que revelan intención | **Rename Variable** |
