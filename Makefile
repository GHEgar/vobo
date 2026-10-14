REPO_NAME    := validaciones
PROJECT_PROD := $(or $(COMPOSE_NOMBRE),$(shell sed -n 's/^COMPOSE_NOMBRE=//p' .env.production 2>/dev/null | tail -n 1),$(REPO_NAME))
COMPOSE_PROD := -f compose.yaml -f compose.prod.yaml
COMPOSE_DEV  := -f compose.yaml -f compose.dev.yaml
ENV_PROD     := .env.production
ENV_DEV      := .env.development

UP_PRE        := setup
DEPLOY_GUARDS  = env_guard; proteger_secretos

include make/common.mk
include make/validacion.mk
