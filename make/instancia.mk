.PHONY: instalar respaldo restaurar actualizar _salud

RESPALDOS_DIR ?= respaldos
INSTANCIA := $(LIB) && source make/instalar.sh && source make/respaldo.sh

export RESPALDOS_DIR

##@ Instancia

instalar: ## Instalar en este servidor: requisitos, .env.production, secretos, build y primer admin
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

actualizar: ## Respaldar, traer la rama actual con git pull y desplegar (FORZAR=1 despliega sin cambios)
	@$(INSTANCIA)
	banner 'ACTUALIZAR' "$(PROJECT_PROD)"
	env_guard
	revisar_git
	if [ "$$NUEVOS" -eq 0 ] && [ -z '$(FORZAR)' ]; then
		row 'Estado' 'al dia' "$$C_GREEN" 'nada que actualizar; FORZAR=1 despliega igual'
		rule
		printf '\n'
		exit 0
	fi
	rule
	respaldar 'previo-actualizar'
	rule
	run_step 'Pull' git pull --ff-only --quiet
	row 'Codigo' "$$(git rev-parse --short "$$ANTES") -> $$(git rev-parse --short HEAD)" "$$C_GREEN"
	rule
	sano=1
	$(MAKE) deploy DEPLOY_SYNC=: || sano=0
	if [ "$$sano" -eq 1 ]; then $(MAKE) _salud || sano=0; fi
	if [ "$$sano" -eq 0 ]; then como_volver; exit 1; fi
	row 'Previo' "$$RESPALDO_HECHO" "$$C_GREEN" 'por si hay que volver'
	rule
	printf '\n'

_salud:
	@$(INSTANCIA)
	run_step 'Salud' esperar_salud || fail 'Salud:la instancia no quedo sana' 'Revisa make logs y make status'
