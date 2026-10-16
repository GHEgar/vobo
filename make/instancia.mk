.PHONY: instalar respaldo restaurar actualizar _salud

RESPALDOS_DIR ?= respaldos
INSTANCIA := $(LIB) && source make/instalar.sh && source make/respaldo.sh && source make/imagen.sh

export RESPALDOS_DIR

##@ Instancia

instalar: ## Instalar en este servidor: requisitos, .env.production, secretos, imagenes o build y primer admin
	@$(INSTANCIA)
	preparar_instalacion
	correo=$${ADMIN_EMAIL:-}
	$(MAKE) deploy DEPLOY_SYNC=:
	$(MAKE) _salud
	if [ -n "$$correo" ]; then
		$(MAKE) admin email="$$correo" || row 'Admin' 'omitido' "$$C_YELLOW" 'ya hay administracion o fallo; revisa arriba'
	fi
	banner 'INSTALAR' 'listo'
	mostrar_entrada
	modo=$$(valor_env AUTH_MODO)
	if [ "$$modo" != 'oidc' ] && [ -z "$$correo" ]; then
		row 'Admin' 'pendiente' "$$C_YELLOW" 'make admin email=persona@ejemplo'
	fi
	row 'Respaldo' 'make respaldo' "$$C_GREEN" 'programalo en cron con RETENER=14'
	rule
	printf '\n'

respaldo: ## Respaldar base, evidencias, media y config en caliente (RETENER=dias borra los viejos)
	@$(INSTANCIA)
	banner 'RESPALDO' "$(PROJECT_PROD)"
	respaldar
	if [ -n '$(RETENER)' ]; then podar '$(RETENER)'; fi
	rule
	printf '\n'

restaurar: ## Restaurar un respaldo: make restaurar desde=respaldos/<carpeta> (CON_CONFIG=1 incluye .env y secretos)
	@$(INSTANCIA)
	banner 'RESTAURAR' "$(PROJECT_PROD)"
	desde='$(desde)'
	desde=$${desde%/}
	revisar_respaldo "$$desde"
	rule
	if [ "$${CONFIRMAR:-}" != "$(PROJECT_PROD)" ]; then
		confirm "Esto reemplaza la base, las evidencias y la media de $(PROJECT_PROD)." "$(PROJECT_PROD)"
	fi
	rule
	printf '  %sRespaldo previo del estado actual%s\n' "$$C_DIM" "$$C_RESET"
	respaldar 'previo-restaurar'
	trap '[ $$? -eq 0 ] || printf "\n  %sEl estado anterior quedo en %s%s\n\n" "$$C_YELLOW" "$$RESPALDO_HECHO" "$$C_RESET"' EXIT
	rule
	restaurar_datos "$$desde"
	run_step 'Salud' esperar_salud
	trap - EXIT
	rule
	comparar_conteos "$$desde"
	row 'Previo' "$$RESPALDO_HECHO" "$$C_GREEN" 'por si hay que volver'
	rule
	printf '\n'

actualizar: ## Respaldar y desplegar: modo imagen con version=X.Y.Z, modo codigo con git pull (FORZAR=1 redespliega)
	@$(INSTANCIA)
	banner 'ACTUALIZAR' "$(PROJECT_PROD), modo $$MODO_ACTIVO"
	env_guard
	if [ "$$MODO_ACTIVO" = 'imagen' ]; then
		elegir_version '$(version)'
		if [ "$$NUEVA" = "$$ANTERIOR" ] && [ -z '$(FORZAR)' ]; then
			al_dia 'make actualizar version=X.Y.Z cambia de version; FORZAR=1 redespliega la misma'
			exit 0
		fi
		rule
		run_step 'Pull' bajar_version "$$NUEVA" \
			|| fail "Pull:no se pudieron bajar las imagenes de $$NUEVA" 'Revisa que la version este publicada; nada cambio'
	else
		revisar_git
		if [ "$$NUEVOS" -eq 0 ] && [ -z '$(FORZAR)' ]; then
			al_dia 'nada que actualizar; FORZAR=1 despliega igual'
			exit 0
		fi
	fi
	rule
	respaldar 'previo-actualizar'
	rule
	if [ "$$MODO_ACTIVO" = 'imagen' ]; then
		fijar_env VOBO_VERSION "$$NUEVA"
		fijar_env MODO_DESPLIEGUE imagen
		row 'Version' "$${ANTERIOR:-ninguna} -> $$NUEVA" "$$C_GREEN" '.env.production'
		desplegar=(VOBO_VERSION="$$NUEVA")
	else
		run_step 'Pull' git pull --ff-only --quiet
		row 'Codigo' "$$(git rev-parse --short "$$ANTES") -> $$(git rev-parse --short HEAD)" "$$C_GREEN"
		desplegar=(DEPLOY_SYNC=:)
	fi
	rule
	sano=1
	$(MAKE) deploy "$${desplegar[@]}" || sano=0
	if [ "$$sano" -eq 1 ]; then $(MAKE) _salud || sano=0; fi
	if [ "$$sano" -eq 0 ]; then
		if [ "$$MODO_ACTIVO" = 'imagen' ]; then como_volver_imagen "$${ANTERIOR:-<anterior>}"; else como_volver; fi
		exit 1
	fi
	row 'Previo' "$$RESPALDO_HECHO" "$$C_GREEN" 'por si hay que volver'
	rule
	printf '\n'

_salud:
	@$(INSTANCIA)
	run_step 'Salud' esperar_salud || fail 'Salud:la instancia no quedo sana' 'Revisa make logs y make status'
