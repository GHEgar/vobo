BASE_SQLITE=/data/validacion.sqlite3
RESPALDO_HECHO=''

backend_activo() {
    [ -n "$(dc prod ps --status running -q backend 2>/dev/null)" ]
}

en_backend() {
    if backend_activo; then
        dc prod exec -T backend "$@"
    else
        dc prod run --rm --no-deps -T backend "$@"
    fi
}

volcar_base() {
    en_backend python -c "import os, shutil, sqlite3, sys, tempfile
ruta = '$BASE_SQLITE'
if not os.path.exists(ruta):
    sys.exit('no hay base en ' + ruta)
carpeta = tempfile.mkdtemp()
copia = os.path.join(carpeta, 'copia.sqlite3')
origen = sqlite3.connect(ruta)
destino = sqlite3.connect(copia)
origen.backup(destino)
destino.execute('PRAGMA journal_mode=DELETE')
destino.close()
origen.close()
with open(copia, 'rb') as archivo:
    shutil.copyfileobj(archivo, sys.stdout.buffer)
shutil.rmtree(carpeta)" > "$1"
    [ -s "$1" ]
}

volcar_tar() {
    local origen=$1 destino=$2
    shift 2
    en_backend sh -c 'o=$1; shift; if [ -d "$o" ]; then exec tar -C "$o" "$@" -cf - .; else exec tar -cf - -T /dev/null; fi' sh "$origen" "$@" > "$destino"
}

volcar_datos() {
    volcar_tar /data "$1" --exclude=./validacion.sqlite3 \
        --exclude=./validacion.sqlite3-wal --exclude=./validacion.sqlite3-shm
}

volcar_config() {
    local -a archivos=(.env.production)
    local secreto
    for secreto in secrets/*; do
        case $secreto in *.example|*/.gitkeep) ;; *) [ -f "$secreto" ] && archivos+=("$secreto") ;; esac
    done
    tar -cf "$1" "${archivos[@]}"
}

