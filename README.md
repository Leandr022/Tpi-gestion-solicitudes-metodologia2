# Sistema de Gestión de Solicitudes Académicas (versión base)

Trabajo Práctico Integrador — Metodología de Sistemas II (TUPaD, UTN).

Aplicación de consola en Python 3 que permite registrar solicitudes de estudiantes,
clasificarlas por tipo, prioridad y estado, asignar responsables, buscar/filtrar y
generar un reporte simple. Los datos se persisten en `datos.json` (datos sintéticos).

## Uso rápido

```bash
python main.py alta-responsable --nombre "Marta Ruiz" --area "Secretaría Académica"
python main.py registrar --legajo 1001 --nombre "Ana Gómez" --email ana@example.com \
    --tipo CERTIFICADO --prioridad ALTA --descripcion "Certificado de alumno regular"
python main.py asignar --id 1 --responsable-id 1
python main.py cambiar-estado --id 1 --estado EN_PROCESO
python main.py buscar --estado EN_PROCESO
python main.py reporte
```

> Este README describe el estado `estado-inicial`. La documentación completa se
> actualiza en el hito `etapa-docs`.
