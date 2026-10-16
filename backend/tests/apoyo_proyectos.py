import yaml

from tests.apoyo_contenido import armar_zip, leer_zip

SOLO_MOVIL = {
    "id": "solo-movil",
    "titulo": "Aplicación móvil",
    "sistema": "general",
    "herramientas": [{"id": "app-movil", "nombre": "App móvil", "hoy": "beta"}],
    "casos": [
        {
            "id": "M-APP-01",
            "familia": "A",
            "titulo": "Abrir la aplicación móvil",
            "herramienta": "app-movil",
            "pasos": [{"texto": "Abrir la aplicación en el teléfono"}],
            "esperado": "Se ve la portada",
            "severidad": "alta",
        }
    ],
}


def crear_proyecto(admin, clave: str = "movil", nombre: str = "App móvil", **extra) -> dict:
    respuesta = admin.post("/api/admin/proyectos", json={"clave": clave, "nombre": nombre, **extra})
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()


def paquete_movil(admin) -> bytes:
    entradas = leer_zip(admin.get("/api/contenido/exportar.zip").content)
    secciones = {k: v for k, v in entradas.items() if k.startswith("secciones/")}
    conservadas = {k: v for k, v in secciones.items() if k == "secciones/catalogo.yaml"}
    conservadas["secciones/solo-movil.yaml"] = yaml.safe_dump(SOLO_MOVIL).encode()
    return armar_zip({**conservadas, "procedimientos.yaml": entradas["procedimientos.yaml"]})


def importar(admin, clave: str, contenido: bytes) -> dict:
    archivo = {"archivo": ("contenido.zip", contenido, "application/zip")}
    respuesta = admin.post(f"/api/editor/importar?confirmar=true&proyecto={clave}", files=archivo)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def ronda(cliente, nombre: str, proyecto: str | None = None) -> int:
    cuerpo = {"nombre": nombre, **({"proyecto": proyecto} if proyecto else {})}
    respuesta = cliente.post("/api/rondas", json=cuerpo)
    assert respuesta.status_code == 201, respuesta.text
    return respuesta.json()["id"]


def marcar(cliente, ronda_id: int, caso_id: str, estado: str = "pasa"):
    return cliente.put(f"/api/resultados/{caso_id}", json={"ronda_id": ronda_id, "estado": estado})


def reportar(cliente, ronda_id: int, caso_id: str, obtenido: str):
    datos = {
        "ronda_id": ronda_id,
        "caso_id": caso_id,
        "obtenido": obtenido,
        "reproducible": "siempre",
    }
    return cliente.post("/api/fallas", data=datos)