respaldar() {
    local etiqueta=${1:-} carpeta version commit
    carpeta="$RESPALDOS_DIR/$(date +%Y%m%d-%H%M%S)${etiqueta:+-$etiqueta}"
    [ -f .env.production ] || fail 'Env:falta .env.production' 'Respaldar necesita una instancia instalada'
    (umask 077; mkdir -p "$RESPALDOS_DIR" "$carpeta")
    chmod 700 "$RESPALDOS_DIR" "$carpeta"
    row 'Carpeta' "$carpeta" "$C_GREEN"
    run_step 'Base' volcar_base "$carpeta/base.sqlite3"
    run_step 'Datos' volcar_datos "$carpeta/datos.tar"
    run_step 'Evidencias' volcar_tar /evidencias "$carpeta/evidencias.tar"
    run_step 'Media' volcar_tar /contenido-media "$carpeta/media.tar"
    run_step 'Config' volcar_config "$carpeta/config.tar"
    version=$(en_backend printenv APP_VERSION 2>/dev/null || printf '')
    commit=''
    [ "${MODO_ACTIVO:-codigo}" = 'imagen' ] || commit=$(git rev-parse HEAD 2>/dev/null || printf '')
    run_step 'Manifiesto' python3 make/manifiesto.py crear "$carpeta" \
        --proyecto "$PROJECT_PROD" --version "$version" --git "$commit"
    chmod 600 "$carpeta"/*
    row 'Tamano' "$(du -sh "$carpeta" | cut -f1)" "$C_GREEN"
    RESPALDO_HECHO=$carpeta
}

podar() {
    local dias=$1 carpeta borradas=0
    [[ $dias =~ ^[0-9]+$ ]] || fail "Retener:'$dias' no es un numero de dias"
    [ -d "$RESPALDOS_DIR" ] || return 0
    while IFS= read -r carpeta; do
        [ -f "$carpeta/manifiesto.json" ] || continue
        [ "$carpeta" = "$RESPALDO_HECHO" ] && continue
        rm -rf "$carpeta"
        borradas=$((borradas + 1))
    done < <(find "$RESPALDOS_DIR" -mindepth 1 -maxdepth 1 -type d -mmin "+$((dias * 1440))")
    row 'Retencion' "$dias dias" "$C_GREEN" "$borradas respaldo(s) borrado(s)"
}

cargar_tar() {
    en_backend sh -c 'find "$0" -mindepth 1 -delete && tar -xf - -C "$0"' "$1" < "$2"
}

cargar_base() {
    en_backend sh -c 'rm -f "$0" "$0-wal" "$0-shm" && cat > "$0"' "$BASE_SQLITE" < "$1"
}

revision_conocida() {
    if [ "${MODO_ACTIVO:-codigo}" = 'imagen' ]; then
        en_backend sh -c 'ls alembic/versions/"$0"_*.py' "$1" >/dev/null 2>&1
    else
        compgen -G "backend/alembic/versions/${1}_*.py" >/dev/null
    fi
}

revisar_respaldo() {
    local desde=$1 revision
    [ -n "$desde" ] || fail 'Origen:falta desde' 'Uso: make restaurar desde=respaldos/<carpeta>'
    [ -f "$desde/manifiesto.json" ] || fail "Origen:$desde no tiene manifiesto.json" \
        'Indica una carpeta creada por make respaldo'
    run_step 'sha256' python3 make/manifiesto.py verificar "$desde" \
        || fail 'Integridad:el respaldo no coincide con su manifiesto' 'No se toco nada'
    revision=$(python3 make/manifiesto.py campo "$desde" alembic)
    if [ -n "$revision" ] && ! revision_conocida "$revision"; then
        fail "Version:el respaldo es de una version mas nueva (revision $revision)" \
             'Pasa a esa version antes de restaurarlo (make actualizar)'
    fi
    row 'Creado' "$(python3 make/manifiesto.py campo "$desde" creado)" "$C_GREEN"
    row 'Proyecto' "$(python3 make/manifiesto.py campo "$desde" proyecto)" "$C_GREEN"
    row 'Revision' "${revision:-ninguna}" "$C_GREEN"
}

restaurar_datos() {
    local desde=$1
    run_step 'Stop' dc prod stop
    if [ -n "${CON_CONFIG:-}" ]; then
        run_step 'Config' tar -xf "$desde/config.tar"
        proteger_secretos
    fi
    run_step 'Datos' cargar_tar /data "$desde/datos.tar"
    run_step 'Base' cargar_base "$desde/base.sqlite3"
    run_step 'Evidencias' cargar_tar /evidencias "$desde/evidencias.tar"
    run_step 'Media' cargar_tar /contenido-media "$desde/media.tar"
    run_step 'Up' dc prod up -d
}

comparar_conteos() {
    local desde=$1 actual tabla esperado ahora marca distintas=0
    actual=$(mktemp)
    if ! volcar_base "$actual"; then
        rm -f "$actual"
        row 'Conteos' 'sin leer' "$C_YELLOW" 'no se pudo copiar la base restaurada'
        return 0
    fi
    while IFS=$'\t' read -r tabla esperado ahora marca; do
        if [ "$marca" = 'igual' ]; then
            printf '  %-28s%s%6s%s\n' "$tabla" "$C_GREEN" "$ahora" "$C_RESET"
        else
            printf '  %-28s%s%6s%s  el respaldo tenia %s\n' "$tabla" "$C_YELLOW" "$ahora" "$C_RESET" "$esperado"
            distintas=$((distintas + 1))
        fi
    done < <(python3 make/manifiesto.py comparar "$desde" "$actual")
    rm -f "$actual"
    rule
    if [ "$distintas" -eq 0 ]; then
        row 'Conteos' 'iguales' "$C_GREEN" 'coinciden con el manifiesto'
    else
        row 'Conteos' "$distintas distinta(s)" "$C_YELLOW" 'una migracion nueva puede agregar filas'
    fi
}

revisar_git() {
    [ -d .git ] || fail 'Git:esta carpeta no es un repo git' 'Actualiza a mano o clona el repositorio'
    RAMA=$(git branch --show-current 2>/dev/null || printf '')
    [ -n "$RAMA" ] || fail 'Git:HEAD detached' 'Vuelve a una rama con: git checkout <rama>'
    git rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1 \
        || fail "Git:$RAMA no tiene upstream" "Configuralo con: git branch --set-upstream-to=origin/$RAMA"
    [ -z "$(git status --porcelain --untracked-files=no)" ] \
        || fail 'Git:hay cambios locales sin commitear' 'Guardalos o descartalos antes de actualizar: git status'
    ANTES=$(git rev-parse HEAD)
    run_step 'Fetch' git fetch --quiet
    NUEVOS=$(git rev-list --count 'HEAD..@{u}')
    row 'Rama' "$RAMA" "$C_GREEN" "$(git rev-parse --short HEAD), $NUEVOS commit(s) nuevos"
}

como_volver() {
    printf '\n  %sLa actualizacion no quedo sana. Nada se revirtio solo.%s\n\n' "$C_RED" "$C_RESET"
    printf '  Volver al codigo anterior:\n'
    printf '    git checkout %s && make deploy DEPLOY_SYNC=:\n\n' "$ANTES"
    printf '  Si ademas la base quedo mal, restaurar el respaldo previo:\n'
    printf '    make restaurar desde=%s\n\n' "$RESPALDO_HECHO"
    printf '  Para regresar a la rama despues: git checkout %s\n\n' "$RAMA"
}
