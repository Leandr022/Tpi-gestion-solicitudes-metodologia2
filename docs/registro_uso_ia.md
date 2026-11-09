# Registro y declaración del uso de inteligencia artificial

Apartado 7 de la consigna: *«Debe declararse en el informe indicando herramienta utilizada, finalidad y grado de
intervención. Debe adjuntarse evidencia del intercambio relevante.»*

## 1. Declaración

| Aspecto | Declaración |
|---|---|
| **Herramienta** | Claude (Anthropic), modelo Claude Sonnet 5.5, en la aplicación Claude con capacidad de ejecutar código y comandos en un entorno de trabajo aislado |
| **Rol** | **Apoyo y tutoría, y chequeo de información y de funcionalidad.** La IA no decide el alcance ni reemplaza el criterio del estudiante: ayuda a interpretar la consigna, a contrastar datos y a comprobar que el sistema se comporta como se afirma |
| **Finalidad** | (1) **Chequear información:** contrastar la interpretación de la consigna y de la rúbrica; verificar que cada cifra del informe (complejidad, mantenibilidad, advertencias, cobertura) provenga de una herramienta y no de una estimación; controlar referencias de línea y conteos. (2) **Chequear funcionalidad:** comprobar con pruebas que el comportamiento externo se conserva tras cada refactoring, reproducir un defecto antes de darlo por cierto y validar las pruebas con mutación manual. (3) **Apoyo/tutoría:** explicar conceptos (SOLID, code smells, refactorings) y revisar críticamente propuestas. |
| **Grado de intervención (declarado con exactitud)** | Apoyo y chequeo, **con generación de borradores** de código, pruebas y texto que el estudiante debe revisar, comprender, ejecutar y adoptar como propios. El estudiante definió el dominio (Gestión de Solicitudes Académicas), el lenguaje (Python), la modalidad (individual) y el registro académico del informe. Ninguna cifra del informe proviene de la IA sin una ejecución real cuya salida se conserva en `docs/evidencias/`. |
| **Responsabilidad** | La IA no reemplaza la autoría ni la defensa. El estudiante debe poder explicar y modificar todo lo entregado, y el video se realiza con su voz propia (sin voces generadas por IA). |

### Aportes propios del estudiante

- Definí el tema del trabajo (Gestión de Solicitudes Académicas), el lenguaje (Python) y la modalidad individual, y fijé el registro académico del informe.
- Indiqué que el uso de la IA debía declararse y acompañarse de evidencia, y pedí ajustar la declaración y los archivos de evidencia hasta que reflejaran el uso real.
- Creé el repositorio en GitHub, publiqué el código con su historial, renombré la rama a `main`, subí los 6 tags y reorganicé la carpeta de evidencias.
- Realicé consultas a la IA para comprender el código y las evidencias (complejidad ciclomática, `except:` sin tipo y el origen de la pérdida de datos) y para estimar la evaluación según la rúbrica.
- Preparé el video con mi propia voz y cámara, ejecuté demostraciones en la terminal (`git log`, `git tag`) y decidí qué tramos se eliminaban en la edición final.
- Completé y confirmé los datos propios del informe (justificación de modalidad, enlaces del repositorio y del video).

## 2. Evidencia del intercambio relevante

Los archivos están en `docs/evidencias/prompts_ia/` y se transcriben textualmente con fecha y hora reales.

| N.º | Prompt del estudiante (resumen / texto) | Respuesta y resultado de la IA | Evidencia |
|---|---|---|---|
| 1 | Pide una tabla de trazabilidad entre la consigna oficial y el informe, y una lista de requisitos pendientes o parciales. | Entrega la tabla con páginas y evidencias, y señala los puntos pendientes. | `prompt_01_trazabilidad_con_la_consigna.txt` |
| 2 | Pide verificar la sección 3 contra los mínimos de la consigna y contrastar sus cifras con las demás secciones, sin corregir nada sin su verificación. | Confirma los 5 mínimos, contrasta cifras con las evidencias y no modifica ninguna. | `prompt_02_verificacion_del_sistema_base.txt` |
| 3 | Pide verificar el repositorio de GitHub (rama, tags, commits, documentación y ejecución en un clon limpio) sin modificar nada en el remoto. | Verifica en un clon temporal y reporta lo correcto y lo pendiente, con los comandos a ejecutar. | `prompt_03_verificacion_del_repositorio.txt` |
| 4 | Pide contrastar seis posibles inconsistencias del informe con docs/evidencias/, con texto actual y propuesto, sin cambiar cifras no respaldadas. | Verifica contra la evidencia, confirma las correcciones aplicadas y señala dos puntos adicionales a confirmar (MI de R4 y CC de clase vs función). | `prompt_04_consistencia_del_informe.txt` |
| 5 | Pide una revisión independiente del código (checklist A a E; servicio, cli, repositorio y modelos), con observaciones nuevas clasificadas por severidad y línea, sin modificar el código. | Lee el código, lo contrasta con el tag, ejecuta sondeos en una copia temporal e informa 15 observaciones (4 Media, 11 Baja); la decisión de aceptarlas queda al estudiante. | `prompt_05_revision_independiente_del_codigo.txt` |
| 6 | Pide el control final de entrega (índice, repositorio, tags, anexo, bundle, prompts, datos personales y cifras) como checklist con estado, sin modificar nada. | Verifica en copias de solo lectura y entrega el checklist: lo correcto y lo que falta o es dudoso, con el archivo de cada ítem. | `prompt_06_control_final_de_entrega.txt` |
| 7 | Pide ejecutar todos los pendientes del control final para dejar listos el informe y el anexo. | Completa el registro, hace clicables los enlaces, rearma el repositorio con tags y bundle actualizados y regenera informe y anexo. | `prompt_07_cierre_de_pendientes.txt` |

