# vobo

Guided test cases for a team validating a release, and a per-tool deploy-or-defer decision.

*VoBo* is short for *visto bueno*, the Spanish sign-off that something is good to go.

Each tester follows the cases assigned to them step by step, marks Pass / Fail / Couldn't test and
reports what didn't match, with screenshots. Coordination sees progress per person and per system,
manages failures, and recommends per tool; approvers decide what ships. Content, branding and
identity provider are per instance: the application ships none of them. One installation serves one
organization.

## Install

Needs a Linux server with Docker Engine, Docker Compose v2, `git`, `make` and `python3`.

```bash
git clone <repository url> /srv/vobo
cd /srv/vobo
make instalar
```

`make instalar` checks the requirements and the port, asks for the domain, whether people reach it
over HTTPS, the port, the sign-in mode (`cuentas`, `oidc` or `ambos`, with the provider details when
it applies), where content lives (`base` by default) and the compose project name, then writes
`.env.production`, generates the secrets, builds, starts, waits for the healthchecks and, when the mode
includes own accounts, prints the invitation link for the first administrator. Running it again never
overwrites an existing `.env.production`: it offers to continue with it or quit.

Every question can be answered with a variable, and without a terminal it takes the defaults:

```bash
DOMINIO=vobo.example.org HTTPS=si NGINX_PORT=8080 AUTH_MODO=cuentas \
    ADMIN_EMAIL=person@example.org make instalar
```

`COMPOSE_NOMBRE`, `VOLUMEN_DATOS`, `VOLUMEN_EVIDENCIAS`, `VOLUMEN_MEDIA`, `NGINX_BIND_ADDR`, `VM_IP`,
`CONTENIDO_DIR`, `TEMA_DIR` and, for the provider, `OIDC_ISSUER_URL`, `OIDC_PUBLIC_URL`,
`OIDC_CLIENT_ID`, `OIDC_AUDIENCE` and `OIDC_CLIENT_SECRET` work the same way.

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
`validacion_cuentas`), never in `.env.production`. `make deploy` rebuilds and restarts with the current
tree; `make status`, `make logs` and `make shell` help diagnose.

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

To move to a new server: clone the repository at the backup's `git` commit, extract `config.tar` from
the backup in the repository folder, run `make instalar` (it keeps that `.env.production`), then
`make restaurar desde=<folder>`.

## Upgrading

```bash
make actualizar
```

It refuses local changes to tracked files, takes a `-previo-actualizar` backup, runs
`git pull --ff-only` on the current branch, rebuilds with `make deploy` and waits for the
healthchecks. With no new commits it does nothing (`FORZAR=1` redeploys anyway). If the new version
does not come up healthy it changes nothing on its own and prints the way back:
`git checkout <previous commit> && make deploy DEPLOY_SYNC=:`, then
`make restaurar desde=<that backup>` if the data needs it too.

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

### Own accounts

There is no self sign-up and no outgoing email: links are generated and shared by hand.

- **First administrator.** While nobody holds Administración, `make admin email=person@example.org`
  prints a one-time invitation link valid for 48 h. It refuses once an administrator exists.
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

## Development

```bash
make test                                   # backend tests in the dev container
make migracion m="adds a table"             # new Alembic revision against the models
cd backend && ruff check .
cd frontend && npm run lint && npm run build
```

## License

AGPL-3.0-only © GHEgar
