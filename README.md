# validaciones

Guided test cases for a team validating a release, and a per-tool deploy-or-defer decision.

Each tester follows the cases assigned to them step by step, marks Pass / Fail / Couldn't test and
reports what didn't match, with screenshots. Coordination sees progress per person and per project,
manages failures, and recommends per tool; approvers decide what ships. Content, branding and
identity provider are per instance: the application ships none of them.

## Run

```bash
make setup    # creates .env.development and the missing secrets
make up       # development: Vite + backend with reload
make deploy   # production: nginx serves the build and proxies /api to the backend
make help
```

In development, `AUTH_MODO=local` shows a picker of test users (tester, coordination, approver, no
role). The backend refuses it unless `APP_ENV=dev`. Without `CONTENIDO_DIR` it serves
`ejemplo/contenido`, a fictional online store.

## Preparing an instance

1. Write the content in its own folder or repository and point `CONTENIDO_DIR` at it.
2. Optionally, add a theme folder and point `TEMA_DIR` at it.
3. Register the application with an OpenID Connect provider and fill the `OIDC_*` variables.
4. Copy `.env.production.example` to `.env.production`, run `make setup` for the secrets, then
   `make deploy`.

| Piece | Where | Reloads without rebuild |
|---|---|---|
| Content | `CONTENIDO_DIR` | Yes, on file change |
| Theme | `TEMA_DIR` | Yes, on browser reload |
| Identity provider | `OIDC_*` in `.env.production` | No, restart the backend |
| Data | Docker volumes `VOLUMEN_DATOS` and `VOLUMEN_EVIDENCIAS` | — |

## Content

```text
instancia.yaml          name, description, project order and names, test account descriptions
secciones/*.yaml        one section per change, with its tools and cases
procedimientos*.yaml    reusable procedures that cases cite
media/<procedure>.webp  one animation per procedure
```

`ejemplo/contenido` is the reference for every field. A broken YAML file never takes the API down:
it is skipped and listed under `errores` in `GET /api/contenido`.

## Theme

Colors and fonts are CSS variables (`--color-*`, `--tipo-*`). Colors default to a neutral palette
and fonts to [Rotulo](https://github.com/GHEgar/rotulo) (`@npmegar/rotulo`). The theme folder holds
a `tema.css` served at `/tema/` whose `:root` overrides them:

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

## Identity provider

Any OpenID Connect provider with discovery, authorization code + PKCE and RS256 access tokens.

| Variable | Use |
|---|---|
| `OIDC_ISSUER_URL` | Base for server-to-server calls; discovery lives under it |
| `OIDC_PUBLIC_URL` | Base the browser sees, when it differs from the issuer URL |
| `OIDC_EXPECTED_ISSUER` | `iss` to require; defaults to the discovery issuer |
| `OIDC_CLIENT_ID`, `secrets/oidc_client_secret` | Client credentials (`client_secret_post`) |
| `OIDC_REDIRECT_URI` | `https://<domain>/api/auth/callback` |
| `OIDC_AUDIENCE` | `aud` the access token must carry |
| `OIDC_TOKEN_TYP` | `typ` claim to require, if the provider sets one |
| `OIDC_PERMISOS_URL` | Endpoint returning `{"permissions": [...]}`; without it, the `OIDC_PERMISOS_CLAIM` claim |

The permissions are `validacion.casos.ejecutar`, `validacion.tablero.ver`,
`validacion.fallas.gestionar` and `validacion.herramientas.aprobar`.

## Read-only access

```bash
curl -H "Authorization: Bearer $(cat secrets/validacion_lectura_token)" \
    "https://<domain>/api/fallas?ronda=1"
```

Also `GET /api/tablero`, `/api/herramientas`, `/api/aprobaciones` and `/api/comentarios`, each with
`?ronda=`.

## Development

```bash
make test                                   # backend tests in the dev container
cd backend && ruff check .
cd frontend && npm run lint && npm run build
```

## License

AGPL-3.0-only © GHEgar
