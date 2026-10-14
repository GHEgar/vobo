SECRETOS='secret_key oidc_client_secret validacion_lectura_token'
OPCIONALES='validacion_cuentas'

env_guard() {
    if [ ! -f .env.production ]; then
        fail 'Env:falta .env.production' \
             'Crealo desde la plantilla y llenalo: cp .env.production.example .env.production'
    fi
    local nombre
    for nombre in $SECRETOS; do
        if [ ! -s "secrets/$nombre" ]; then
            fail "Secretos:falta secrets/$nombre" \
                 "Su contenido esta descrito en secrets/$nombre.example; make setup crea los que faltan"
        fi
    done
    for nombre in $OPCIONALES; do
        if [ ! -f "secrets/$nombre" ]; then
            fail "Secretos:falta secrets/$nombre" \
                 "Puede ir vacio; su formato esta en secrets/$nombre.example; make setup lo crea"
        fi
    done
    row 'Env' '.env.production' "$C_GREEN"
}

crear_secretos() {
    local nombre
    for nombre in $OPCIONALES; do
        if [ ! -f "secrets/$nombre" ]; then
            (umask 077; : > "secrets/$nombre")
            row 'Secreto' 'creado vacio' "$C_GREEN" "secrets/$nombre"
        fi
    done
    for nombre in $SECRETOS; do
        if [ ! -s "secrets/$nombre" ]; then
            (umask 077; python3 -c 'import secrets; print(secrets.token_urlsafe(32))' > "secrets/$nombre")
            row 'Secreto' 'creado' "$C_GREEN" "secrets/$nombre"
        fi
    done
}

proteger_secretos() {
    docker run --rm -v "$PWD/secrets":/s alpine sh -c \
        'chgrp 10001 /s && chmod 750 /s && find /s -type f ! -name "*.example" ! -name ".gitkeep" -exec chgrp 10001 {} + -exec chmod 640 {} +' \
        >/dev/null 2>&1 || chmod 600 secrets/* 2>/dev/null || true
}
