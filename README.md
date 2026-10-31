# Sistema de Gestión de Solicitudes Académicas

Trabajo Práctico Integrador — **Metodología de Sistemas II** · Tecnicatura Universitaria en Programación (TUPaD), UTN.
Autor: Leandro Nahuel Santagada (legajo 100129, comisión 01) · Modalidad individual.

Aplicación de consola en Python que permite registrar solicitudes de estudiantes, clasificarlas por tipo, prioridad y
estado, asignar responsables, buscar/filtrar y generar un reporte. El objetivo del trabajo **no es agregar
funcionalidad**, sino analizar un sistema existente, diagnosticar su deuda técnica y mejorarlo mediante refactoring
seguro, pruebas y code review.

## Funcionalidades

| Comando | Qué hace |
|---|---|
| `registrar` | Registra una solicitud (valida datos, calcula el vencimiento y notifica al estudiante) |
| `alta-responsable` | Da de alta un responsable de un área |
| `asignar` | Asigna un responsable a una solicitud |
| `cambiar-estado` | Cambia el estado respetando las transiciones permitidas |
| `buscar` | Filtra por tipo, estado, prioridad y/o legajo |
| `reporte` | Totales por estado y tipo, y solicitudes vencidas |

**Reglas de negocio:** vencimiento = plazo base del tipo (CERTIFICADO 5, EQUIVALENCIA 15, REINCORPORACION 10,
CONSULTA 3 días) ajustado por prioridad (ALTA: mitad; MEDIA: igual; BAJA: +5 días). Estados:
`PENDIENTE → EN_PROCESO | RECHAZADA`, `EN_PROCESO → RESUELTA | RECHAZADA`, `RESUELTA → CERRADA`; para pasar a
`EN_PROCESO` se requiere responsable asignado. Un responsable puede tener como máximo 3 solicitudes activas.

## Requisitos e instalación

- **Python 3.11 o superior** (usa `enum.StrEnum`). El sistema no requiere librerías externas.
- Para ejecutar las pruebas y el análisis: `pip install -r requirements-dev.txt`.

## Uso

```bash
python main.py alta-responsable --nombre "Marta Ruiz" --area "Secretaría Académica"
python main.py registrar --legajo 1001 --nombre "Ana Gómez" --email ana@example.com \
    --tipo CERTIFICADO --prioridad ALTA --descripcion "Certificado de alumno regular"
python main.py asignar --id 1 --responsable-id 1
python main.py cambiar-estado --id 1 --estado EN_PROCESO
python main.py buscar --estado EN_PROCESO
python main.py reporte
```

Los datos se guardan en `datos.json` dentro de la carpeta desde la que se ejecuta el comando. Todos los datos de
ejemplo y de prueba son **sintéticos**.

## Estructura

```
main.py                    Punto de entrada
solicitudes/
  modelos.py               Dominio: entidades, enumeraciones, reglas y objetos de valor
  servicio.py              Casos de uso (sin entrada/salida)
  repositorio.py           Contrato de persistencia + implementación JSON
  notificador.py           Contrato de notificación + implementación por consola
  presentacion.py          Formato de texto para el usuario
  cli.py                   Argumentos, composición de dependencias y códigos de salida
  errores.py               ErrorDeDominio
tests/
  test_caracterizacion.py  50 pruebas de caja negra (idénticas antes y después del refactoring)
  unit/                    123 pruebas unitarias y de integración con dobles en memoria
docs/                      Diagnóstico, refactorings, code review, decisiones, uso de IA, evidencias, diagramas
```

## Pruebas y calidad

```bash
pytest                                              # 173 pruebas
pytest tests/unit --cov=solicitudes --cov-branch    # cobertura (100 % sentencias, 99 % ramas)
flake8 --max-line-length=120 main.py solicitudes tests
radon cc -s -a main.py solicitudes                  # complejidad ciclomática
```

## Tags del repositorio

| Tag | Hito |
|---|---|
| `estado-inicial` | Entrega del sistema base, **sin refactorizar** |
| `etapa-diagnostico` | Diagnóstico de calidad, deuda técnica y code smells |
| `etapa-refactoring` | Refactorings R1–R4 aplicados |
| `etapa-pruebas` | Suite de pruebas, cobertura y mutación manual |
| `etapa-docs` | Documentación final y code review |
| `estado-refactorizado` | Estado final del código |

Para comparar el antes y el después:

```bash
git checkout estado-inicial      # versión base (archivos main.py, gestor.py, modelos.py)
git checkout estado-refactorizado
git diff estado-inicial estado-refactorizado --stat
```

> Las pruebas de `tests/test_caracterizacion.py` se agregaron después de `estado-inicial`; para ejecutarlas sobre esa
> versión, copiar la carpeta `tests/` desde `estado-refactorizado` (no dependen de la estructura interna).

## Resultados principales

| Indicador | `estado-inicial` | `estado-refactorizado` |
|---|---|---|
| Complejidad ciclomática promedio | 6,5 (B) | 2,2 (A) |
| Método más complejo | 23 (D) | 12 (C, solo validación) |
| Mantenibilidad del peor módulo | 17,28 (B) | 33,56 (A) |
| Advertencias `flake8` | 9 | 0 |
| Pruebas automatizadas | 0 | 173 (cobertura 100 % / 99 % ramas) |
| Pérdida de datos ante `datos.json` corrupto | **Sí (silenciosa)** | No (se informa y se conserva) |

## Documentación (`docs/`)

- `diagnostico.md` — calidad externa vs. interna, 10 code smells y trazabilidad.
- `refactorings.md` — SOLID, Clean Code y refactorings con evidencia antes/después.
- `code_review_checklist.md` — checklist aplicado, observaciones y criterios de aceptación.
- `decisiones_tecnicas.md` — decisiones de diseño y alternativas descartadas.
- `registro_uso_ia.md` — declaración y evidencia del uso de IA.
- `guion_video.md` — guía para el video de defensa.
- `evidencias/` — salidas reales de pruebas, métricas, cobertura, mutación y demostraciones reproducibles.
- `diagramas/` — arquitectura antes y después (Graphviz).

## Uso de inteligencia artificial

Se utilizó Claude (Anthropic) como asistente técnico de apoyo. La declaración completa (herramienta, finalidad y
grado de intervención) y la evidencia del intercambio están en [`docs/registro_uso_ia.md`](docs/registro_uso_ia.md).
