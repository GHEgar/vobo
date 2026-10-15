# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto se adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [No publicado]

### Agregado

- Buzón de avisos: coordinación avisa a quien reportó una falla (mensaje prellenado según su estado) o
  manda avisos libres a varias personas; campana con contador de no leídos y página `/avisos`.
- Entrada directa al proveedor OIDC sin pantalla intermedia, con regreso a la página pedida
  (`/api/auth/login?siguiente=`), protección contra bucles y aviso de sesión cerrada.
- Buscador en la cabecera (`/` o Ctrl+K) sobre secciones, casos, pasos, herramientas y
  procedimientos visibles para cada persona, sin acentos ni mayúsculas; `GET /api/buscar` y
  `/caso/:id?paso=n` para abrir un caso en un paso.
- Desplegable propio para elegir la ronda, reutilizable como `Desplegable`.
- Componentes de telar vendorizados en `frontend/vendor/`: `muestrario`, `abanico`, `plomada` y
  `lanzadera`.

### Cambiado

- El lint del frontend usa `@npmegar/eslint-config` 0.4.0 desde npm (presets `base`, `react` y
  `react-app`) en lugar de una config propia.
- Imagen base del backend a `python:3.14-slim`.
- Íconos de tesela (vendorizada en `frontend/vendor/`) en lugar de los SVG y caracteres dibujados a
  mano: información, cerrar, subir, buscar, chevrons, marca, más y campana.
- Los avisos pasan al menú del avatar, con su contador de no leídos; el avatar muestra un badge con
  el número de avisos sin leer y la campana sale de la cabecera.
- El buscador baja a la fila de páginas, pegado a la derecha; en pantallas chicas queda fijo como
  ícono fuera del área con scroll y despliega el campo sobre la fila.

### Corregido

- Varias peticiones con el token vencido renovaban la sesión a la vez: el proveedor rechazaba el
  refresh token ya rotado, la sesión se cerraba y la persona tenía que volver a entrar (500 con
  `StaleDataError`). Ahora solo una renueva y las demás esperan su resultado.
- El foco del modal saltaba al botón de cerrar en cada render del padre.

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
