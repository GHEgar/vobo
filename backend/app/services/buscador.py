import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass
from urllib.parse import quote

from app.schemas.busqueda import ResultadoBusqueda, TipoResultado
from app.schemas.contenido import HERRAMIENTA_GENERAL, Caso, Procedimiento, Seccion
from app.services.contenido import Contenido

MINIMO = 2
LIMITE = 40
ANCHO = 120
GRUPOS: dict[str, int] = {"caso": 0, "paso": 0, "seccion": 1, "herramienta": 2, "procedimiento": 3}


@dataclass(frozen=True)
class _Candidato:
    tipo: TipoResultado
    id: str
    titulo: str
    ruta: str
    encabezado: str
    campos: tuple[str, ...]
    contexto: str | None = None


def _plano(texto: str) -> tuple[str, list[int]]:
    caracteres: list[str] = []
    origen: list[int] = []
    for indice, caracter in enumerate(texto):
        for parte in unicodedata.normalize("NFKD", caracter):
            if unicodedata.combining(parte):
                continue
            for minuscula in parte.casefold():
                caracteres.append(minuscula)
                origen.append(indice)
    return "".join(caracteres), origen


def normalizar(texto: str) -> str:
    return _plano(texto)[0]


def palabras_de(consulta: str) -> list[str]:
    limpia = normalizar(consulta).strip()
    if len(limpia) < MINIMO:
        return []
    return list(dict.fromkeys(limpia.split()))


def _limpio(texto: str) -> str:
    return " ".join(texto.split())


def _recorte(texto: str, centro: int) -> str:
    if len(texto) <= ANCHO:
        return texto
    desde = max(0, min(centro - ANCHO // 3, len(texto) - ANCHO))
    hasta = desde + ANCHO
    fragmento = texto[desde:hasta].strip()
    return f"{'…' if desde else ''}{fragmento}{'…' if hasta < len(texto) else ''}"


def _contexto(campos: tuple[str, ...], palabras: list[str]) -> str:
    for texto in campos:
        plano, origen = _plano(texto)
        posiciones = [plano.find(p) for p in palabras if p in plano]
        if posiciones:
            return _recorte(texto, origen[min(posiciones)])
    return _recorte(next((t for t in campos if t), ""), 0)


def _relevancia(candidato: _Candidato, palabras: list[str]) -> int | None:
    encabezado = normalizar(candidato.encabezado)
    cuerpo = "\n".join(normalizar(t) for t in candidato.campos)
    todo = f"{encabezado}\n{cuerpo}"
    if not all(p in todo for p in palabras):
        return None
    en_encabezado = sum(p in encabezado for p in palabras)
    if en_encabezado == len(palabras):
        return 0
    return 1 if en_encabezado else 2


def _ruta_seccion(seccion_id: str) -> str:
    return f"/seccion/{quote(seccion_id, safe='')}"


def _ruta_caso(caso_id: str, paso: int | None = None) -> str:
    base = f"/caso/{quote(caso_id, safe='')}"
    return base if paso is None else f"{base}?paso={paso}"


def _de_caso(caso: Caso) -> Iterator[_Candidato]:
    yield _Candidato(
        tipo="caso",
        id=caso.id,
        titulo=caso.titulo,
        ruta=_ruta_caso(caso.id),
        encabezado=f"{caso.id} {caso.titulo}",
        campos=tuple(_limpio(t) for t in (caso.antes, caso.esperado, caso.rol, caso.cuenta)),
    )
    ultimo = len(caso.pasos) - 1
    for indice, paso in enumerate(caso.pasos):
        numero = indice + 1
        textos = (paso.texto, caso.esperado) if indice == ultimo else (paso.texto,)
        yield _Candidato(
            tipo="paso",
            id=f"{caso.id}:{numero}",
            titulo=f"{caso.titulo} · Paso {numero}",
            ruta=_ruta_caso(caso.id, numero),
            encabezado="",
            campos=tuple(_limpio(t) for t in textos),
        )


def _de_seccion(seccion: Seccion) -> Iterator[_Candidato]:
    ruta = _ruta_seccion(seccion.id)
    yield _Candidato(
        tipo="seccion",
        id=seccion.id,
        titulo=seccion.titulo,
        ruta=ruta,
        encabezado=seccion.titulo,
        campos=tuple(_limpio(t) for t in (seccion.resumen, *seccion.que_cambia, seccion.donde)),
    )
    for herramienta in seccion.herramientas:
        if herramienta.id == HERRAMIENTA_GENERAL:
            continue
        nombre = herramienta.nombre or herramienta.id
        yield _Candidato(
            tipo="herramienta",
            id=herramienta.id,
            titulo=nombre,
            ruta=ruta,
            encabezado=nombre,
            campos=(),
            contexto=f"Sección: {seccion.titulo}",
        )
    for caso in seccion.casos:
        yield from _de_caso(caso)


def _referencias(secciones: list[Seccion]) -> dict[str, str]:
    rutas: dict[str, str] = {}
    for seccion in secciones:
        for caso in seccion.casos:
            for indice, paso in enumerate(caso.pasos):
                if paso.procedimiento:
                    rutas.setdefault(paso.procedimiento, _ruta_caso(caso.id, indice + 1))
        for media in seccion.media:
            rutas.setdefault(media.procedimiento, _ruta_seccion(seccion.id))
    return rutas


def _textos_extra(procedimiento: Procedimiento) -> list[str]:
    textos: list[str] = []
    for valor in (procedimiento.model_extra or {}).values():
        if isinstance(valor, str):
            textos.append(valor)
        elif isinstance(valor, list):
            textos.extend(v for v in valor if isinstance(v, str))
    return textos


def _de_procedimientos(
    procedimientos: list[Procedimiento], rutas: dict[str, str]
) -> Iterator[_Candidato]:
    for procedimiento in procedimientos:
        ruta = rutas.get(procedimiento.id)
        if ruta is None:
            continue
        titulo = procedimiento.titulo or procedimiento.id
        textos = (procedimiento.descripcion, *_textos_extra(procedimiento))
        yield _Candidato(
            tipo="procedimiento",
            id=procedimiento.id,
            titulo=titulo,
            ruta=ruta,
            encabezado=titulo,
            campos=tuple(_limpio(t) for t in textos),
        )


def _candidatos(contenido: Contenido, visibles: set[str]) -> Iterator[_Candidato]:
    secciones = [s for s in contenido.respuesta.secciones if s.id in visibles]
    for seccion in secciones:
        yield from _de_seccion(seccion)
    yield from _de_procedimientos(contenido.respuesta.procedimientos, _referencias(secciones))


def buscar(
    contenido: Contenido, visibles: set[str], palabras: list[str]
) -> list[ResultadoBusqueda]:
    encontrados: list[tuple[int, int, int, ResultadoBusqueda]] = []
    vistos: set[tuple[str, str]] = set()
    for orden, candidato in enumerate(_candidatos(contenido, visibles)):
        if (candidato.tipo, candidato.id) in vistos:
            continue
        relevancia = _relevancia(candidato, palabras)
        if relevancia is None:
            continue
        vistos.add((candidato.tipo, candidato.id))
        resultado = ResultadoBusqueda(
            tipo=candidato.tipo,
            id=candidato.id,
            titulo=candidato.titulo,
            contexto=candidato.contexto or _contexto(candidato.campos, palabras),
            ruta=candidato.ruta,
        )
        encontrados.append((GRUPOS[candidato.tipo], relevancia, orden, resultado))
    encontrados.sort(key=lambda e: e[:3])
    return [e[3] for e in encontrados[:LIMITE]]
