# Registro y declaración del uso de inteligencia artificial

Apartado 7 de la consigna: *«Debe declararse en el informe indicando herramienta utilizada, finalidad y grado de
intervención. Debe adjuntarse evidencia del intercambio relevante.»*

## 1. Declaración

| Aspecto | Declaración |
|---|---|
| **Herramienta** | Claude (Anthropic), modelo Claude Sonnet 5.5, en la aplicación Claude con capacidad de ejecutar código y comandos en un entorno de trabajo aislado |
| **Rol** | Asistente técnico de apoyo, bajo la dirección del estudiante |
| **Finalidad** | (1) Interpretar la consigna y ordenar el trabajo en las 8 etapas. (2) Construir el sistema base con defectos de diseño diagnosticables. (3) Medir calidad con herramientas objetivas (`radon`, `flake8`, `pytest`, `pytest-cov`). (4) Proponer y aplicar refactorings, verificándolos con pruebas. (5) Escribir pruebas unitarias y realizar mutación manual. (6) Redactar borradores de la documentación y del informe. |
| **Grado de intervención** | **Alto en la producción de borradores** (código, pruebas y texto) y **bajo en las decisiones de alcance**: el estudiante definió el dominio (Gestión de Solicitudes Académicas), el lenguaje (Python), la modalidad (individual) y el registro académico del informe. Toda afirmación cuantitativa del informe proviene de una ejecución real de herramientas, cuya salida se conserva en `docs/evidencias/`. |
| **Responsabilidad** | La IA no reemplaza la autoría ni la defensa. El estudiante debe comprender, justificar y poder modificar todo lo entregado, y la defensa del video se realiza con su voz propia (sin voces generadas por IA). |

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

## 3. Ejemplos reales de apoyo (con su evidencia)

Ejemplos concretos ocurridos durante este trabajo. Incluyen los **errores de la propia IA detectados y
corregidos**, porque muestran el criterio técnico aplicado sobre sus resultados.

| N.º | Qué aportó la IA | Cómo se verificó / qué se corrigió | Evidencia |
|---|---|---|---|
| E1 | Generó un sistema base funcional con 10 code smells identificables. | Se midió con herramientas (CC 23, MI 17,28, 9 advertencias `flake8`) y se comprobó con 50 pruebas. | `metricas_estado-inicial.txt`, `flake8_estado-inicial.txt` |
| E2 | Detectó que el archivo corrupto provocaba pérdida silenciosa de datos. | No se aceptó por lectura del código: se **reprodujo** con un script y se conservó la salida antes/después. | `cs09_reproduccion.sh`, `cs09_salida_*.txt` |
| E3 | Cometió un error en R3: la carga dejaba `prioridad` como `str` y no como `Prioridad`. | Las 50 pruebas pasaban igualmente; lo detectó la lectura crítica antes del commit y se corrigió. | Commit bf731b8; `code_review_checklist.md` |
| E4 | Escribió una prueba unitaria que fijaba «14 líneas» en el reporte. | La demostración de OCP la hizo fallar al agregar un tipo; se corrigió para derivar el valor de las enumeraciones. | Commit e045062 (CR-08) |
| E5 | Redactó en un script «ningún test debe romperse» al agregar un tipo. | Al ejecutar, fallaban 2 pruebas (las que fijan el texto literal del reporte). Se corrigió la afirmación en lugar de ocultar el resultado. | `demostracion_ocp_salida.txt` |
| E6 | Escribió «6 responsabilidades» en un documento y «5» en otro. | Se contrastó con el diagnóstico y el diagrama y se unificó en 5. | `docs/refactorings.md` |
| E7 | Propuso pruebas unitarias tras el refactoring. | Se validó su calidad con **mutación manual**: detectaron 10 de 10 defectos inyectados, mientras que las de caja negra solas detectaron 7 de 10. | `mutacion_manual.txt` |
| E8 | Corrigió referencias de línea imprecisas del diagnóstico (130-136 → 131-136; 244 → 246) y el conteo de literales (27, no «más de 15»). | Se verificaron con `grep`/`sed` sobre el código real. | Commit 6e53f39 |

## 4. Buenas prácticas seguidas

- Las cifras del informe provienen de la ejecución de herramientas, no de estimaciones de la IA.
- Cada refactoring se confirmó solo después de ejecutar la suite completa.
- Los resultados desfavorables (costo en líneas de código, pruebas que no detectan defectos, un test frágil)
  se informan en lugar de omitirse.
- No se usaron datos personales reales: nombres, legajos y correos son ficticios.
