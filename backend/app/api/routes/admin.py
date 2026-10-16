from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import Actor, require_permission
from app.core.config import settings
from app.core.database import get_db
from app.core.permisos import ADMINISTRAR, CATALOGO
from app.models.cuenta import Cuenta
from app.models.rol import Rol
from app.models.usuario import Usuario
from app.schemas.admin import (
    CuentaResumen,
    EnlaceResponse,
    EstadoCuenta,
    InvitacionCrear,
    InvitacionItem,
    PermisoItem,
    PersonaItem,
    RolCambios,
    RolCrear,
    RolesDePersona,
    RolItem,
)
from app.services import cuentas_propias, roles

router = APIRouter(prefix="/api/admin", tags=["administracion"])

admin = require_permission(ADMINISTRAR)


def _con_cuentas() -> None:
    if not settings.auth_cuentas:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Las cuentas propias no están habilitadas en esta instancia",
        )


def _usuario_o_404(db: Session, usuario_id: int) -> Usuario:
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona no encontrada")
    return usuario


def _persona(usuario: Usuario, claves: list[str], cuenta: Cuenta | None) -> PersonaItem:
    return PersonaItem(
        id=usuario.id,
        email=usuario.email,
        nombre=usuario.nombre,
        ultimo_acceso=usuario.ultimo_acceso,
        oidc=bool(usuario.sub_oidc),
        roles=claves,
        cuenta=CuentaResumen.model_validate(cuenta) if cuenta else None,
    )


@router.get("/permisos", response_model=list[PermisoItem])
def listar_permisos(_actor: Actor = Depends(admin)) -> list[PermisoItem]:
    return [PermisoItem(clave=c, descripcion=d) for c, d in CATALOGO.items()]


@router.get("/roles", response_model=list[RolItem])
def listar_roles(db: Session = Depends(get_db), _actor: Actor = Depends(admin)) -> list[Rol]:
    return roles.listar(db)


@router.post("/roles", response_model=RolItem, status_code=status.HTTP_201_CREATED)
def crear_rol(
    datos: RolCrear, db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> Rol:
    return roles.crear(db, datos)


@router.patch("/roles/{rol_id}", response_model=RolItem)
def actualizar_rol(
    rol_id: int, datos: RolCambios, db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> Rol:
    return roles.actualizar(db, roles.obtener_o_404(db, rol_id), datos)


@router.delete("/roles/{rol_id}", status_code=status.HTTP_204_NO_CONTENT)
def borrar_rol(rol_id: int, db: Session = Depends(get_db), _actor: Actor = Depends(admin)) -> None:
    roles.borrar(db, roles.obtener_o_404(db, rol_id))


@router.get("/personas", response_model=list[PersonaItem])
def listar_personas(
    response: Response, db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> list[PersonaItem]:
    response.headers["Cache-Control"] = "no-store"
    claves = roles.claves_por_usuario(db)
    cuentas = {c.usuario_id: c for c in db.scalars(select(Cuenta))}
    usuarios = db.scalars(select(Usuario).order_by(Usuario.nombre, Usuario.email))
    return [_persona(u, claves.get(u.id, []), cuentas.get(u.id)) for u in usuarios]


@router.put("/personas/{usuario_id}/roles", response_model=PersonaItem)
def asignar_roles(
    usuario_id: int,
    datos: RolesDePersona,
    db: Session = Depends(get_db),
    _actor: Actor = Depends(admin),
) -> PersonaItem:
    usuario = _usuario_o_404(db, usuario_id)
    claves = roles.asignar(db, usuario, datos.roles)
    return _persona(usuario, claves, cuentas_propias.cuenta_de(db, usuario.id))


@router.patch("/personas/{usuario_id}/cuenta", response_model=PersonaItem)
def cambiar_estado_cuenta(
    usuario_id: int,
    datos: EstadoCuenta,
    db: Session = Depends(get_db),
    actor: Actor = Depends(admin),
) -> PersonaItem:
    usuario = _usuario_o_404(db, usuario_id)
    if usuario.id == actor.usuario_id and not datos.activa:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="No puedes desactivar tu propia cuenta"
        )
    cuenta = cuentas_propias.fijar_activa(db, usuario, datos.activa)
    return _persona(usuario, roles.claves_por_usuario(db).get(usuario.id, []), cuenta)


@router.post("/personas/{usuario_id}/restablecer", response_model=EnlaceResponse)
def restablecer_contrasena(
    usuario_id: int, db: Session = Depends(get_db), actor: Actor = Depends(admin)
) -> EnlaceResponse:
    _con_cuentas()
    usuario = _usuario_o_404(db, usuario_id)
    nuevo, enlace = cuentas_propias.restablecimiento(db, usuario, actor.email)
    return EnlaceResponse(enlace=enlace, expira=nuevo.expira)


@router.get("/invitaciones", response_model=list[InvitacionItem])
def listar_invitaciones(
    db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> list[InvitacionItem]:
    return cuentas_propias.pendientes(db)


@router.post("/invitaciones", response_model=EnlaceResponse, status_code=status.HTTP_201_CREATED)
def invitar(
    datos: InvitacionCrear, db: Session = Depends(get_db), actor: Actor = Depends(admin)
) -> EnlaceResponse:
    _con_cuentas()
    invitacion, enlace = cuentas_propias.invitar(db, datos.email, datos.roles, actor.email)
    return EnlaceResponse(enlace=enlace, expira=invitacion.expira)


@router.delete("/invitaciones/{invitacion_id}", status_code=status.HTTP_204_NO_CONTENT)
def revocar_invitacion(
    invitacion_id: int, db: Session = Depends(get_db), _actor: Actor = Depends(admin)
) -> None:
    cuentas_propias.revocar_invitacion(db, invitacion_id)
