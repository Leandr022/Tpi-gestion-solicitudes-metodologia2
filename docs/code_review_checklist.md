# Code review profesional (Etapa 7)

**Objeto de la revisión:** repositorio completo en el estado posterior a `etapa-pruebas` (commit 66208f5).
**Herramientas de apoyo:** `flake8`, `radon`, `pytest`, `pytest-cov`, lectura manual del código y pruebas de mutación manual.
**Revisor:** el autor del trabajo, con apoyo de IA (ver `docs/registro_uso_ia.md`). *El estudiante debe repasar cada ítem
por sí mismo antes de entregar y ajustar el resultado a su propio criterio.*

Leyenda: ✔ cumple · ⚠ observación (con acción) · ✖ no cumple.

## 1. Checklist técnico

### A. Diseño (SOLID)
| # | Criterio | Resultado | Evidencia |
|---|---|---|---|
| A1 | Cada módulo/clase tiene una única responsabilidad (SRP) | ✔ | 7 módulos con responsabilidad única; `docs/diagramas/arquitectura_refactorizada.png` |
| A2 | Las reglas de negocio pueden extenderse sin editar condicionales (OCP) | ✔ | Tablas de reglas; `docs/evidencias/demostracion_ocp_salida.txt` |
| A3 | Las dependencias apuntan a abstracciones (DIP) | ✔ | `servicio.py` no importa infraestructura |
| A4 | Las implementaciones son sustituibles por su contrato (LSP) | ✔ | Dobles en memoria en `tests/unit/soporte.py` |
| A5 | Las interfaces son pequeñas (ISP) | ✔ | 2 y 1 método respectivamente |

### B. Clean Code
| # | Criterio | Resultado | Evidencia |
|---|---|---|---|
| B1 | Nombres que revelan intención, sin variables de una letra | ✔ | `flake8` sin advertencias (antes 9) |
| B2 | Funciones cortas y de baja complejidad | ⚠ | Ver CR-03 |
| B3 | Sin duplicación de código | ✔ | Búsquedas y parseo de fecha unificados (R1) |
| B4 | Sin números/cadenas mágicas | ✔ | Enumeraciones y constantes con nombre |
| B5 | Módulos cohesivos y de tamaño razonable | ⚠ | Ver CR-05 |
| B6 | Contratos y precondiciones documentados | ⚠ | Ver CR-04 (corregido) |

### C. Errores y robustez
| # | Criterio | Resultado | Evidencia |
|---|---|---|---|
| C1 | Sin `except:` genéricos ni errores silenciados | ✔ | Búsqueda en el código: 0 ocurrencias |
| C2 | Los errores se informan de forma consistente (excepciones + código de salida) | ✔ | `cli.main` |
| C3 | La corrupción de datos no provoca pérdida silenciosa | ✔ | `cs09_salida_estado-refactorizado.txt` |
| C4 | La escritura de datos es atómica | ✔ | `RepositorioJSON.guardar` (`os.replace`) |
| C5 | Compatibilidad de versión de Python explicitada | ⚠ | Ver CR-07 (corregido) |

### D. Pruebas
| # | Criterio | Resultado | Evidencia |
|---|---|---|---|
| D1 | Las pruebas verifican comportamiento observable y fallan ante defectos | ✔ | Mutación manual: 10/10 detectados por las unitarias |
| D2 | Cobertura adecuada | ✔ | 100 % de sentencias, 99 % de ramas (`cobertura_estado-refactorizado.txt`) |
| D3 | Las pruebas no están acopladas a detalles accidentales | ⚠ | Ver CR-08 (corregido) |
| D4 | Las pruebas son rápidas y aisladas | ✔ | 123 unitarias en 0,2 s; sin archivos reales |

### E. Repositorio y proceso
| # | Criterio | Resultado | Evidencia |
|---|---|---|---|
| E1 | Historial de commits claro y ordenado | ✔ | Commits por hito y por refactoring (`git log --oneline`) |
| E2 | Tags obligatorios presentes | ✔ | `estado-inicial`, `estado-refactorizado`, `etapa-diagnostico`, `etapa-refactoring`, `etapa-pruebas`, `etapa-docs` |
| E3 | README con descripción, instalación/uso, funcionalidades y tecnologías | ✔ | `README.md` |
| E4 | Datos sintéticos, sin datos personales reales | ✔ | Nombres y legajos ficticios en pruebas y ejemplos |
| E5 | Uso de IA declarado con evidencia | ✔ | `docs/registro_uso_ia.md` |

