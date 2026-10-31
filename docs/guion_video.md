# Guía para el video de defensa y demostración (10 a 15 minutos)

> Guía de **puntos a cubrir**, no un texto para leer: la consigna exige voz propia, cámara encendida y que se
> muestren rostro y nombre completo. Explicá cada punto con tus palabras; si algo no lo podés explicar, volvé a
> estudiarlo antes de grabar (la cátedra puede pedir defensa individual).

| Minutos | Sección | Qué decir | Qué mostrar |
|---|---|---|---|
| 0:00–0:45 | 1. Presentación | Nombre completo, legajo, comisión, materia, modalidad individual | Cámara encendida |
| 0:45–2:00 | 2. Sistema base | Dominio, actores, 6 operaciones, reglas (plazos, estados, límite de 3), tecnología | `git checkout estado-inicial`; ejecutar un flujo corto (`registrar` → `asignar` → `cambiar-estado` → `reporte`) |
| 2:00–4:00 | 3. Diagnóstico | Calidad externa (funciona) vs. interna (frágil); métricas | `docs/evidencias/metricas_estado-inicial.txt` (CC 23, MI 17,28); diagrama `arquitectura_inicial.png` |
| 4:00–6:00 | 4. Code smells | Mostrar 4 o 5 con código real: God Class, Long Method, duplicación, mágicos, `except:` genérico | `gestor.py` en `estado-inicial`; **reproducir CS-09** con `bash docs/evidencias/cs09_reproduccion.sh` (pérdida de datos) |
| 6:00–9:00 | 5. SOLID, Clean Code y refactoring | R1 Extract Method, R2 Parameter Object, R3 Move Method/tabla, R4 Extract Class/excepciones; qué principio resuelve cada uno | `git log --oneline`; comparar `registrar_solicitud` antes/después; diagrama `arquitectura_refactorizada.png`; demo OCP (`bash docs/evidencias/demostracion_ocp.sh`) |
| 9:00–11:30 | 6. Pruebas | Por qué caja negra antes de refactorizar; golden master; unitarias después; mutación manual (10/10 vs. 7/10) | `pytest` (173 en verde); cobertura; `docs/evidencias/mutacion_manual.txt` |
| 11:30–13:00 | 7. Code review | Checklist, observaciones (CR-04, CR-07, CR-08 corregidas), criterios de aceptación | `docs/code_review_checklist.md` |
| 13:00–14:30 | 8. Conclusiones | Aprendizajes, dificultades, límites (costo en líneas de código, deuda aceptada), mejoras futuras (CR-03, CR-05); **declarar el uso de IA** | `docs/registro_uso_ia.md` |

**Recordatorios**
- Aclará en el video qué parte hiciste vos y cómo usaste la IA (debe coincidir con `docs/registro_uso_ia.md`).
- Incluí el enlace al video dentro del PDF y cargalo en la plataforma, junto con PDF + repositorio + ZIP.
- Probá todos los comandos antes de grabar; para comparar versiones usá los tags del repositorio.
