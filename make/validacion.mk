.PHONY: setup token-lectura test migracion admin

##@ Validacion

setup: ## Crear el .env.development y los secretos que falten
	@$(LIB)
	if [ ! -f $(ENV_DEV) ]; then
		cp .env.example $(ENV_DEV)
		row 'Env' 'creado' "$$C_GREEN" 'edita $(ENV_DEV)'
	fi
	crear_secretos
	proteger_secretos

token-lectura: ## Mostrar como consultar fallas y tablero con el token de solo lectura
	@$(LIB)
	banner 'TOKEN' 'solo lectura'
	if [ ! -s secrets/validacion_lectura_token ]; then
		fail 'Secretos:falta secrets/validacion_lectura_token' 'Crealo con make setup'
	fi
	row 'Uso' 'curl' "$$C_GREEN" 'GET /api/fallas y /api/tablero'
	printf '\n  curl -H "Authorization: Bearer $$(cat secrets/validacion_lectura_token)" https://vobo.ejemplo/api/fallas?ronda=1\n\n'
	rule
	printf '\n'

test: ## Correr las pruebas del backend en el entorno de desarrollo
	@$(LIB)
	banner 'TEST' 'desarrollo'
	run_step 'pytest' dc dev run --rm --no-deps backend python -m pytest
	rule
	printf '\n'

migracion: ## Crear una revision de Alembic contra los modelos: make migracion m="mensaje"
	@$(LIB)
	banner 'MIGRACION' 'alembic'
	if [ -z '$(m)' ]; then
		fail 'Mensaje:falta m' 'Uso: make migracion m="agrega roles"'
	fi
	ultima=$$(ls backend/alembic/versions | sed -n 's/^\([0-9]\{4\}\)_.*\.py$$/\1/p' | sort | tail -1)
	rev=$$(printf '%04d' $$((10#$${ultima:-0} + 1)))
	run_step "$$rev" dc dev run --rm --no-deps --user "$$(id -u):$$(id -g)" \
		-e DATABASE_PATH=/tmp/migracion.sqlite3 -e EVIDENCIAS_DIR=/tmp/evidencias \
		-e REVISION="$$rev" -e MENSAJE='$(m)' backend \
		sh -c 'python -m app.inicializar && alembic revision --autogenerate --rev-id "$$REVISION" -m "$$MENSAJE"'
	row 'Archivo' "$$(ls backend/alembic/versions/$${rev}_*.py)" "$$C_GREEN" 'revisalo antes de commitear'
	rule
	printf '\n'

admin: ## Primer administrador: invitación (cuentas o ambos) o rol a quien ya entró (oidc): make admin email=persona@ejemplo
	@$(LIB)
	banner 'ADMIN' 'primer administrador'
	if [ -z '$(email)' ]; then
		fail 'Correo:falta email' 'Uso: make admin email=persona@ejemplo'
	fi
	env=$$(resolve_env)
	if [ -z "$$env" ]; then
		fail 'Entorno:nada levantado' 'Levanta la instancia con make up o make deploy'
	fi
	rule
	dc "$$env" exec -T backend python -m app.crear_admin '$(email)'
	rule
	printf '\n'