## 2. Observaciones, feedback y acciones

| ID | Observación | Severidad | Acción / decisión | Estado |
|---|---|---|---|---|
| CR-01 | El servicio no recibe el `Notificador`: devuelve la `Notificacion` y la envía la CLI. Se hizo así para conservar el **orden de salida** original (primero «registrada», luego la notificación). | Baja | Decisión de diseño documentada en `decisiones_tecnicas.md` (D2) | Aceptado |
| CR-02 | `buscar` acepta valores desconocidos (devuelve «Sin resultados.»). | Baja | Se mantiene: es comportamiento original fijado por las pruebas de caracterización | Aceptado |
| CR-03 | `DatosSolicitud.validar` tiene complejidad ciclomática 12 (cadena de 9 validaciones). Es la única función con rango C. | Media | Mejora futura: reglas de validación como tabla/lista de funciones | Pendiente |
| CR-04 | `Solicitud.nueva` asume que los datos fueron validados; si no, lanza `ValueError` al construir las enumeraciones. | Media | **Corregido:** precondición documentada en el docstring (commit e97478a) | Cerrado |
| CR-05 | `modelos.py` concentra enumeraciones, objetos de valor, entidades y agregado (286 líneas; mantenibilidad 33,6, la más baja del proyecto). | Baja | Mejora futura: dividir en `enumeraciones.py`, `entidades.py` y `registro.py` | Pendiente |
| CR-06 | Varios manejadores de `cli.py` reciben el parámetro `notificador` sin usarlo, para mantener una firma uniforme en la tabla de comandos. | Baja | Aceptado: se prefirió la uniformidad al polimorfismo adicional | Aceptado |
| CR-07 | `enum.StrEnum` exige Python ≥ 3.11; en versiones anteriores el error sería críptico. | Media | **Corregido:** verificación de versión con mensaje claro en `main.py` y requisito en el README (commit e97478a) | Cerrado |
| CR-08 | La prueba `test_formato_del_reporte` fijaba «14 líneas» y se rompía al agregar un tipo nuevo (detectado al ejecutar la demostración de OCP). | Media | **Corregido:** el valor esperado se calcula a partir de las enumeraciones (commit e045062) | Cerrado |
| CR-09 | `datos.json` se lee y reescribe completo en cada operación y no hay control de concurrencia. | Baja | Fuera de alcance; documentado como deuda aceptada | Aceptado |
| CR-10 | En `cli.py:60` la rama «sin notificación» no está cubierta a nivel CLI (sí a nivel servicio). | Baja | Aceptado: el comportamiento está probado en `test_servicio.py` | Aceptado |

### Hallazgo durante el desarrollo (auto-revisión previa al commit de R3)
En la primera versión de R3, la carga desde archivo dejaba `prioridad` como `str` en lugar de `Prioridad`. Las 50
pruebas de caja negra pasaban (la salida era idéntica), por lo que **solo la lectura crítica del código lo detectó**.
Se corrigió dentro del mismo commit. Es un ejemplo de por qué la revisión humana complementa a las pruebas.

## 3. Criterios de aceptación técnica

El código se considera aceptado cuando:

1. Las 173 pruebas pasan (50 de caracterización + 123 unitarias).
2. `flake8` no informa advertencias.
3. Ninguna función nueva supera complejidad ciclomática 12 y el promedio se mantiene en rango A.
4. La cobertura de sentencias no baja del 95 %.
5. Todo cambio de comportamiento externo está justificado y documentado (único caso: archivo corrupto).
6. Las observaciones de severidad Media o superior están cerradas o tienen una acción planificada
   (CR-03 y CR-05 quedan planificadas como mejoras futuras).

**Resultado:** aceptado, con 2 observaciones de mejora futura (CR-03, CR-05).
