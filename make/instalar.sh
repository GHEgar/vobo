declare -A ENV_NUEVO=()

interactivo() {
    [ -t 0 ] && [ -z "${NO_INTERACTIVO:-}" ]
}

preguntar() {
    local variable=$1 texto=$2 valor=${!1:-} omision=${3:-}
    if [ -z "$valor" ] && interactivo; then
        printf '  %s [%s]: ' "$texto" "$omision" >/dev/tty
        read -r valor </dev/tty || valor=''
    fi
    printf -v "$variable" '%s' "${valor:-$omision}"
}

preguntar_secreto() {
    local variable=$1 texto=$2 valor=${!1:-}
    if [ -z "$valor" ] && interactivo; then
        printf '  %s: ' "$texto" >/dev/tty
        read -rs valor </dev/tty || valor=''
        printf '\n' >/dev/tty
    fi
    printf -v "$variable" '%s' "$valor"
}

elegir() {
    local variable=$1 texto=$2 opciones=$3 omision=$4
    preguntar "$variable" "$texto ($opciones)" "$omision"
    case " ${opciones//\// } " in
        *" ${!variable} "*) ;;
        *) fail "Valor:$texto no admite '${!variable}'" "Opciones: $opciones" ;;
    esac
}

puerto_ocupado() {
    (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null
}

requisitos() {
    local version
    command -v docker >/dev/null 2>&1 || fail 'Docker:no esta instalado' 'Instalalo: https://docs.docker.com/engine/install/'
    docker info >/dev/null 2>&1 || fail 'Docker:el daemon no responde o no hay permiso' \
        'Arranca el servicio o agrega tu usuario al grupo docker'
    version=$(docker compose version --short 2>/dev/null || printf '')
    [ -n "$version" ] || fail 'Compose:falta docker compose v2' 'Instala el plugin docker-compose-plugin'
    [ "${version%%.*}" -ge 2 ] 2>/dev/null || fail "Compose:version $version" 'Se necesita docker compose v2 o mas reciente'
    command -v python3 >/dev/null 2>&1 || fail 'Python:falta python3' 'Se usa para los secretos y los manifiestos de respaldo'
    row 'Docker' "$(docker version --format '{{.Server.Version}}' 2>/dev/null)" "$C_GREEN"
    row 'Compose' "$version" "$C_GREEN"
}

revisar_compose_imagen() {
    local version
    version=$(docker compose version --short 2>/dev/null || printf '0')
    [ "$(printf '2.24.0\n%s\n' "$version" | sort -V | head -n 1)" = '2.24.0' ] \
        || fail "Compose:version $version" 'El modo imagen necesita docker compose 2.24 o mas reciente'
}

reunir_modo() {
    elegir MODO_DESPLIEGUE 'Como se despliega (imagen: descarga lo publicado; codigo: compila aqui)' 'imagen/codigo' 'imagen'
    ENV_NUEVO[MODO_DESPLIEGUE]=$MODO_DESPLIEGUE
    if [ "$MODO_DESPLIEGUE" = 'codigo' ]; then
        [ -f backend/Dockerfile ] || fail 'Modo:codigo necesita el repositorio completo' \
            'Clona el repositorio o instala con MODO_DESPLIEGUE=imagen'
        return 0
    fi
    revisar_compose_imagen
    preguntar VOBO_VERSION 'Version publicada a instalar' "$(version_local)"
    [ -n "$VOBO_VERSION" ] || fail 'Version:falta VOBO_VERSION' 'Indica una version publicada, p. ej. VOBO_VERSION=0.3.0'
    ENV_NUEVO[VOBO_VERSION]=$VOBO_VERSION
    ENV_NUEVO[VOBO_IMAGEN_BACKEND]=${VOBO_IMAGEN_BACKEND:-}
    ENV_NUEVO[VOBO_IMAGEN_WEB]=${VOBO_IMAGEN_WEB:-}
}

valor_env() {
    sed -n "s/^$1=//p" .env.production 2>/dev/null | tail -n 1
}

reunir_valores() {
    local sitio ip
    printf '\n  %sEnter acepta el valor entre corchetes.%s\n\n' "$C_DIM" "$C_RESET"
    reunir_modo
    preguntar DOMINIO 'Dominio o IP con que se entra' "$(hostname -f 2>/dev/null || hostname)"
    elegir HTTPS 'Se entra por HTTPS (un proxy pone el certificado)' 'si/no' 'si'
    preguntar NGINX_PORT 'Puerto donde escucha la app en este servidor' '80'
    [[ $NGINX_PORT =~ ^[0-9]+$ ]] || fail "Puerto:'$NGINX_PORT' no es un numero"
    puerto_ocupado "$NGINX_PORT" && fail "Puerto:$NGINX_PORT ya esta ocupado" 'Elige otro puerto o libera ese'
    elegir AUTH_MODO 'Como se entra' 'cuentas/oidc/ambos' 'cuentas'
    elegir CONTENIDO_FUENTE 'Donde vive el contenido' 'base/archivos' 'base'
    preguntar COMPOSE_NOMBRE 'Nombre del proyecto de compose' 'vobo'
    if [ "$HTTPS" = 'si' ]; then
        sitio='https://${DOMINIO}'
        ENV_NUEVO[SESSION_COOKIE_SECURE]=true
    else
        sitio='http://${DOMINIO}'
        [ "$NGINX_PORT" = '80' ] || sitio="$sitio:$NGINX_PORT"
        ENV_NUEVO[SESSION_COOKIE_SECURE]=false
    fi
    ip=$(hostname -I 2>/dev/null | awk '{print $1}')
    ENV_NUEVO[APP_ENV]=prod
    ENV_NUEVO[AUTH_MODO]=$AUTH_MODO
    ENV_NUEVO[DOMINIO]=$DOMINIO
    ENV_NUEVO[DOMINIO_IDP]=''
    ENV_NUEVO[SITIO]=$sitio
    ENV_NUEVO[VM_IP]=${VM_IP:-${ip:-127.0.0.1}}
    ENV_NUEVO[NGINX_BIND_ADDR]=${NGINX_BIND_ADDR:-0.0.0.0}
    ENV_NUEVO[NGINX_PORT]=$NGINX_PORT
    ENV_NUEVO[COMPOSE_NOMBRE]=$COMPOSE_NOMBRE
    ENV_NUEVO[VOLUMEN_DATOS]=${VOLUMEN_DATOS:-${COMPOSE_NOMBRE}_datos}
    ENV_NUEVO[VOLUMEN_EVIDENCIAS]=${VOLUMEN_EVIDENCIAS:-${COMPOSE_NOMBRE}_evidencias}
    ENV_NUEVO[VOLUMEN_MEDIA]=${VOLUMEN_MEDIA:-${COMPOSE_NOMBRE}_media}
    ENV_NUEVO[CONTENIDO_DIR]=${CONTENIDO_DIR:-./ejemplo/contenido}
    ENV_NUEVO[CONTENIDO_FUENTE]=$CONTENIDO_FUENTE
    ENV_NUEVO[TEMA_DIR]=${TEMA_DIR:-}
    if [ "$AUTH_MODO" != 'cuentas' ]; then
        reunir_oidc
    fi
    if [ "$AUTH_MODO" != 'oidc' ]; then
        preguntar ADMIN_EMAIL 'Correo del primer administrador (vacio para despues)' ''
    fi
}

reunir_oidc() {
    preguntar OIDC_ISSUER_URL 'URL del proveedor OIDC vista desde el servidor' ''
    preguntar OIDC_PUBLIC_URL 'URL del proveedor vista desde el navegador (vacia si es la misma)' ''
    preguntar OIDC_CLIENT_ID 'client_id de la app en el proveedor' 'vobo'
    preguntar OIDC_AUDIENCE 'aud que trae el access token' "$OIDC_CLIENT_ID"
    preguntar_secreto OIDC_CLIENT_SECRET 'client_secret (no se muestra)'
    [ -n "$OIDC_ISSUER_URL" ] || fail 'OIDC:falta OIDC_ISSUER_URL' 'Es obligatoria con AUTH_MODO oidc o ambos'
    ENV_NUEVO[OIDC_ISSUER_URL]=$OIDC_ISSUER_URL
    ENV_NUEVO[OIDC_PUBLIC_URL]=$OIDC_PUBLIC_URL
    ENV_NUEVO[OIDC_CLIENT_ID]=$OIDC_CLIENT_ID
    ENV_NUEVO[OIDC_AUDIENCE]=$OIDC_AUDIENCE
    ENV_NUEVO[OIDC_REDIRECT_URI]='${SITIO}/api/auth/callback'
    if [ -n "$OIDC_CLIENT_SECRET" ]; then
        (umask 077; printf '%s\n' "$OIDC_CLIENT_SECRET" > secrets/oidc_client_secret)
        row 'Secreto' 'guardado' "$C_GREEN" 'secrets/oidc_client_secret'
    fi
}

escribir_env() {
    local linea clave
    while IFS= read -r linea || [ -n "$linea" ]; do
        clave=${linea%%=*}
        if [[ $linea =~ ^[A-Z_]+= ]] && [ -n "${ENV_NUEVO[$clave]+x}" ]; then
            printf '%s=%s\n' "$clave" "${ENV_NUEVO[$clave]}"
        elif [[ $linea =~ ^[A-Z_]+=\< ]]; then
            printf '%s=\n' "$clave"
        else
            printf '%s\n' "$linea"
        fi
    done < .env.production.example > .env.production.nuevo
    chmod 600 .env.production.nuevo
    mv .env.production.nuevo .env.production
    row 'Env' 'creado' "$C_GREEN" '.env.production'
}

revisar_volumenes() {
    local clave nombre
    for clave in VOLUMEN_DATOS VOLUMEN_EVIDENCIAS VOLUMEN_MEDIA; do
        nombre=$(valor_env "$clave")
        if [ -n "$nombre" ] && docker volume inspect "$nombre" >/dev/null 2>&1; then
            row 'Volumen' 'ya existe' "$C_YELLOW" "$nombre: se usan sus datos"
        fi
    done
}

revisar_puerto() {
    local puerto proyecto
    puerto=$(valor_env NGINX_PORT)
    proyecto=$(valor_env COMPOSE_NOMBRE)
    if project_running "${proyecto:-$PROJECT_PROD}"; then
        row 'Puerto' "$puerto" "$C_GREEN" 'en uso por esta instancia'
    elif puerto_ocupado "$puerto"; then
        fail "Puerto:$puerto ya esta ocupado" 'Elige otro con NGINX_PORT en .env.production'
    else
        row 'Puerto' "$puerto" "$C_GREEN" 'libre'
    fi
}

preparar_instalacion() {
    banner 'INSTALAR' 'produccion'
    requisitos
    rule
    if [ -f .env.production ]; then
        row 'Env' 'ya existe' "$C_YELLOW" '.env.production no se toca'
        if interactivo; then
            local seguir
            printf '  Continuar con el .env.production actual? [s/N]: ' >/dev/tty
            read -r seguir </dev/tty || seguir=''
            case $seguir in
                s|S|si|SI) ;;
                *) printf '  %sNada cambio.%s\n\n' "$C_GREEN" "$C_RESET"; exit 0 ;;
            esac
        fi
        ADMIN_EMAIL=${ADMIN_EMAIL:-}
    else
        reunir_valores
        rule
        escribir_env
    fi
    revisar_puerto
    revisar_volumenes
    crear_secretos
    proteger_secretos
    rule
}

esperar_salud() {
    local limite=${1:-240} inicio id estado pendiente
    local -a ids
    inicio=$(date +%s)
    while :; do
        pendiente=0
        mapfile -t ids < <(dc prod ps -a -q 2>/dev/null)
        [ ${#ids[@]} -gt 0 ] || pendiente=1
        for id in "${ids[@]}"; do
            estado=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$id")
            [ "$estado" = 'healthy' ] || pendiente=1
        done
        [ "$pendiente" -eq 0 ] && return 0
        [ $(( $(date +%s) - inicio )) -lt "$limite" ] || return 1
        sleep 2
    done
}

mostrar_entrada() {
    local sitio
    sitio=$(dc prod config --format json 2>/dev/null \
        | python3 -c 'import json, sys; e = json.load(sys.stdin)["services"]["backend"]["environment"]; print(e.get("FRONTEND_URL", ""))' \
        2>/dev/null || printf '')
    row 'Entrada' "${sitio:-sin url}" "$C_GREEN"
}
