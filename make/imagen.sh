KIT_ARCHIVOS='LICENSE README.md Makefile compose.yaml compose.prod.yaml compose.imagen.yaml
.env.production.example make ejemplo frontend/public/tema docs/CHANGELOG.md secrets/.gitkeep secrets/*.example'
SEMVER='^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$'

version_local() {
    if [ -f VERSION ]; then
        tr -d '[:space:]' < VERSION
    elif [ -f frontend/package.json ]; then
        python3 -c 'import json; print(json.load(open("frontend/package.json"))["version"])'
    fi
}

fijar_env() {
    local clave=$1 valor=$2 nuevo
    nuevo=$(mktemp .env.production.XXXXXX)
    awk -v c="$clave" -v v="$valor" \
        'index($0, c "=") == 1 { print c "=" v; hecho = 1; next } { print } END { if (!hecho) print c "=" v }' \
        .env.production > "$nuevo"
    chmod 600 "$nuevo"
    mv "$nuevo" .env.production
}

elegir_version() {
    ANTERIOR=$(valor_env VOBO_VERSION)
    NUEVA=${1:-$ANTERIOR}
    [ -n "$NUEVA" ] || fail 'Version:falta version' 'Uso: make actualizar version=X.Y.Z'
    [[ $NUEVA =~ $SEMVER ]] || row 'Version' "$NUEVA" "$C_YELLOW" 'no es X.Y.Z'
    row 'Actual' "${ANTERIOR:-ninguna}" "$C_GREEN"
    row 'Destino' "$NUEVA" "$C_GREEN"
}

bajar_version() {
    VOBO_VERSION=$1 dc prod pull --policy missing
}

al_dia() {
    row 'Estado' 'al dia' "$C_GREEN" "$1"
    rule
    printf '\n'
}

como_volver_imagen() {
    printf '\n  %sLa actualizacion no quedo sana. Nada se revirtio solo.%s\n\n' "$C_RED" "$C_RESET"
    printf '  Volver a la version anterior:\n'
    printf '    make actualizar version=%s\n\n' "$1"
    printf '  Si la base ya quedo migrada y la anterior no arranca, restaurar despues el respaldo previo:\n'
    printf '    make restaurar desde=%s\n\n' "$RESPALDO_HECHO"
}

empaquetar_kit() {
    local version=${1:-$(version_local)} destino=$2 nombre temporal archivo
    [[ $version =~ $SEMVER ]] || fail "Version:'$version' no es X.Y.Z" 'Uso: make kit version=X.Y.Z'
    command -v git >/dev/null 2>&1 || fail 'Git:falta git' 'El kit se arma desde un clon del repositorio'
    nombre="vobo-kit-$version"
    temporal=$(mktemp -d)
    mkdir -p "$temporal/$nombre" "$destino"
    git ls-files -z --cached --others --exclude-standard -- $KIT_ARCHIVOS \
        | tar --null -T - -cf - | tar -xf - -C "$temporal/$nombre"
    printf '%s\n' "$version" > "$temporal/$nombre/VERSION"
    archivo="$destino/$nombre.tar.gz"
    tar -C "$temporal" --owner=0 --group=0 --numeric-owner -czf "$archivo" "$nombre"
    rm -rf "$temporal"
    (cd "$destino" && sha256sum "$nombre.tar.gz" > "$nombre.tar.gz.sha256")
    row 'Kit' "$archivo" "$C_GREEN" "$(du -h "$archivo" | cut -f1)"
    row 'Suma' "$archivo.sha256" "$C_GREEN"
}
