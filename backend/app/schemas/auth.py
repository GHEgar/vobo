from pydantic import BaseModel


class UsuarioSesion(BaseModel):
    email: str
    nombre: str
    permisos: list[str]
    paginas: list[str]


class SesionResponse(BaseModel):
    csrf_token: str
    usuario: UsuarioSesion


class SalidaResponse(BaseModel):
    logout_url: str


class ModoResponse(BaseModel):
    modo: str


class UsuarioLocal(BaseModel):
    clave: str
    nombre: str
    email: str
    rol: str


class EntradaLocal(BaseModel):
    clave: str
