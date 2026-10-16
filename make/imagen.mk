.PHONY: kit

KIT_DIR ?= dist

##@ Distribucion

kit: ## Empaquetar el kit para instalar desde imagenes: make kit version=X.Y.Z (por omision la de package.json)
	@$(LIB) && source make/imagen.sh
	banner 'KIT' 'instalacion desde imagenes'
	empaquetar_kit '$(version)' '$(KIT_DIR)'
	rule
	printf '\n'
