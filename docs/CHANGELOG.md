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
- Buscador en la cabecera (ñ o Ctrl+K) sobre secciones, casos, pasos, herramientas y
  procedimientos visibles para cada persona, sin acentos ni mayúsculas; `GET /api/buscar` y
  `/caso/:id?paso=n` para abrir un caso en un paso.
- Desplegable propio para elegir la ronda, reutilizable como `Desplegable`.
- Inicio y las secciones recuerdan la posición del scroll al regresar de un caso o sección (atrás
  del navegador o enlace), junto con la pestaña de proyecto y las secciones desplegadas en Inicio,
  durante la sesión de la pestaña.
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
- Cabecera en una sola fila desde `lg`: logo, páginas pegadas al logo y, a la derecha, el buscador
  junto al avatar. Desde `xl` el buscador es un campo; entre `lg` y `xl`, y en pantallas chicas, es
  un ícono que despliega el campo bajo la cabecera. En pantallas chicas las páginas van en una
  segunda fila con scroll horizontal.
- El atajo del buscador pasa de `/` a ñ (fuera de campos de texto); Ctrl/Cmd+K se conserva y el
  campo muestra la pista «Buscar (ñ)».
- El menú del avatar muestra íconos junto a los datos de la persona y en «Salir».
- Al cambiar de página por un enlace el scroll empieza arriba.

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
