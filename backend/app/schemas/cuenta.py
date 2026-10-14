from pydantic import BaseModel


class CuentaPrueba(BaseModel):
    email: str
    password: str
    descripcion: str
