from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.permisos import GESTIONAR_FALLAS
from app.models.acceso import Acceso
from app.models.usuario import Usuario
from app.services.contenido import Contenido

PAGINA_TECNICO = "tecnico"
AUDIENCIAS = ("funcional", "tecnica")


def secciones_visibles(
    contenido: Contenido, asignadas: set[str], tecnico: bool, audiencia: str | None = None
) -> set[str]:
    visibles = set()
    for seccion in contenido.respuesta.secciones:
        if audiencia in AUDIENCIAS and seccion.audiencia != audiencia:
            continue
        if seccion.audiencia == "tecnica":
            if seccion.id in asignadas or tecnico:
                visibles.add(seccion.id)
        elif not asignadas or seccion.id in asignadas:
            visibles.add(seccion.id)
    return visibles


def tecnicos(db: Session, emails: set[str]) -> dict[str, bool]:
    gestores = {
        u.email
        for u in db.scalars(select(Usuario).where(Usuario.email.in_(emails)))
        if GESTIONAR_FALLAS in (u.permisos or [])
    }
    concedidos = {
        a.usuario_email
        for a in db.scalars(select(Acceso).where(Acceso.usuario_email.in_(emails)))
        if PAGINA_TECNICO in (a.paginas or [])
    }
    return {email: email in gestores or email in concedidos for email in emails}
