from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.permisos import (
    CATALOGO,
    EDITAR_IDENTIDAD,
    VER_PARTICIPACION,
    expandir,
)
from app.models.rol import Rol, UsuarioRol
from app.models.usuario import Usuario
from app.schemas.admin import RolCambios, RolCrear

CLAVE_ADMIN = "administracion"

ROLES_SISTEMA = (
    {
        "clave": "validador",
        "nombre": "Validador",
        "descripcion": "Ejecuta los casos que tiene asignados y reporta fallas.",
        "permisos": ["validacion.casos.ejecutar"],
    },
    {
        "clave": "coordinacion",
        "nombre": "Coordinación",
        "descripcion": "Organiza las rondas, sigue el tablero y gestiona las fallas.",
        "permisos": [
            "validacion.casos.ejecutar",
            "validacion.fallas.gestionar",
            "validacion.tablero.ver",
        ],
    },
    {
        "clave": "aprobacion",
        "nombre": "Aprobación",
        "descripcion": "Aprueba o rechaza herramientas y características.",
        "permisos": ["validacion.herramientas.aprobar"],
    },
    {
        "clave": CLAVE_ADMIN,
        "nombre": "Administración",
        "descripcion": "Administra personas y roles; incluye todos los demás permisos.",
        "permisos": ["validacion.admin"],
    },
)

ROLES_AGREGADOS = (
    {
        "clave": "pantalla",
        "nombre": "Pantalla",
        "descripcion": "Solo ve la página Participación; pensado para una TV.",
        "permisos": [VER_PARTICIPACION],
    },
    {
        "clave": "identidad",
        "nombre": "Identidad visual",
        "descripcion": "Edita nombre, textos de entrada, marca, colores y tipografía.",
        "permisos": [EDITAR_IDENTIDAD],
    },
)


def _conflicto(detalle: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detalle)


def sembrar_sistema(db: Session) -> None:
    existentes = set(db.scalars(select(Rol.clave)))
    sembrar = (*ROLES_SISTEMA, *ROLES_AGREGADOS)
    db.add_all(Rol(**r, sistema=True) for r in sembrar if r["clave"] not in existentes)
    db.commit()


def listar(db: Session) -> list[Rol]:
    return list(db.scalars(select(Rol).order_by(Rol.sistema.desc(), Rol.id)))


def obtener_o_404(db: Session, rol_id: int) -> Rol:
    rol = db.get(Rol, rol_id)
    if rol is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado")
    return rol


def _permisos_validos(permisos: list[str]) -> list[str]:
    ajenos = sorted(set(permisos) - set(CATALOGO))
    if ajenos:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Permisos desconocidos: {', '.join(ajenos)}",
        )
    return sorted(set(permisos))


def crear(db: Session, datos: RolCrear) -> Rol:
    if db.scalar(select(Rol).where(Rol.clave == datos.clave)) is not None:
        raise _conflicto("Ya existe un rol con esa clave")
    rol = Rol(
        clave=datos.clave,
        nombre=datos.nombre.strip(),
        descripcion=datos.descripcion.strip(),
        permisos=_permisos_validos(datos.permisos),
        sistema=False,
    )
    db.add(rol)
    db.commit()
    return rol


def actualizar(db: Session, rol: Rol, datos: RolCambios) -> Rol:
    if datos.permisos is not None:
        if rol.clave == CLAVE_ADMIN:
            raise _conflicto("Los permisos de Administración no se pueden cambiar")
        rol.permisos = _permisos_validos(datos.permisos)
    if datos.nombre is not None:
        rol.nombre = datos.nombre.strip()
    if datos.descripcion is not None:
        rol.descripcion = datos.descripcion.strip()
    db.commit()
    return rol


def borrar(db: Session, rol: Rol) -> None:
    if rol.sistema:
        raise _conflicto("Los roles de sistema no se pueden borrar")
    db.delete(rol)
    db.commit()


def claves_por_usuario(db: Session) -> dict[int, list[str]]:
    filas = db.execute(
        select(UsuarioRol.usuario_id, Rol.clave).join(Rol, Rol.id == UsuarioRol.rol_id)
    )
    resultado: dict[int, list[str]] = {}
    for usuario_id, clave in filas:
        resultado.setdefault(usuario_id, []).append(clave)
    return {u: sorted(c) for u, c in resultado.items()}


def por_claves(db: Session, claves: list[str]) -> list[Rol]:
    unicas = set(claves)
    encontrados = list(db.scalars(select(Rol).where(Rol.clave.in_(unicas))))
    faltan = sorted(unicas - {r.clave for r in encontrados})
    if faltan:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Roles desconocidos: {', '.join(faltan)}",
        )
    return encontrados


def administradores(db: Session) -> int:
    return db.scalar(
        select(func.count(UsuarioRol.usuario_id))
        .join(Rol, Rol.id == UsuarioRol.rol_id)
        .where(Rol.clave == CLAVE_ADMIN)
    )


def agregar(db: Session, usuario: Usuario, claves: list[str]) -> None:
    actuales = set(db.scalars(select(UsuarioRol.rol_id).where(UsuarioRol.usuario_id == usuario.id)))
    db.add_all(
        UsuarioRol(usuario_id=usuario.id, rol_id=rol.id)
        for rol in por_claves(db, claves)
        if rol.id not in actuales
    )


def asignar(db: Session, usuario: Usuario, claves: list[str]) -> list[str]:
    nuevos = por_claves(db, claves)
    tenia_admin = CLAVE_ADMIN in claves_por_usuario(db).get(usuario.id, [])
    if tenia_admin and CLAVE_ADMIN not in claves and administradores(db) <= 1:
        raise _conflicto("No se puede quitar Administración a la última persona que la tiene")
    db.execute(delete(UsuarioRol).where(UsuarioRol.usuario_id == usuario.id))
    db.add_all(UsuarioRol(usuario_id=usuario.id, rol_id=rol.id) for rol in nuevos)
    db.commit()
    return sorted(r.clave for r in nuevos)


def _permisos_de(roles: list[Rol]) -> set[str]:
    return {p for rol in roles for p in (rol.permisos or [])}


def asignados(db: Session, usuario_id: int) -> set[str]:
    roles = db.scalars(
        select(Rol)
        .join(UsuarioRol, UsuarioRol.rol_id == Rol.id)
        .where(UsuarioRol.usuario_id == usuario_id)
    )
    return _permisos_de(list(roles))


def por_grupos(db: Session, grupos: set[str]) -> set[str]:
    mapa = settings.mapa_de_roles
    claves = {mapa[g] for g in grupos if g in mapa}
    if not claves:
        return set()
    return _permisos_de(list(db.scalars(select(Rol).where(Rol.clave.in_(claves)))))


def efectivos(
    db: Session, usuario_id: int, del_proveedor: set[str], grupos: set[str]
) -> frozenset[str]:
    return expandir(del_proveedor | asignados(db, usuario_id) | por_grupos(db, grupos))


def exigir_otorgables(otorgante: frozenset[str], permisos: set[str] | list[str]) -> None:
    faltan = sorted(expandir(set(permisos)) - otorgante)
    if faltan:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"No puedes otorgar permisos que no tienes: {', '.join(faltan)}",
        )


def permisos_de_claves(db: Session, claves: list[str] | set[str]) -> set[str]:
    return _permisos_de(list(db.scalars(select(Rol).where(Rol.clave.in_(set(claves))))))
