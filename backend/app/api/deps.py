import hmac
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core import oidc, security
from app.core.config import settings
from app.core.database import get_db
from app.core.permisos import GESTIONAR_FALLAS, VER_TABLERO
from app.models.proyecto import Proyecto
from app.models.usuario import Sesion, Usuario
from app.services import accesos, proyectos, roles, sesiones

EMAIL_TOKEN_LECTURA = "token-de-lectura"

_bearer = HTTPBearer(auto_error=False)


@dataclass
class Actor:
    email: str
    nombre: str
    permisos: frozenset[str] = field(default_factory=frozenset)
    sesion_id: str | None = None
    paginas: frozenset[str] = field(default_factory=frozenset)
    usuario_id: int | None = None
    origen: str = "oidc"

    def puede(self, permiso: str) -> bool:
        return permiso in self.permisos

    def ve(self, pagina: str) -> bool:
        return pagina in self.paginas


def _prohibido(permiso: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail=f"Requiere permiso: {permiso}"
    )


async def _del_proveedor(sesion: Sesion) -> tuple[set[str], set[str]]:
    if sesion.origen == "cuenta":
        return set(), set()
    if sesion.permisos_locales is not None:
        return set(sesion.permisos_locales), set()
    return await oidc.permisos_y_grupos(sesion.access_token)


async def get_actor(request: Request, db: Session = Depends(get_db)) -> Actor:
    sesion = await sesiones.vigente(db, request.cookies.get(security.COOKIE_SESION))
    security.verificar_csrf(request, sesion.id)
    del_proveedor, grupos = await _del_proveedor(sesion)
    usuario = db.get(Usuario, sesion.usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado"
        )
    permisos = roles.efectivos(db, usuario.id, del_proveedor, grupos)
    if usuario.permisos != sorted(permisos):
        usuario.permisos = sorted(permisos)
        db.commit()
    efectivas = accesos.efectivas(frozenset(permisos), accesos.otorgadas(db, usuario.email))
    return Actor(
        email=usuario.email,
        nombre=usuario.nombre,
        permisos=frozenset(permisos),
        sesion_id=sesion.id,
        paginas=frozenset(efectivas),
        usuario_id=usuario.id,
        origen=sesion.origen,
    )


def require_permission(permiso: str) -> Callable[..., Awaitable[Actor]]:
    async def dependencia(actor: Actor = Depends(get_actor)) -> Actor:
        if not actor.puede(permiso):
            raise _prohibido(permiso)
        return actor

    return dependencia


def require_alguno(*permisos: str) -> Callable[..., Awaitable[Actor]]:
    async def dependencia(actor: Actor = Depends(get_actor)) -> Actor:
        if not any(actor.puede(p) for p in permisos):
            raise _prohibido(" o ".join(permisos))
        return actor

    return dependencia


SEGUIMIENTO = require_alguno(VER_TABLERO, GESTIONAR_FALLAS)


def _actor_de_token(credenciales: HTTPAuthorizationCredentials) -> Actor:
    esperado = settings.validacion_lectura_token
    if not esperado or not hmac.compare_digest(credenciales.credentials, esperado):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de lectura inválido"
        )
    return Actor(email=EMAIL_TOKEN_LECTURA, nombre="Token de lectura")


async def lectura_o_sesion(
    request: Request,
    credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> Actor:
    if credenciales is not None:
        return _actor_de_token(credenciales)
    return await get_actor(request, db)


def lectura_o_permiso(permiso: str, pagina: str | None = None) -> Callable[..., Awaitable[Actor]]:
    async def dependencia(
        request: Request,
        credenciales: HTTPAuthorizationCredentials | None = Depends(_bearer),
        db: Session = Depends(get_db),
    ) -> Actor:
        if credenciales is not None:
            return _actor_de_token(credenciales)
        actor = await get_actor(request, db)
        if not actor.puede(permiso) and not (pagina and actor.ve(pagina)):
            raise _prohibido(permiso)
        return actor

    return dependencia


def proyecto_actual(
    ronda: int | None = Query(default=None),
    proyecto: str | None = Query(default=None, max_length=60),
    db: Session = Depends(get_db),
) -> Proyecto:
    return proyectos.resolver(db, ronda, proyecto)
