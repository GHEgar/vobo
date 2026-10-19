# Changelog

Todos los cambios notables de este proyecto se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/)
y el proyecto se adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [No publicado]

### Agregado

- Bitácora de resultados (`resultados_historial`, migración `0007`): cada vez que un resultado se
  crea, cambia de estado, se limpia o cambia de pasos queda una fila con estado, paso y acción
  (`crear`, `marcar`, `cambiar`, `limpiar`, `paso`), en la misma transacción que el cambio.
- Hora de cierre de las rondas (`cerrada_en`, también en la respuesta de rondas): se guarda al
  cerrarla y se limpia al reabrirla; las rondas cerradas antes de la migración quedan sin fecha.
- `GET /api/historial/avance?ronda=&proyecto=&desde=&hasta=` (permiso de seguimiento): casos
  marcados acumulados por día calculados desde la bitácora; lista vacía si aún no hay historial.
- Seguimiento de fallas y comentarios (migración `0009`): tabla `comentarios_seguimiento` con estado
  (nuevo, en curso, resuelto), plazo y resolución de cada comentario de paso o «No pude probarlo»,
  sembrada con los comentarios existentes; tabla `seguimiento` de solo inserción con respuestas y
  cambios de estado, plazo y nota, con autor y hora.
- Fallas con `plazo` (fecha compromiso), `plazo_por` (quien lo fijó, mostrado como responsable),
  `resuelta_en` y `resuelta_por`: se fijan al cerrar y se limpian al reabrir. Las cerradas antes de
  la migración quedan sin fecha.
- `POST /api/fallas/{id}/respuestas`, `PATCH /api/comentarios/{id}` (estado y plazo) y
  `POST /api/comentarios/{id}/respuestas`, con permiso de gestionar fallas. Las respuestas de fallas
  y comentarios traen su hilo en `seguimiento`, cargado en una sola consulta.
- Un comentario resuelto vuelve a «Nuevo» si quien lo escribió cambia el texto; uno borrado conserva
  su seguimiento y deja de listarse.
- En Fallas: plazo con responsable, marca «Vencida», «Resuelta por … · tardó …» e hilo con respuestas
  y cambios en cada falla y comentario; los comentarios ganan estado editable.
- CSV de fallas: columnas plazo, responsable, resuelta, resolvió, tiempo de solución (horas) y
  respuestas al final, sin mover las existentes.

### Cambiado

- El informe imprimible se organiza por proyecto, herramienta y fallas y comentarios, de todos los
  proyectos o de los elegidos, con resumen por proyecto (abiertas, resueltas, vencidas, tiempo
  medio de solución) y opciones para incluir o no resumen, fallas, «No pude probarlo», comentarios,
  respuestas e historial, evidencias y tiempos, filtrar por herramienta, estado y severidad. Todo
  queda en la dirección para reproducir el informe; los enlaces anteriores siguen funcionando.
  Por omisión incluye todo.
- «Descargar CSV» pasa de Fallas al informe, junto a «Imprimir / guardar PDF», y descarga lo mismo
  que muestra el informe: una fila por falla o comentario con proyecto y herramienta.
- Las migraciones `0008` y `0010` crean y quitan la tabla `pantallas` de un modo pantalla que no
  llegó a publicarse; al actualizar desde 0.3.2 no queda rastro.
- Fallas muestra al entrar todas las rondas y tipos; los filtros se abren con el botón «Filtros»,
  que cuenta los activos. Se quita la casilla «Incluir comentarios».

## [0.3.2] - 2026-10-16

### Agregado

- Comentarios en el informe de fallas: `GET /api/fallas/informe.csv?comentarios=1` agrega la columna
  «Comentarios» con los del mismo caso (y paso) de esa ronda, `fecha · nombre: texto` uno por línea.
  En Fallas, la casilla «Incluir comentarios» (recordada en el navegador) la activa para el CSV y el
  informe imprimible, que los muestra debajo de cada falla.

### Cambiado

