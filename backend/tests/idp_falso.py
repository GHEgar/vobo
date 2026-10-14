import json
import time
from dataclasses import dataclass, field
from urllib.parse import parse_qs

import httpx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jose import jwk, jwt

INTERNA = "http://idp.ejemplo:3000"
PUBLICA = "https://idp.ejemplo"
PERMISOS_URL = f"{INTERNA}/api/v1/me/permissions?application=validacion"

DESCUBRIMIENTO = {
    "issuer": PUBLICA,
    "authorization_endpoint": f"{PUBLICA}/auth/authorize",
    "token_endpoint": f"{PUBLICA}/auth/token",
    "userinfo_endpoint": f"{PUBLICA}/userinfo",
    "jwks_uri": f"{PUBLICA}/.well-known/jwks.json",
    "revocation_endpoint": f"{PUBLICA}/auth/revoke",
    "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
    "code_challenge_methods_supported": ["S256"],
}


@dataclass
class Llave:
    kid: str
    privada: bytes
    publica: dict


def nueva_llave(kid: str) -> Llave:
    privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = privada.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    publica_pem = privada.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    publica = {**jwk.construct(publica_pem, "RS256").to_dict(), "kid": kid, "use": "sig"}
    return Llave(kid=kid, privada=pem, publica=publica)


@dataclass
class IdpFalso:
    llaves: list[Llave] = field(default_factory=lambda: [nueva_llave("k1")])
    descubrimiento: dict = field(default_factory=lambda: dict(DESCUBRIMIENTO))
    permisos: list[str] = field(default_factory=lambda: ["validacion.casos.ejecutar"])
    estado_permisos: int = 200
    respuesta_token: tuple[int, dict] | None = None
    peticiones: list[httpx.Request] = field(default_factory=list)
    formularios: list[dict[str, str]] = field(default_factory=list)

    def token(self, llave: Llave | None = None, **claims: object) -> str:
        llave = llave or self.llaves[0]
        ahora = int(time.time())
        datos = {
            "iss": PUBLICA,
            "aud": "validacion",
            "sub": "u-1",
            "email": "persona@ejemplo.test",
            "name": "Persona de Prueba",
            "typ": "access",
            "iat": ahora,
            "exp": ahora + 600,
            **claims,
        }
        datos = {k: v for k, v in datos.items() if v is not None}
        return jwt.encode(datos, llave.privada, algorithm="RS256", headers={"kid": llave.kid})

    def llamadas(self, url: str) -> int:
        return sum(1 for p in self.peticiones if str(p.url) == url)

    def _formulario(self, peticion: httpx.Request) -> None:
        formulario = {k: v[0] for k, v in parse_qs(peticion.content.decode()).items()}
        self.formularios.append(formulario)

    def _revocar(self, peticion: httpx.Request) -> httpx.Response:
        self._formulario(peticion)
        return httpx.Response(200)

    def _token(self, peticion: httpx.Request) -> httpx.Response:
        self._formulario(peticion)
        if self.respuesta_token is not None:
            return httpx.Response(self.respuesta_token[0], json=self.respuesta_token[1])
        return httpx.Response(
            200,
            json={
                "access_token": self.token(),
                "refresh_token": "refresco-1",
                "expires_in": 900,
                "token_type": "Bearer",
            },
        )

    def _permisos(self, peticion: httpx.Request) -> httpx.Response:
        if not peticion.headers.get("authorization", "").startswith("Bearer "):
            return httpx.Response(401, json={"detail": "sin token"})
        if self.estado_permisos != 200:
            return httpx.Response(self.estado_permisos, json={"detail": "no"})
        return httpx.Response(200, json={"permissions": self.permisos})

    def __call__(self, peticion: httpx.Request) -> httpx.Response:
        self.peticiones.append(peticion)
        url = str(peticion.url)
        rutas = {
            f"{INTERNA}/.well-known/openid-configuration": lambda: httpx.Response(
                200, content=json.dumps(self.descubrimiento)
            ),
            f"{INTERNA}/.well-known/jwks.json": lambda: httpx.Response(
                200, json={"keys": [llave.publica for llave in self.llaves]}
            ),
            f"{INTERNA}/auth/token": lambda: self._token(peticion),
            f"{INTERNA}/auth/revoke": lambda: self._revocar(peticion),
            PERMISOS_URL: lambda: self._permisos(peticion),
        }
        respuesta = rutas.get(url)
        if respuesta is None:
            return httpx.Response(404, json={"error": "not_found", "url": url})
        return respuesta()
