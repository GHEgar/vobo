from pydantic import BaseModel, Field


class UsuarioSesion(BaseModel):
    email: str
    nombre: str
    permisos: list[str]
    paginas: list[str]
    origen: str = "oidc"
    tiene_cuenta: bool = False
    debe_cambiar: bool = False


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


class EntradaCuenta(BaseModel):
    email: str = Field(max_length=200)
    contrasena: str = Field(max_length=1024)


class DefinirCuenta(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    contrasena: str = Field(max_length=1024)


class NuevaContrasena(BaseModel):
    contrasena: str = Field(max_length=1024)


class CambioContrasena(BaseModel):
    actual: str = Field(max_length=1024)
    nueva: str = Field(max_length=1024)


class EnlacePublico(BaseModel):
    email: str