- El enlace «Informe imprimible» de Fallas pasa a decir «Informe».
- El informe de fallas y el acta separan las acciones del documento: barra fija arriba que no se
  imprime y el documento como hoja centrada.
- El encabezado del informe, del acta y su `.md` usan el nombre del proyecto actual.
- Con un solo proyecto cuyo nombre es igual al producto (sin distinguir mayúsculas, acentos ni
  espacios), el nombre no se repite junto a la marca, en la entrada ni en los títulos.
- Los enlaces de comentarios, avisos y pasos se muestran acortados (dominio y ruta, con la dirección
  completa al pasar el cursor) y los comentarios ya son enlazables.

### Corregido

- La imagen web compilaba el frontend una vez por arquitectura, y en arm64 (emulada) tardaba más de
  una hora: ahora se compila una sola vez en la plataforma del build.
- `make restaurar CON_CONFIG=1` fallaba si `secrets/` o `.env.production` eran enlaces simbólicos: ahora
  copia el contenido sobre las rutas existentes.
- Las direcciones muy largas en comentarios desbordaban su contenedor.
- `make admin` no podía nombrar al primer administrador con `AUTH_MODO=oidc`: ahora da el rol a una
  persona que ya entró por el proveedor.

## [0.3.1] - 2026-10-16

### Cambiado

- tesela 0.7: íconos de archivo según lo que se maneja (CSV, informe, acta en Markdown, paquete
  .zip, capturas, animaciones y logos).

### Corregido

- Variable sin usar en el Tablero que hacía fallar el lint.
- `make actualizar` de modo código a modo imagen fallaba en el respaldo previo: faltaba `VOBO_VERSION`
  y no existía la carpeta de animaciones en contenedores anteriores a 0.3.0.

## [0.3.0] - 2026-10-16

### Agregado

- Imágenes públicas versionadas en GHCR: `ghcr.io/ghegar/vobo-backend` y `ghcr.io/ghegar/vobo-web`
  para `linux/amd64` y `linux/arm64`, con tags `X.Y.Z`, `X.Y`, `latest` (salvo prerrelease) y
  `sha-<commit>`, etiquetas OCI y `APP_VERSION` igual a la versión. Nada de la instancia va horneado:
  dominio, OIDC, tema y contenido llegan por variables y volúmenes al arrancar.
- Instalación desde imágenes, sin compilar: `compose.imagen.yaml` cambia el build por
  `image: …:${VOBO_VERSION}` y `MODO_DESPLIEGUE=imagen` (por omisión de `make instalar`) guarda la
  versión en `.env.production`. En ese modo `make deploy` baja las imágenes, levanta y espera los
  healthchecks, y `make actualizar version=X.Y.Z` respalda, cambia de versión y despliega; si no queda
  sano imprime cómo volver a la anterior. `MODO_DESPLIEGUE=codigo` sigue construyendo en el servidor.
- Kit de instalación `vobo-kit-X.Y.Z.tar.gz` (compose, `Makefile`, `make/`, plantillas de
  `.env.production` y secretos, ejemplo y tema neutro) con `make kit`, para instalar sin clonar el
  repositorio.
- Release automático: al empujar un tag `vX.Y.Z` el workflow `imagenes` verifica que coincida con
  `frontend/package.json` y el CHANGELOG, publica las imágenes y crea el release de GitHub con el kit
  adjunto y estas notas.

- Proyectos: lo que se valida (una versión, un ecosistema) con su propio contenido y sus propias
  rondas. Tabla `proyectos` (migración `0005`) con clave, nombre, descripción, color del nombre,
  orden, archivado y por omisión; la migración crea el proyecto `principal` con el nombre de la
  instancia y le asigna todas las rondas, el contenido en base, los avisos y la presencia. Con
  `CONTENIDO_FUENTE=base` cada proyecto tiene secciones, casos, procedimientos, animaciones,
  historial y .zip propios, y los ids de caso pueden repetirse entre proyectos; con `archivos` hay un
  solo proyecto. La API resuelve el proyecto por la ronda, luego por `?proyecto=<clave>` y si no por
  el de omisión, así que los scripts y el token de lectura siguen igual; `GET /api/proyectos`,
  `GET /api/rondas?proyecto=`, `proyecto` al crear una ronda y `/api/admin/proyectos` para
  administrarlos.
