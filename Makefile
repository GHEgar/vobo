REPO_NAME    := vobo
PROJECT_PROD := $(or $(COMPOSE_NOMBRE),$(shell sed -n 's/^COMPOSE_NOMBRE=//p' .env.production 2>/dev/null | tail -n 1),$(REPO_NAME))
MODO_ACTIVO  := $(or $(MODO_DESPLIEGUE),$(shell sed -n 's/^MODO_DESPLIEGUE=//p' .env.production 2>/dev/null | tail -n 1),$(if $(wildcard backend/Dockerfile),codigo,imagen))
COMPOSE_PROD := -f compose.yaml -f compose.prod.yaml$(if $(filter imagen,$(MODO_ACTIVO)), -f compose.imagen.yaml)
COMPOSE_DEV  := -f compose.yaml -f compose.dev.yaml
ENV_PROD     := .env.production
ENV_DEV      := .env.development

UP_PRE        := setup
DEPLOY_GUARDS  = env_guard; proteger_secretos; fijar_version

ifeq ($(MODO_ACTIVO),imagen)
DEPLOY_SYNC    := :
DEPLOY_GUARDS   = env_guard; proteger_secretos; version_imagen
DEPLOY_BUILD   := run_step 'Pull' dc prod pull --policy missing
DEPLOY_DOWN    := :
DEPLOY_CMD     := dc prod up -d --remove-orphans
DEPLOY_POST     = $(MAKE) _salud
endif

export MODO_ACTIVO

include make/common.mk
include make/validacion.mk
include make/instancia.mk
include make/imagen.mk
