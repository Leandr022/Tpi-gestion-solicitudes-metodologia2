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

### Aportes propios del estudiante (completar y confirmar antes de entregar)
> Esta sección debe ser redactada por el estudiante con lo que efectivamente hizo (por ejemplo: ejecutó el sistema y
> las pruebas en su equipo, revisó cada refactoring, modificó o amplió código, creó el repositorio en GitHub y subió los
> commits y tags, grabó el video). El grado de intervención declarado debe coincidir con la realidad.

- [ ] Ejecuté el sistema y las 173 pruebas en mi equipo.
- [ ] Revisé y comprendí cada refactoring (R1–R4) y puedo explicarlo.
- [ ] Hice cambios o ampliaciones propias: ______________________________
- [ ] Publiqué el repositorio en GitHub con los tags indicados.
- [ ] Grabé el video con mi propia voz.

## 2. Evidencia del intercambio relevante

Los textos íntegros están en `docs/evidencias/prompts_ia/`.

| N.º | Prompt del estudiante (resumen / texto) | Respuesta y resultado de la IA | Evidencia |
|---|---|---|---|
| 1 | Presenta rol, contexto de la materia, consigna, rúbrica y modelo de presentación; pide lenguaje académico y que se declare el uso de IA «como apoyo/tutoría» con ejemplos reales como evidencia. | Confirma la interpretación de la consigna, propone seguir las 8 etapas y las 11 secciones del informe, y pregunta por sistema, código existente, lenguaje y modalidad. Aclara que la evidencia se generaría durante el trabajo y no se inventaría. | `prompt_01_consigna_y_contexto.txt`, `respuesta_01_resumen.txt` |
| 2 | *«Vamos a usar el sistema de gestion de solicitudes academicas como sugiere la consigna. El codigo no existe, vamos a utilizar Python y la modalidad es Individual»* | Construye el repositorio completo: sistema base (`estado-inicial`), pruebas de caracterización, diagnóstico, refactorings R1–R4, pruebas unitarias, code review, documentación e informe. | Historial de git (`git log`), `docs/` y `docs/evidencias/` |

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

### 3.3 Chequeos propios del estudiante (completar con lo realmente hecho)

> Ejemplos de chequeos que el estudiante puede realizar y registrar aquí **solo si efectivamente los hizo**; no se incluyen como hechos consumados.

| N.º | Chequeo | Cómo registrarlo |
|---|---|---|
| P1 | Ejecutar las 173 pruebas en su equipo y comparar con la salida del informe | Pegar su propia salida de `pytest` y la fecha |
| P2 | Cambiar un valor (por ejemplo, el plazo de CERTIFICADO) y observar qué prueba falla | Anotar el cambio, la prueba que falló y lo que concluyó |
| P3 | Revisar un refactoring (R1 a R4) contra el diff real y verificar que lo entiende | Anotar el `git diff` consultado y una explicación con sus palabras |
| P4 | Contrastar una explicación de la IA (por ejemplo, de LSP) con el material de la cátedra | Anotar la fuente de la cátedra y si coincidió o se corrigió |

## 4. Buenas prácticas seguidas

- La IA se usó para apoyar y para **chequear**; las cifras del informe provienen de la ejecución de herramientas, no de estimaciones de la IA.
- Cada refactoring se confirmó solo después de ejecutar la suite completa.
- Los resultados desfavorables (costo en líneas de código, pruebas que no detectan defectos, un test frágil)
  se informan en lugar de omitirse.
- No se usaron datos personales reales: nombres, legajos y correos son ficticios.