- Administración → Proyectos: crear, editar, ordenar, archivar, marcar por omisión y borrar los que
  no tienen rondas. En modo archivos muestra el único proyecto y por qué no se pueden crear más.
- Selector de proyecto junto al logo cuando hay más de uno; el elegido se recuerda y los enlaces de
  caso, sección, informe, acta y avisos llevan `?proyecto=<clave>` cuando no es el de omisión.

- Instalación, respaldo, restauración y actualización con make. `make instalar` revisa requisitos
  y puerto, crea `.env.production` preguntando lo mínimo (o con variables, sin terminal), genera los
  secretos, construye, espera los healthchecks e imprime la invitación del primer administrador.
  `make respaldo` copia en caliente la base con la API de backup de SQLite, el resto del volumen de
  datos, evidencias, media, `.env.production` y `secrets/` a `respaldos/<fecha-hora>/` con
  `manifiesto.json` (versión, commit, revisión Alembic, conteos y sha256), y `RETENER=N` borra los
  de más de N días. `make restaurar desde=...` verifica sumas, pide confirmación, respalda el estado
  actual, restaura (`CON_CONFIG=1` incluye la configuración) y compara conteos. `make actualizar`
  respalda, hace `git pull --ff-only`, despliega y, si no queda sano, imprime cómo volver.
- Configuración de la instancia desde la app (Administración → Configuración): identidad, textos de
  entrada, logo claro y oscuro, favicon, color del navegador, doce colores con vista previa en vivo,
  fuente, proyectos ordenables y descripciones de cuentas de prueba. Lo guardado gana sobre
  `instancia.yaml` y el tema de archivos, y cada campo se puede restablecer; sin nada guardado todo
  queda igual. Tabla `configuracion` (migración `0004`), imágenes PNG, SVG o WebP de hasta 2 MB en
  `MARCA_DIR` (`/data/marca`) con SVG peligrosos rechazados, `GET /api/instancia/tema.css` y API en
  `/api/admin/configuracion`.
- Aviso de versión nueva: `make deploy` fija `APP_VERSION` en las dos imágenes, `GET /api/version`
  la expone y las pestañas abiertas ofrecen recargar cuando cambia.

- Editor de contenido opcional con `CONTENIDO_FUENTE=base` (por omisión `archivos`, sin cambios):
  secciones, casos, herramientas, galería y procedimientos en SQLite (revisión `0003`), importación
  inicial desde `CONTENIDO_DIR`, página `/editor` con permiso nuevo `validacion.contenido.editar`,
  validación por campo, historial con restaurar, ocultar secciones con resultados y animaciones
  WebP/GIF/PNG/JPEG/MP4/WebM en el volumen `VOLUMEN_MEDIA`. API en `/api/editor/...`.
- Exportar el contenido como .zip de YAML (`GET /api/contenido/exportar.zip`) e importarlo desde el
  editor con vista previa de cambios.
- Presencia en línea para coordinación: cada sesión informa dónde está (página, caso, paso y si está
  reportando una falla o comentando) cada 30 s mientras la pestaña está visible, y
  coordinación lo ve en Actividad con estado activo/inactivo y enlace al caso. `POST` y `GET /api/presencia`.
- Informe de fallas con los filtros vigentes: descarga CSV para hojas de cálculo
  (`GET /api/fallas/informe.csv`, UTF-8 con BOM, fechas en la zona horaria de quien descarga y
  celdas protegidas contra fórmulas) e informe imprimible en `/informe-fallas` con resumen por
  severidad, estado y sección, detalle de cada falla y miniaturas de sus capturas.
- Marca por instancia en `instancia.yaml`: nombre del producto, logo claro/oscuro, favicon, color del
  navegador (`theme-color`) y textos de la pantalla de entrada, con rutas limitadas a la carpeta del
  tema. Se usan en la cabecera, la entrada, el acta y el informe imprimibles; tema de ejemplo en
  `ejemplo/tema`.
