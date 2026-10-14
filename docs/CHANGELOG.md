# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto se adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [0.1.0] - 2026-10-14

### Agregado

- Casos guiados paso a paso con su animación, resultado Pasa / Falla / No pude probarlo y
  comentarios por paso.
- Reporte de fallas con datos automáticos y capturas de hasta 5 MB.
- Tablero de coordinación por persona, familia y proyecto; bandeja de fallas; rondas y asignaciones.
- Recomendación y decisión por herramienta, aprobaciones por herramienta y por característica, y acta
  imprimible o en Markdown.
- Instancia personalizable: contenido en `CONTENIDO_DIR` con `instancia.yaml`, tema en `TEMA_DIR` y
  `GET /api/instancia`.
- Inicio de sesión con cualquier proveedor OpenID Connect (discovery, PKCE, RS256) y permisos por
  endpoint o por claim; modo local de usuarios de prueba solo en desarrollo.
- Token de solo lectura para consultar fallas, tablero, herramientas, aprobaciones y comentarios.
- Contenido de ejemplo en `ejemplo/contenido`.
