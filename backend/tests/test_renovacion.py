import asyncio
from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.core import oidc
from app.core.database import SessionLocal
from app.core.time import utcnow
from app.models.usuario import Sesion, Usuario
from app.services import sesiones


class ProveedorQueRota:
    def __init__(self, demora: float = 0.0) -> None:
        self.vigente = "refresco-0"
        self.llamadas = 0
        self.demora = demora

    async def refrescar(self, refresh_token: str) -> dict:
        self.llamadas += 1
        await asyncio.sleep(self.demora)
        if refresh_token != self.vigente:
            raise oidc.ErrorOIDC("invalid_grant", "reutilizado", 400)
        self.vigente = f"refresco-{self.llamadas}"
        return {
            "access_token": f"acceso-{self.llamadas}",
            "refresh_token": self.vigente,
            "expires_in": 900,
        }


@pytest.fixture
def sesion_vencida() -> str:
    with SessionLocal() as db:
        usuario = Usuario(email="persona@ejemplo.test", nombre="Persona", sub_oidc="u-1")
        db.add(usuario)
        db.flush()
        sesion = Sesion(
            id="sesion-1",
            usuario_id=usuario.id,
            access_token="acceso-0",
            refresh_token="refresco-0",
            access_expira=utcnow() - timedelta(minutes=1),
        )
        db.add(sesion)
        db.commit()
        return sesion.id


def _proveedor(monkeypatch: pytest.MonkeyPatch, demora: float = 0.0) -> ProveedorQueRota:
    proveedor = ProveedorQueRota(demora)
    monkeypatch.setattr(oidc, "refrescar", proveedor.refrescar)
    return proveedor


def test_un_proceso_con_vista_vieja_usa_la_renovacion_del_otro(monkeypatch, sesion_vencida) -> None:
    proveedor = _proveedor(monkeypatch)
    with SessionLocal() as primero, SessionLocal() as segundo:
        segundo.get(Sesion, sesion_vencida)
        asyncio.run(sesiones.vigente(primero, sesion_vencida))
        renovada = asyncio.run(sesiones.vigente(segundo, sesion_vencida))
        assert renovada.access_token == "acceso-1"
    assert proveedor.llamadas == 1
    with SessionLocal() as db:
        assert db.get(Sesion, sesion_vencida).refresh_token == "refresco-1"


def test_renovaciones_simultaneas_llaman_una_vez_y_no_cierran(monkeypatch, sesion_vencida) -> None:
    proveedor = _proveedor(monkeypatch, demora=0.3)

    async def dos_a_la_vez() -> set[str]:
        with SessionLocal() as uno, SessionLocal() as dos:
            resultados = await asyncio.gather(
                sesiones.vigente(uno, sesion_vencida), sesiones.vigente(dos, sesion_vencida)
            )
            return {s.access_token for s in resultados}

    assert asyncio.run(dos_a_la_vez()) == {"acceso-1"}
    assert proveedor.llamadas == 1
    with SessionLocal() as db:
        guardada = db.get(Sesion, sesion_vencida)
        assert guardada is not None
        assert guardada.renovando_hasta is None


def test_reclamo_abandonado_se_retoma(monkeypatch, sesion_vencida) -> None:
    proveedor = _proveedor(monkeypatch)
    with SessionLocal() as db:
        db.get(Sesion, sesion_vencida).renovando_hasta = utcnow() - timedelta(seconds=1)
        db.commit()
        renovada = asyncio.run(sesiones.vigente(db, sesion_vencida))
        assert renovada.access_token == "acceso-1"
    assert proveedor.llamadas == 1


def test_rechazo_tras_rotacion_ajena_no_cierra_la_sesion(monkeypatch, sesion_vencida) -> None:
    async def rechaza_y_otro_rota(refresh_token: str) -> dict:
        with SessionLocal() as otro:
            otro.get(Sesion, sesion_vencida).refresh_token = "refresco-ajeno"
            otro.commit()
        raise oidc.ErrorOIDC("invalid_grant", "reutilizado", 400)

    monkeypatch.setattr(oidc, "refrescar", rechaza_y_otro_rota)
    with SessionLocal() as db, pytest.raises(HTTPException) as error:
        asyncio.run(sesiones.vigente(db, sesion_vencida))
    assert error.value.status_code == 503
    with SessionLocal() as db:
        guardada = db.get(Sesion, sesion_vencida)
        assert guardada is not None
        assert guardada.renovando_hasta is None


def test_rechazo_definitivo_propio_cierra_la_sesion(monkeypatch, sesion_vencida) -> None:
    proveedor = _proveedor(monkeypatch)
    proveedor.vigente = "otro"
    with SessionLocal() as db, pytest.raises(HTTPException) as error:
        asyncio.run(sesiones.vigente(db, sesion_vencida))
    assert error.value.status_code == 401
    with SessionLocal() as db:
        assert db.get(Sesion, sesion_vencida) is None