- Roles en la app: tablas `roles` y `usuario_roles` con cuatro roles de sistema (Validador,
  Coordinación, Aprobación y Administración) y permiso nuevo `validacion.admin`, que implica todos los
  demás. Los permisos efectivos son la unión de los del proveedor, los de los roles asignados y los de
  roles mapeados desde grupos del proveedor (`OIDC_ROLES_CLAIM`, `OIDC_ROLES_MAPA`).
- Página Administración (menú de usuario, solo con `validacion.admin`): personas con sus roles,
  asignación de roles, activación de cuentas, y roles propios con permisos descritos. API en
  `/api/admin/...`.
- Cuentas propias con correo y contraseña: `AUTH_MODO=cuentas` o `ambos` (cuentas más proveedor),
  hashes Argon2id, invitaciones y restablecimientos por enlace de un solo uso de 48 h, cambio de la
  propia contraseña, límite de 5 intentos fallidos por correo e IP cada 15 min y primer administrador
  con `make admin email=...`. Migración `0002`.
- Modo edición en contexto para quien puede editar el contenido y solo con `CONTENIDO_FUENTE=base`:
  se enciende desde el menú de la cuenta, está apagado por omisión, dura la pestaña y se apaga al
  salir. Mientras está activo, una píldora con borde envuelve al avatar con «Modo edición» y «Salir»,
  sin relleno. Cada contenedor editable lleva contorno punteado y su propia barra de
  acciones arriba a la derecha (atenuada hasta pasar el puntero o enfocarla; siempre visible en
  pantallas táctiles): en el inicio cada sección se ordena, edita, oculta, muestra o borra (solo sin
  resultados), con las ocultas atenuadas; en la sección se edita su cabecera y cada caso se ordena,
  edita, duplica o borra; el caso se edita completo desde su tarjeta. «Agregar sección» y «Agregar
  caso» son un contenedor fantasma al final de cada lista. Los formularios son los del editor, en un
  modal con enlace «Abrir en el editor», que acepta `?seccion=<id>`. El listado del editor incluye
  la audiencia de cada sección.
- Actividad, para coordinación y administración (`validacion.tablero.ver` o
  `validacion.fallas.gestionar`): botón «Actividad» en la cabecera con el número de personas activas
  y un modal con **Ahora** (quién está, qué hace, desde cuándo, ronda, navegador, dispositivo y
  pantalla) y **Actividad reciente**, una línea de tiempo por día de resultados, fallas, comentarios,
  aprobaciones, decisiones, avisos, inicios de sesión y cambios de contenido, filtrable por persona y
  tipo y paginada con «Cargar más». Se deriva de las tablas existentes, sin bitácora nueva:
  `GET /api/actividad?proyecto=&ronda=&usuario=&tipo=&antes=&limite=` (cursor por fecha y
  desempate, `limite` hasta 100) y `GET /api/actividad/resumen`. Nunca expone sesiones, tokens ni
  capturas, solo cuántas trae una falla. La presencia guarda navegador y versión y dispositivo
  (derivados del User-Agent en el servidor, que se guarda recortado a 300), pantalla que manda el
  cliente y el inicio de la sesión de presencia, que se reinicia tras 10 minutos sin actividad
  (migración `0006`). El botón es solo ícono, con la etiqueta como tooltip y el número de personas
  activas.

### Cambiado

- «Rondas» pasa del menú de páginas al menú de la cuenta, con su ícono, para quien ve la página; la
  ruta `/rondas` no cambia y quien se queda con una sola página tiene la cabecera de una fila.

- La imagen web corre nginx sin root (usuario `nginx`, uid 101) y escucha en el puerto 8080 del
  contenedor; el puerto del servidor sigue siendo `NGINX_PORT`.