**Otros intercambios de apoyo durante la producción (sin archivo individual).** Además de los anteriores hubo consultas sobre: la presentación en PowerPoint y el guion del video; la unión y el corte del video grabado por el estudiante; la redacción y revisión de la justificación de modalidad; la instalación de Python y la ejecución de las pruebas en Windows; y la publicación de cambios en GitHub (commit, push y tags). No se transcribieron una por una; su resultado se refleja en el repositorio, la presentación y el video.

## 3. Ejemplos reales de apoyo y chequeo (con su evidencia)

Cada ejemplo ocurrió durante este trabajo y se presenta como un **chequeo**: qué se consultó, cómo se comprobó y qué resultado tuvo. Incluyen los errores de la propia IA que el chequeo detectó, porque muestran el criterio aplicado sobre sus resultados.

### 3.1 Chequeo de información

| N.º | Qué se consultó / afirmó | Cómo se comprobó | Resultado | Evidencia |
|---|---|---|---|---|
| E1 | ¿Qué tan complejo y mantenible es el sistema base? | Se midió con `radon` y `flake8` en lugar de aceptar una apreciación | CC 23, MI 17,28 y 9 advertencias, medidos | `metricas_estado-inicial.txt`, `flake8_estado-inicial.txt` |
| E2 | Referencias de línea del diagnóstico (130-136, 244) y cantidad de literales («más de 15») | Se contrastaron con `grep`/`sed` sobre el código real | Corregidas a 131-136 y 246; los literales son 27 | Commit 6e53f39 |
| E3 | Cantidad de responsabilidades de la clase (6 en un documento, 5 en otro) | Se comparó con el diagnóstico y con el diagrama | Unificado en 5 | `docs/refactorings.md` |
| E4 | Una afirmación en un script: «ningún test debe romperse al agregar un tipo» | Se ejecutó la demostración | Fallaban 2 pruebas (las que fijan el texto del reporte); se corrigió la afirmación en lugar de ocultar el resultado | `demostracion_ocp_salida.txt` |

### 3.2 Chequeo de funcionalidad

| N.º | Qué se verificó | Cómo se comprobó | Resultado | Evidencia |
|---|---|---|---|---|
| E5 | Que un archivo corrupto provoque pérdida de datos (sospecha al leer el código) | No se aceptó por lectura: se **reprodujo** con un script contra cada versión | Confirmado en `estado-inicial`; corregido y conservado en la versión final | `cs09_reproduccion.sh`, `cs09_salida_*.txt` |
| E6 | Que R3 preservara el comportamiento | Las 50 pruebas pasaban, pero la **lectura crítica** del diff mostró que `prioridad` quedaba como `str` y no como `Prioridad` | Error detectado antes del commit y corregido | Commit bf731b8; `code_review_checklist.md` |
| E7 | Una prueba unitaria que fijaba «14 líneas» en el reporte | La demostración de OCP la hizo fallar al agregar un tipo | Se derivó el valor de las enumeraciones (CR-08) | Commit e045062 |
| E8 | Que las pruebas realmente detecten defectos | **Mutación manual**: 10 defectos inyectados, uno por vez | Unitarias: 10 de 10; caracterización sola: 7 de 10 | `mutacion_manual.txt` |

### 3.3 Chequeos propios del estudiante

| N.º | Chequeo realizado | Resultado |
|---|---|---|
| P1 | Pedí una estimación de la nota con la rúbrica de la cátedra y contrasté sus puntos débiles (revisión hecha por el mismo autor, conclusiones genéricas, datos pendientes) | Identifiqué lo que faltaba completar antes de entregar |
| P2 | Pedí que se explicara en simple qué demuestra cada archivo de evidencia y formulé tres preguntas: complejidad ciclomática, `except:` sin tipo y la línea que causaba la pérdida de datos | Comprendí que el `except:` desnudo de `cargar` más el modo "w" de `guardar` producía la pérdida de datos |
| P3 | Revisé el repositorio publicado: existencia de `main`, los 6 tags y las carpetas de evidencia | Detecté archivos de prompts movidos o ausentes y tags en un commit anterior, y los corregí |
| P4 | Ensayé la demostración en la terminal (`git log`, `git tag`) y la grabé en el video | Se muestran los commits por etapa y los 6 tags |
| P5 | Revisé el video completo y pedí quitar tramos que quedaban mal en la presentación | Video final de unos 11 minutos |

## 4. Buenas prácticas seguidas

- La IA se usó para apoyar y para **chequear**; las cifras del informe provienen de la ejecución de herramientas, no de estimaciones de la IA.
- Cada refactoring se confirmó solo después de ejecutar la suite completa.
- Los resultados desfavorables (costo en líneas de código, pruebas que no detectan defectos, un test frágil)
  se informan en lugar de omitirse.
- No se usaron datos personales reales: nombres, legajos y correos son ficticios.
