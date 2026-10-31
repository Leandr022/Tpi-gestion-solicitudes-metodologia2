# Decisiones técnicas

Registro breve de las decisiones de diseño y proceso, con su justificación y las alternativas descartadas.

## D1 — Pruebas de caracterización de caja negra sobre la línea de comandos
**Decisión.** Antes de refactorizar se escribieron 50 pruebas que ejecutan `main.py` como lo haría un usuario y
verifican salida estándar, código de salida y contenido de `datos.json`. Incluyen una comparación contra un
resultado de referencia (*golden master*) generado a partir de `estado-inicial`.
**Justificación.** Un refactoring exige probar el comportamiento externo, no la estructura interna. Al apoyarse
solo en la interfaz de usuario, las mismas pruebas se ejecutan **sin modificaciones** sobre la versión inicial,
sobre cada paso intermedio y sobre la versión final.
**Alternativa descartada.** Pruebas unitarias sobre `GestorSolicitudes`: habrían quedado obsoletas con el primer
cambio de firma (R2).
**Límite reconocido.** Las pruebas de caracterización fijan también comportamientos accidentales y dejan huecos
(la mutación manual mostró que no detectan 3 de 10 defectos inyectados); por eso se complementan con pruebas
unitarias tras el refactoring.

## D2 — El servicio devuelve las notificaciones; la CLI las envía
**Decisión.** `ServicioSolicitudes` devuelve un objeto `Notificacion` y es la CLI quien primero muestra el
resultado («Solicitud #1 registrada…») y después invoca al `Notificador`.
**Justificación.** La versión inicial imprimía primero el resultado y luego la notificación. Si el servicio
enviara la notificación, el orden de salida se invertiría y se alteraría el comportamiento externo.
**Consecuencia.** El servicio queda libre de entrada/salida; el `Notificador` sigue siendo intercambiable
(probado con `NotificadorEnMemoria`).

## D3 — Enumeraciones `StrEnum` y tablas de reglas
**Decisión.** `Tipo`, `Prioridad` y `Estado` son `StrEnum`; plazos, ajustes y transiciones se declaran como
tablas.
**Justificación.** Eliminan cadenas mágicas y cadenas `if/elif` (OCP) y siguen comparándose y serializándose
como texto, de modo que el formato de `datos.json` no cambia.
**Costo.** Requiere Python ≥ 3.11 (verificado en `main.py` y documentado en el README).
**Alternativa descartada.** Clases con herencia (patrón *Strategy* clásico) para cada tipo: más código para
reglas que son solo datos.

## D4 — Único cambio deliberado de comportamiento: archivo de datos corrupto
**Decisión.** Un `datos.json` ilegible o incompleto ya no se reemplaza en silencio por un registro vacío: se
informa `ERROR: el archivo de datos está corrupto` y el archivo se conserva.
**Justificación.** Evita la pérdida silenciosa de datos comprobada en `estado-inicial` (CS-09). Es una mejora,
permitida por la consigna («se mantiene o mejora»), y no se oculta: está documentada y probada
(`tests/unit/test_repositorio_json.py`).

## D5 — Escritura atómica del archivo de datos
**Decisión.** Se escribe en `datos.json.tmp` y luego `os.replace`.
**Justificación.** Una interrupción durante el guardado ya no puede dejar un archivo truncado (resuelve la
observación (i) de deuda aceptada del diagnóstico). No cambia el formato.

## D6 — Parameter Objects inmutables
**Decisión.** `DatosSolicitud` y `CriteriosBusqueda` son `dataclass(frozen=True)`.
**Justificación.** Agrupan datos que viajan juntos, evitan modificaciones accidentales y alojan comportamiento
propio (`validar`, `coincide_con`).

## D7 — Reloj inyectable
**Decisión.** `ServicioSolicitudes` recibe `reloj` (por defecto `datetime.date.today`).
**Justificación.** Permite probar el comportamiento «sin fecha explícita» de forma determinista, sin depender
de la fecha real del sistema.

## D8 — Patrones y alcance
Se aplicaron *Repository* (persistencia detrás de un contrato), *Parameter Object* (R2), métodos de fábrica
estáticos (`Solicitud.nueva`, `Responsable.nuevo`) y una arquitectura de puertos y adaptadores
(`RepositorioDeRegistro`/`RepositorioJSON`, `Notificador`/`NotificadorConsola`). No se incorporaron patrones
GoF adicionales (por ejemplo *Observer* para las notificaciones) porque el dominio no lo justifica: se evitó el
sobrediseño para no agregar complejidad sin beneficio medible.

## D9 — Deuda técnica aceptada (fuera de alcance)
Lectura y reescritura completa del archivo en cada operación, ausencia de control de concurrencia, validación
de entrada en una cadena de condicionales (`DatosSolicitud.validar`, CR-03) y módulo `modelos.py` extenso
(CR-05). Documentadas en `docs/code_review_checklist.md`.