- `make restaurar` comprueba la revisión del respaldo contra la imagen en uso en modo imagen.
- rotulo 0.3.0: trazo un 15 % más grueso y descendentes del largo de las ascendentes.
- Lo que antes se llamaba «proyectos» (agrupación de secciones por `sistema`) se llama «Sistemas» en
  la interfaz: Configuración → Sistemas, pestañas del inicio, vista «Por sistema» del tablero, editor y
  asignaciones. Son de toda la instancia. `instancia.yaml` acepta `sistemas` además de `proyectos`, y
  `GET /api/instancia` sigue devolviendo `proyectos` y agrega `sistemas` y el `proyecto` pedido. Las
  pestañas del inicio usan `?sistema=` en la dirección (también leen el `?proyecto=` de enlaces viejos).
- El producto se llama VoBo (paquete `vobo`); los defaults de compose, volúmenes y red de instalaciones
  nuevas pasan a `vobo`. Permisos `validacion.*`, secretos y base conservan su nombre.
- El `nombre` de la instancia queda vacío por omisión: la marca la da `producto`, y un campo inválido
  de `instancia.yaml` se reporta sin descartar el resto del archivo.
- Migraciones con Alembic (revisión base `0001` y `make migracion m="..."`) y adopción automática
  de bases existentes al arrancar: se aplican las migraciones a mano previas, se verifica el esquema
  contra la revisión base y se marca, todo en una transacción que no toca nada si algo no coincide.
- Cabecera en dos filas: el nombre de la instancia va junto al logo, separado por un divisor, y el
  avatar a la derecha; debajo, las páginas a la izquierda y el buscador fijo como campo de texto a la
  derecha (en pantallas chicas, en su propia fila a todo el ancho). Conserva ñ y Ctrl/Cmd+K.
- Color del nombre de la instancia configurable con `color_nombre` en `instancia.yaml` o en
  Configuración → Colores («Nombre del proyecto», token `--color-nombre`); por omisión usa el texto
  tenue y ya no es naranja.
- Íconos de tesela 0.6.1 (con centrado óptico) y reseleccionados: el menú del avatar usa lápiz para
  el editor de contenido y el ícono de cerrar sesión en «Salir», que también sale del modo edición
  desde su píldora; Pasa, Falla y No pude probarlo usan círculo con palomita, círculo con cruz y
  alerta en botones, chips y criterios de salida; la ayuda de los campos es un signo de
  interrogación; los estados vacíos y de error muestran un ícono grande en duotono; las pestañas de
  Administración y del editor tienen ícono, y descargar, informe, imprimir, restaurar y «Cómo se ve»
  llevan el suyo. Grosor de trazo por omisión en íconos de 16 px o más.
- Menú de páginas solo con texto; el buscador mide lo que su placeholder y crece al enfocarlo si hay
  espacio, y con una sola página visible se coloca junto a la cuenta, sin segunda fila.
- El botón «Continuar» del inicio usa el color primario.
- Carga diferida de las páginas que no usa todo el mundo y React, React Router y React Query en su
  propio chunk: el chunk principal pasa de 639 kB a 117 kB.

### Corregido

- El detalle de los íconos de tesela casi no se veía sobre botones y fondos de relleno oscuros; ahora
  va en dirección clara (`--tesela-dir: -1`) sobre esos fondos.
- El ícono de ayuda del selector de ronda quedaba por debajo del centro.
- La presencia ya no se envía antes de que la sesión tenga su token CSRF, lo que daba 403 al cargar.
- Una sesión vencida ya no deja pestañas consultando con 401 en bucle: el primer 401 de una petición
  autenticada cierra la sesión en el cliente y lleva a la pantalla de entrada.

## [0.2.0] - 2026-10-15

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

- La fuente por defecto pasa a ser rótulo (`rotulo` en npm) en todo el frontend; un `tema.css` puede
  cambiarla con las variables `--tipo-*`.

- El lint del frontend usa `@npmegar/eslint-config` 0.4.0 desde npm (presets `base`, `react` y
  `react-app`) en lugar de una config propia.
- Imagen base del backend a `python:3.14-slim`.
- La interfaz usa los íconos de tesela.
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
