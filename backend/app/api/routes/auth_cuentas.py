from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import Actor, get_actor
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import (
    CambioContrasena,
    DefinirCuenta,
    EnlacePublico,
    EntradaCuenta,
    ModoResponse,
    NuevaContrasena,
)
from app.services import cuentas_propias, intentos, sesiones
from app.services.cuentas_propias import ORIGEN

router = APIRouter(
    prefix="/api/auth",
    tags=["autenticacion"],
)

ERROR_GENERICO = "Correo o contraseña incorrectos"


def _solo_cuentas() -> None:
    if not settings.auth_cuentas:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No disponible")


PUBLICA = [Depends(_solo_cuentas), Depends(security.verificar_origen)]


def _abrir_sesion(db: Session, usuario: Usuario, response: Response) -> ModoResponse:
    segundos = int(security.duracion_sesion().total_seconds())
    sesion = sesiones.crear(
        db, usuario, {"access_token": ORIGEN, "expires_in": segundos}, origen=ORIGEN
    )
    security.emitir_cookie(response, sesion.id)
    return ModoResponse(modo=settings.auth_modo)


@router.post("/entrar", response_model=ModoResponse, dependencies=PUBLICA)
def entrar(
    entrada: EntradaCuenta, request: Request, response: Response, db: Session = Depends(get_db)
) -> ModoResponse:
    email = entrada.email.strip().lower()
    llaves = intentos.claves(email, intentos.ip_de(request))
    intentos.exigir_margen(db, llaves)
    usuario = cuentas_propias.autenticar(db, email, entrada.contrasena)
    if usuario is None:
        intentos.registrar_fallo(db, llaves)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=ERROR_GENERICO)
    intentos.olvidar(db, llaves[0])
    return _abrir_sesion(db, usuario, response)


@router.get(
    "/invitacion/{token}", response_model=EnlacePublico, dependencies=[Depends(_solo_cuentas)]
)
def ver_invitacion(token: str, db: Session = Depends(get_db)) -> EnlacePublico:
    return EnlacePublico(email=cuentas_propias.invitacion_vigente(db, token).email)


@router.post("/invitacion/{token}", response_model=ModoResponse, dependencies=PUBLICA)
def aceptar_invitacion(
    token: str, datos: DefinirCuenta, response: Response, db: Session = Depends(get_db)
) -> ModoResponse:
    usuario = cuentas_propias.aceptar_invitacion(db, token, datos.nombre, datos.contrasena)
    return _abrir_sesion(db, usuario, response)


@router.get(
    "/restablecer/{token}", response_model=EnlacePublico, dependencies=[Depends(_solo_cuentas)]
)
def ver_restablecimiento(token: str, db: Session = Depends(get_db)) -> EnlacePublico:
    encontrado = cuentas_propias.restablecimiento_vigente(db, token)
    usuario = db.get(Usuario, encontrado.usuario_id)
    return EnlacePublico(email=usuario.email if usuario else "")


@router.post("/restablecer/{token}", response_model=ModoResponse, dependencies=PUBLICA)
def restablecer(
    token: str, datos: NuevaContrasena, response: Response, db: Session = Depends(get_db)
) -> ModoResponse:
    usuario, cuenta = cuentas_propias.restablecer(db, token, datos.contrasena)
    if not cuenta.activa:
        return ModoResponse(modo=settings.auth_modo)
    return _abrir_sesion(db, usuario, response)


@router.post(
    "/contrasena", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(_solo_cuentas)]
)
def cambiar_contrasena(
    datos: CambioContrasena,
    request: Request,
    db: Session = Depends(get_db),
    actor: Actor = Depends(get_actor),
) -> None:
    usuario = db.get(Usuario, actor.usuario_id)
    llaves = intentos.claves(actor.email.lower(), intentos.ip_de(request))
    intentos.exigir_margen(db, llaves)
    try:
        cuentas_propias.cambiar(db, usuario, datos.actual, datos.nueva, actor.sesion_id)
    except HTTPException as error:
        if error.status_code == status.HTTP_400_BAD_REQUEST:
            intentos.registrar_fallo(db, llaves)
        raise
