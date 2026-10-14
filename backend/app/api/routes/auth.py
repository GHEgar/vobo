from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.api.deps import Actor, get_actor
from app.core import oidc, security
from app.core.config import settings
from app.core.database import get_db
from app.models.usuario import Sesion
from app.schemas.auth import (
    EntradaLocal,
    ModoResponse,
    SalidaResponse,
    SesionResponse,
    UsuarioLocal,
    UsuarioSesion,
)
from app.services import sesiones
from app.services.usuarios_locales import USUARIOS_LOCALES, por_clave

router = APIRouter(prefix="/api/auth", tags=["autenticacion"])

COOKIE_REINTENTO = "validacion_oidc_reintento"


def _solo_local() -> None:
    if not settings.auth_local:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No disponible")


def _solo_oidc() -> None:
    if settings.auth_local:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No disponible")


@router.get("/modo", response_model=ModoResponse)
def modo() -> ModoResponse:
    return ModoResponse(modo=settings.auth_modo)


@router.get("/login", dependencies=[Depends(_solo_oidc)])
async def login() -> RedirectResponse:
    try:
        solicitud = await oidc.solicitud_de_autorizacion()
    except oidc.ErrorOIDC:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo iniciar sesión; intenta de nuevo en un momento",
        ) from None
    respuesta = RedirectResponse(url=solicitud.url, status_code=status.HTTP_302_FOUND)
    security.guardar_transaccion(
        respuesta, {"estado": solicitud.state, "verificador": solicitud.code_verifier}
    )
    return respuesta


@router.get("/callback", dependencies=[Depends(_solo_oidc)])
async def callback(
    request: Request, code: str = "", state: str = "", db: Session = Depends(get_db)
) -> RedirectResponse:
    transaccion = security.leer_transaccion(request)
    if not transaccion and code and not request.cookies.get(COOKIE_REINTENTO):
        reintento = RedirectResponse(url="/api/auth/login", status_code=status.HTTP_302_FOUND)
        reintento.set_cookie(
            COOKIE_REINTENTO, "1", max_age=60, path=security.COOKIE_PATH, httponly=True
        )
        return reintento
    if not transaccion or not code or not state or state != transaccion.get("estado"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado OIDC inválido")
    try:
        tokens = await oidc.canjear_codigo(code, transaccion["verificador"])
    except oidc.ErrorOIDC:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo completar el inicio de sesión",
        ) from None
    claims = await oidc.validar_access_token(tokens["access_token"])
    usuario = sesiones.resolver_usuario(db, claims)
    sesion = sesiones.crear(db, usuario, tokens)
    respuesta = RedirectResponse(url=f"{settings.frontend_url}/", status_code=status.HTTP_302_FOUND)
    security.borrar_transaccion(respuesta)
    respuesta.delete_cookie(COOKIE_REINTENTO, path=security.COOKIE_PATH)
    security.emitir_cookie(respuesta, sesion.id)
    return respuesta


@router.get(
    "/usuarios-locales",
    response_model=list[UsuarioLocal],
    dependencies=[Depends(_solo_local)],
)
def usuarios_locales() -> list[UsuarioLocal]:
    return [
        UsuarioLocal(clave=u.clave, nombre=u.nombre, email=u.email, rol=u.rol)
        for u in USUARIOS_LOCALES
    ]


@router.post(
    "/local",
    response_model=ModoResponse,
    dependencies=[Depends(_solo_local), Depends(security.verificar_origen)],
)
def entrar_local(
    entrada: EntradaLocal, response: Response, db: Session = Depends(get_db)
) -> ModoResponse:
    prueba = por_clave(entrada.clave)
    if prueba is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Usuario de prueba no encontrado"
        )
    usuario = sesiones.resolver_usuario_local(db, prueba)
    sesion = sesiones.crear(
        db, usuario, {"access_token": "local", "expires_in": 86400}, sorted(prueba.permisos)
    )
    security.emitir_cookie(response, sesion.id)
    return ModoResponse(modo="local")


@router.get("/me", response_model=SesionResponse)
def me(response: Response, actor: Actor = Depends(get_actor)) -> SesionResponse:
    response.headers["Cache-Control"] = "no-store"
    return SesionResponse(
        csrf_token=security.csrf_de(actor.sesion_id or ""),
        usuario=UsuarioSesion(
            email=actor.email,
            nombre=actor.nombre,
            permisos=sorted(actor.permisos),
            paginas=sorted(actor.paginas),
        ),
    )


@router.post(
    "/logout",
    response_model=SalidaResponse,
    dependencies=[Depends(security.verificar_origen)],
)
async def logout(
    request: Request, response: Response, db: Session = Depends(get_db)
) -> SalidaResponse:
    sesion = db.get(Sesion, request.cookies.get(security.COOKIE_SESION) or "")
    if sesion is not None:
        if sesion.refresh_token and sesion.permisos_locales is None:
            await oidc.revocar(sesion.refresh_token)
        sesiones.cerrar(db, sesion)
    security.borrar_cookie(response)
    return SalidaResponse(logout_url=oidc.url_de_salida())
