# vobo

Guided test cases for a team validating a release, and a per-tool deploy-or-defer decision.

*VoBo* is short for *visto bueno*, the Spanish sign-off that something is good to go.

Each tester follows the cases assigned to them step by step, marks Pass / Fail / Couldn't test and
reports what didn't match, with screenshots. Coordination sees progress per person and per system,
manages failures, and recommends per tool; approvers decide what ships. Content, branding and
identity provider are per instance: the application ships none of them. One installation serves one
organization.

## Install

Needs a Linux server (`amd64` or `arm64`) with Docker Engine, Docker Compose 2.24 or newer, `make`,
`python3` and `curl` or `git`. The recommended path runs the published images: nothing is compiled on
the server.

The images are public on GitHub Container Registry, `ghcr.io/ghegar/vobo-backend` and
`ghcr.io/ghegar/vobo-web`, tagged `X.Y.Z`, `X.Y`, `latest` and `sha-<commit>`. Pin an exact
`X.Y.Z`. Each [release](https://github.com/GHEgar/vobo/releases) attaches `vobo-kit-X.Y.Z.tar.gz`:
the compose files, `Makefile` and `make/`, the `.env.production` and `secrets/` templates, the
example content and the neutral theme. That is all a server needs:

```bash
VERSION=0.3.0
BASE=https://github.com/GHEgar/vobo/releases/download/v$VERSION
curl -fsSLO "$BASE/vobo-kit-$VERSION.tar.gz" -O "$BASE/vobo-kit-$VERSION.tar.gz.sha256"
sha256sum -c "vobo-kit-$VERSION.tar.gz.sha256"
sudo mkdir -p /srv/vobo && sudo chown "$USER" /srv/vobo
tar -xzf "vobo-kit-$VERSION.tar.gz" -C /srv/vobo --strip-components=1
cd /srv/vobo
make instalar
```

A shallow clone of the tag works the same way:
`git clone --depth 1 --branch v0.3.0 <repository url> /srv/vobo`.

`make instalar` checks the requirements and the port, asks how to deploy (`imagen` by default, or
`codigo` to build on this server from a full clone) and which version (the kit's or the clone's), the
domain, whether people reach it over HTTPS, the port, the sign-in mode (`cuentas`, `oidc` or `ambos`,
with the provider details when it applies), where content lives (`base` by default) and the compose
project name, then writes `.env.production` (with `MODO_DESPLIEGUE` and `VOBO_VERSION`), generates the
secrets, pulls the images (or builds), starts, waits for the healthchecks and, when the mode includes
own accounts, prints the invitation link for the first administrator. Running it again never
overwrites an existing `.env.production`: it offers to continue with it or quit.

Every question can be answered with a variable, and without a terminal it takes the defaults:

```bash
VOBO_VERSION=0.3.0 DOMINIO=vobo.example.org HTTPS=si NGINX_PORT=8080 AUTH_MODO=cuentas \
    ADMIN_EMAIL=person@example.org make instalar
```

`MODO_DESPLIEGUE`, `COMPOSE_NOMBRE`, `VOLUMEN_DATOS`, `VOLUMEN_EVIDENCIAS`, `VOLUMEN_MEDIA`,
`NGINX_BIND_ADDR`, `VM_IP`, `CONTENIDO_DIR`, `TEMA_DIR` and, for the provider, `OIDC_ISSUER_URL`,
`OIDC_PUBLIC_URL`, `OIDC_CLIENT_ID`, `OIDC_AUDIENCE` and `OIDC_CLIENT_SECRET` work the same way.
`VOBO_IMAGEN_BACKEND` and `VOBO_IMAGEN_WEB` replace the image repositories (a mirror, a local build);
the tag is always `VOBO_VERSION`.

In `imagen` mode `compose.imagen.yaml` is layered over `compose.yaml` and `compose.prod.yaml`: it only
swaps each `build` for `image: <repository>:${VOBO_VERSION}`, so volumes, variables and secrets are
the same in both modes. `codigo` mode keeps building on the server; development and anyone who
prefers to compile use it. An instance installed before 0.3.0 has no `MODO_DESPLIEGUE` and stays in
`codigo`; `make actualizar version=X.Y.Z MODO_DESPLIEGUE=imagen` moves it to the images.

## Quick start

```bash
make setup    # creates .env.development and the missing secrets
make up       # Vite + backend with reload
make help
```

In development, `AUTH_MODO=local` shows a picker of test users (tester, coordination, approver,
administration, no role). The backend refuses it unless `APP_ENV=dev`. Without `CONTENIDO_DIR` it serves
`ejemplo/contenido`, a fictional online store.

## Deploying

The production stack is two containers: nginx serves the build and proxies `/api` to the backend
(FastAPI on SQLite). Migrations run on every backend start.

1. **Port.** nginx listens on `NGINX_BIND_ADDR:NGINX_PORT` (`0.0.0.0:80` by default). Behind a proxy on
   the same machine, use `127.0.0.1` and any free port.
2. **Domain and TLS.** The app does not handle certificates. Put a TLS-terminating reverse proxy in
   front, forward the domain to that port with the `Host` header, and answer `HTTPS=si` (it sets
   `SITIO=https://<domain>` and `SESSION_COOKIE_SECURE=true`). Allow request bodies of 200 MB for the
   content import. Plain HTTP works with `HTTPS=no`, for an internal network only.
3. **Content and theme.** `CONTENIDO_DIR` points at the instance content (default
   `ejemplo/contenido`, imported once with `CONTENIDO_FUENTE=base`), `TEMA_DIR` at its theme. See
   [Content](#content) and [Theme](#theme).
4. **First administrator.** With `cuentas` or `ambos`, `make instalar` prints the link when given an
   email; later, `make admin email=person@example.org`. See [Own accounts](#own-accounts).

| Variable | Use |
|---|---|
| `DOMINIO`, `SITIO` | Public host and base URL; `FRONTEND_URL` and `ALLOWED_ORIGINS` derive from it |
| `NGINX_BIND_ADDR`, `NGINX_PORT` | Where nginx listens on the server |
| `AUTH_MODO`, `OIDC_*` | Sign-in, see [Authentication](#authentication) |
| `CONTENIDO_DIR`, `CONTENIDO_FUENTE`, `TEMA_DIR` | Content source and theme |
| `COMPOSE_NOMBRE`, `VOLUMEN_*` | Project and volume names; changing them on a running instance starts empty volumes |

Secrets live in `secrets/` (`secret_key`, `oidc_client_secret`, `validacion_lectura_token` and
`validacion_cuentas`), never in `.env.production`. In `imagen` mode `make deploy` pulls the images of
`VOBO_VERSION` that are missing, recreates what changed and waits for the healthchecks; in `codigo`
mode it rebuilds and restarts with the current tree. `make status`, `make logs` and `make shell` help
diagnose. Both containers run as non-root users: the backend as uid 10001, nginx as uid 101 on port
8080 inside the container.

## Backups

```bash
make respaldo               # respaldos/<date-time>/
make respaldo RETENER=14    # same, then deletes backups older than 14 days
```

A backup is taken hot, without stopping the app: the database through SQLite's backup API inside the
backend container, the rest of the data volume (uploaded logos), evidences, editor media,
`.env.production` and `secrets/`. `manifiesto.json` records the app version, git commit, Alembic
revision, row counts per table and the SHA-256 of every file. Folders are `700` and files `600`;
`RESPALDOS_DIR` changes the destination. Retention only deletes folders that carry a manifest.

```bash
make restaurar desde=respaldos/20261016-030000
make restaurar desde=respaldos/20261016-030000 CON_CONFIG=1    # also .env.production and secrets/
```

Restoring checks every checksum, refuses a backup from a newer schema, asks to type the project name
(`CONFIRMAR=<project>` answers it), backs up the current state to a `-previo-restaurar` folder, stops
the app, replaces database, data, evidences and media, starts it, waits for the healthchecks and
compares row counts with the manifest.

A suggested daily cron entry, plus a copy of `respaldos/` to another machine:

```cron
0 3 * * * cd /srv/vobo && make respaldo RETENER=14 >> respaldos/cron.log 2>&1
```

To move to a new server: unpack the kit of the backup's `version` (in `codigo` mode, clone the
repository at its `git` commit), extract `config.tar` from the backup in that folder, run
`make instalar` (it keeps that `.env.production`), then `make restaurar desde=<folder>`.

## Upgrading

```bash
make actualizar version=0.3.1
```

In `imagen` mode it pulls the images of the new version first (a version that is not published
changes nothing), takes a `-previo-actualizar` backup, writes `VOBO_VERSION` in `.env.production`,
deploys and waits for the healthchecks. Migrations run when the backend starts. Without `version`, or
with the current one, it does nothing (`FORZAR=1` redeploys anyway). If the new version does not come
up healthy it changes nothing on its own and prints the way back:
`make actualizar version=<previous>`, then `make restaurar desde=<that backup>` when the database was
already migrated and the previous version refuses it. Read the release notes before jumping several
versions.

In `codigo` mode `make actualizar` refuses local changes to tracked files, takes the backup, runs
`git pull --ff-only` on the current branch, rebuilds with `make deploy` and waits for the
healthchecks; with no new commits it does nothing. The way back is
`git checkout <previous commit> && make deploy DEPLOY_SYNC=:`, then `make restaurar` if needed.

## Releasing

For the maintainer:

1. Set the version in `frontend/package.json` and its lock (`npm version X.Y.Z --no-git-tag-version`
   in `frontend/`).
2. In `docs/CHANGELOG.md`, rename `## [No publicado]` to `## [X.Y.Z] - YYYY-MM-DD` and leave an empty
   `## [No publicado]` above it.
3. Commit, create the tag `vX.Y.Z` on that commit and push the tag to GitHub.

The `imagenes` workflow checks that the tag, `package.json`, its lock and the latest dated CHANGELOG
section agree, builds both images for `linux/amd64` and `linux/arm64` with `APP_VERSION=X.Y.Z`,
pushes them to GHCR with the `GITHUB_TOKEN`, and creates the GitHub release with that CHANGELOG
section as notes and the kit attached. A tag with a pre-release suffix (`v0.4.0-rc.1`) publishes only
its exact tag and a pre-release. It can be re-run for an existing tag from *Actions → imagenes → Run
workflow*. `make kit version=X.Y.Z` builds the same kit locally in `dist/`.

GHCR creates a new package as private. After the first publish, open each package
(`vobo-backend`, `vobo-web`) from the repository's *Packages*, then *Package settings → Change
visibility → Public*; it is a one-time step per package.

## Content

```text
instancia.yaml          branding, name, description, system order and names, test account descriptions
secciones/*.yaml        one section per change, with its tools and cases
procedimientos*.yaml    reusable procedures that cases cite
media/<procedure>.webp  one animation per procedure
```

`ejemplo/contenido` is the reference for every field. A broken YAML file never takes the API down:
it is skipped and listed under `errores` in `GET /api/contenido`.

`CONTENIDO_FUENTE` chooses where sections, cases and procedures live:

- `base` (what `make instalar` proposes): stored in SQLite and edited from `/editor` (permission
  `validacion.contenido.editar`, included in Administración and assignable to custom roles). On the
  first start with empty content tables, `CONTENIDO_DIR` is imported (sections, procedures and media).
- `archivos` (the default when unset): read from `CONTENIDO_DIR` as above, reloaded on file change;
  `/editor` only offers an export.

`instancia.yaml` is read from `CONTENIDO_DIR` in both modes. The editor works on the current
project, groups sections by system, reorders, duplicates, hides or deletes them (a section whose
cases already have results can only be hidden), edits every field, and manages procedures with
their animation (WebP, GIF, PNG, JPEG, MP4 or WebM up to 20 MB, checked by content). Saves are validated with the YAML loader's models, errors come
back per field, and every change is kept in a restorable history. Case ids with results, and tool ids
with decisions, cannot change.

`GET /api/contenido/exportar.zip` (edit permission or the read-only token) returns the content as
YAML plus `media/`; importing that zip from the editor previews the changes and replaces everything
after confirmation. Uploaded media lives in the `VOLUMEN_MEDIA` volume, served by nginx at `/media/`.

## Projects

A project is what is being validated: a release, a product, an ecosystem. Each one has its own
content (sections, cases, procedures, animations, history and export) and its own rounds; results,
assignments, failures, decisions, approvals and comments belong to it through their round. Its name
sits next to the logo, in its own color; with more than one, that name is a picker that switches
content, rounds and home page.

**Projects and systems are different things.** Systems (`sistema` in a section, the `sistemas` list
in `instancia.yaml`, Configuración → Sistemas) group the sections of a project into tabs and columns
on the home page and the board, and the same list serves every project. The older key `proyectos` is
still read, and `GET /api/instancia` still returns it next to `sistemas`.

- Every install starts with one project, `principal`, named after the instance; upgrading moves all
  existing rounds and content into it, so nothing changes until a second project is created.
- Administration → Proyectos creates, edits, orders, archives and picks the default project. A
  project with rounds can be archived, not deleted; the default one cannot be archived.
- With `CONTENIDO_FUENTE=archivos` there is exactly one project (the files); creating more requires
  `CONTENIDO_FUENTE=base`. In `base`, the first import from `CONTENIDO_DIR` goes to the default
  project, the editor and the `.zip` work on the current project, and case ids only need to be
  unique within a project.
- The API resolves the project from `ronda` when given, then from `?proyecto=<clave>`, then the
  default one, so existing scripts and the read-only token keep working unchanged. Shared links carry
  `?proyecto=<clave>` when the project is not the default one.

## Branding

`instancia.yaml` brands the instance. Every field is optional; paths are relative to the theme
folder, served from `/tema/`, and may not leave it (no `..`, absolute paths or URLs).

| Field | Use | Default |
|---|---|---|
| `producto` | Product name shown as the brand | `VoBo` |
| `nombre` | Instance name, next to the brand and in the window title | empty |
| `descripcion` | Page description | empty |
| `logo.claro`, `logo.oscuro` | Logos for light and dark surfaces (the light one is used everywhere today), about 32–40 px tall | the `producto` text |
| `logo.alt` | Logo alternative text | `producto` |
| `favicon` | Browser tab icon | `/favicon.svg` |
| `color_tema` | Browser UI color (`theme-color`), quoted `"#RRGGBB"` | `"#1F4E79"` |
| `color_nombre` | Default color of the project name (`--color-nombre`), quoted `"#RRGGBB"`; a project's own color wins | the muted text color |
| `entrada.titulo`, `entrada.mensaje` | Sign-in heading and a note shown in every sign-in state | `Iniciar sesión`, none |

A missing logo falls back to the `producto` text, and an invalid field is reported under `errores`
without discarding the rest. Start with `TEMA_DIR=./ejemplo/tema` to see the example logo and palette.

## Configuration

Administrators can customize the instance from **Administration → Configuración**. Each value
resolves as built-in default, then `instancia.yaml` and `TEMA_DIR`, then what was saved in the app;
every saved field has a **Restablecer** button that falls back to the file or default.

| Part | What can be edited |
|---|---|
| Identidad | `producto`, `nombre`, `descripcion` and the sign-in texts |
| Marca | light and dark logo, favicon, alternative text and `color_tema` |
| Colores | twelve palette colors, including «Nombre del proyecto» (`color_nombre`), and the font (theme, bundled Rotulo or system), with live preview |
| Sistemas | ordered `clave`/`nombre` list shared by every project; a key used by sections cannot be removed |
| Cuentas de prueba | `prefijo`/`descripcion` pairs |

Logos and favicon accept PNG, SVG or WebP up to 2 MB, recognized by content; SVG with scripts, event
handlers, `javascript:`/`data:` URLs or `foreignObject` is rejected. They are stored in the data volume
(`/data/marca`) and included in `make respaldo`. Saved colors are served at `/api/instancia/tema.css`,
loaded after `/tema/tema.css`.

`make deploy` sets `APP_VERSION` (short commit plus build time) in both images; open tabs compare it
with `GET /api/version` every 5 minutes and offer to reload when it changes.

## Theme

Colors and fonts are CSS variables (`--color-*`, `--tipo-*`), defaulting to a neutral palette and to
[Rotulo](https://github.com/GHEgar/rotulo). The theme folder holds a `tema.css` served at `/tema/`:

```css
@font-face {
    font-family: MyFont;
    src: url('fuentes/MyFont-Bold.otf') format('opentype');
    font-weight: bold;
}

:root {
    --color-primario: #0B6E4F;
    --tipo-negrita: MyFont, sans-serif;
    --tipo-negrita-peso: bold;
}
```

## Authentication

| `AUTH_MODO` | Sign-in screen |
|---|---|
| `oidc` | Straight redirect to the identity provider |
| `cuentas` | Email and password stored by the app |
| `ambos` | Email and password, plus a «Entrar con tu organización» button for the provider |
| `local` | Test-user picker; development only |

The same person is one user whatever the method, matched by email. Changes to `.env.production`
take effect on the next `make deploy`.

### Roles and permissions

Permissions: `validacion.casos.ejecutar`, `validacion.tablero.ver`, `validacion.fallas.gestionar`,
`validacion.herramientas.aprobar`, `validacion.contenido.editar` and `validacion.admin`, which implies
all the others and opens **Administración**. A person's permissions are the union of what the provider
grants, the roles assigned in the app, and roles mapped from provider groups. Four system roles ship:
Validador, Coordinación, Aprobación and Administración; own roles are managed in Administración → Roles,
and a role's key is fixed once created.

Anyone with `validacion.tablero.ver` or `validacion.fallas.gestionar` gets an **Actividad** button in
the header with the number of people active right now. It shows who is online (what they are doing,
for how long, round, browser, device and screen size) and a timeline of recent results, failures,
comments, approvals, decisions, notices, sign-ins and content edits, filterable by person and type. It
is derived from existing data (`GET /api/actividad`, `GET /api/actividad/resumen`) and never exposes
sessions, tokens or screenshots.

### Own accounts

There is no self sign-up and no outgoing email: links are generated and shared by hand.

- **First administrator.** While nobody holds Administración, `make admin email=person@example.org`
  prints a one-time invitation link valid for 48 h (`cuentas`, `ambos`). With `AUTH_MODO=oidc` it gives
  the role to that person instead, once they have signed in through the provider. It refuses once an
  administrator exists.
- **Invitations and resets.** Administración → Personas invites by email with roles or resets a
  password, each with a one-time 48 h link; a reset closes that person's password sessions.
- **Deactivation** blocks password sign-in and closes its sessions; provider sign-in is unaffected.

Passwords need 10 characters and cannot be one of the most common ones; they are stored as Argon2id,
link tokens only as SHA-256. After 5 failed attempts in 15 minutes for the same email or IP the app
answers 429. Behind a proxy the IP is the proxy's, so the email limit is the one that holds.

### Identity provider

Any OpenID Connect provider with discovery, authorization code + PKCE and RS256 access tokens.

| Variable | Use |
|---|---|
| `OIDC_ISSUER_URL` | Base for server-to-server calls; discovery lives under it |
| `OIDC_PUBLIC_URL` | Base the browser sees, when it differs |
| `OIDC_EXPECTED_ISSUER` | `iss` to require; defaults to the discovery issuer |
| `OIDC_CLIENT_ID`, `secrets/oidc_client_secret` | Client credentials (`client_secret_post`) |
| `OIDC_REDIRECT_URI` | `https://<domain>/api/auth/callback` |
| `OIDC_AUDIENCE`, `OIDC_TOKEN_TYP` | `aud` and `typ` the access token must carry |
| `OIDC_PERMISOS_URL` | Endpoint returning `{"permissions": [...]}`; without it, the `OIDC_PERMISOS_CLAIM` claim |
| `OIDC_ROLES_CLAIM`, `OIDC_ROLES_MAPA` | Claim with the person's groups and a JSON map from group to role key |

```bash
OIDC_ROLES_CLAIM=groups
OIDC_ROLES_MAPA='{"qa-leads": "coordinacion", "release-managers": "aprobacion"}'
```

Unmapped groups are ignored; an invalid `OIDC_ROLES_MAPA` stops the backend at startup.

## Read-only access

```bash
curl -H "Authorization: Bearer $(cat secrets/validacion_lectura_token)" \
    "https://<domain>/api/fallas?ronda=1"
```

Also `GET /api/tablero`, `/api/herramientas`, `/api/aprobaciones` and `/api/comentarios`, each with
`?ronda=`. Without a round, lists use the default project; add `?proyecto=<clave>` for another one.

`GET /api/participacion?proyectos=<clave>,<clave>&ronda=<id>&agrupar=proyecto|sistema|seccion` returns who marked cases in which project
in the [tequio](https://github.com/GHEgar/tequio) data format, ready for `<Tequio>`, `toSvg` or
`npx @npmegar/tequio render`. Without `proyectos` it covers every active project; each one uses its
open round (or its latest), and `ronda` applies when a single project is asked. People are identified
by a keyed hash, never by email. The «Participación» page shows it live, and the failure report
prints it as a section. Anyone who sees the board or the failures can read it.

## Development

```bash
make test                                   # backend tests in the dev container
make migracion m="adds a table"             # new Alembic revision against the models
cd backend && ruff check .
cd frontend && npm run lint && npm run build
```

## License

AGPL-3.0-only © GHEgar
