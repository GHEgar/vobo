.PHONY: setup token-lectura test

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
	printf '\n  curl -H "Authorization: Bearer $$(cat secrets/validacion_lectura_token)" https://validaciones.ejemplo/api/fallas?ronda=1\n\n'
	rule
	printf '\n'

test: ## Correr las pruebas del backend en el entorno de desarrollo
	@$(LIB)
	banner 'TEST' 'desarrollo'
	run_step 'pytest' dc dev run --rm --no-deps backend python -m pytest
	rule
	printf '\n'
