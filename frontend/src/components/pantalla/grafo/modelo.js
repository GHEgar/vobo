import { ESTADOS, PALETA } from '@/utils/pantalla/paleta';

export const CENTRO = { x: 960, y: 580 };

const LARGOS = { fuerte: 140, medio: 70, debil: 36, mirada: 90, participa: 230 };

const totalDe = (persona) => Object.values(persona.participa).reduce((a, b) => a + b, 0);

const azar = (semilla) => {
    let h = 2166136261;
    for (let i = 0; i < semilla.length; i += 1) {
        h ^= semilla.charCodeAt(i);
        h = Math.imul(h, 16777619);
    }
    return ((h >>> 0) % 10000) / 10000;
};

const cerca = (base, id, radio) => ({
    x: base.x + (azar(`${id}x`) - 0.5) * radio,
    y: base.y + (azar(`${id}y`) - 0.5) * radio,
});

const lugarDeProyecto = (indice, total) => {
    if (total === 1) return { ...CENTRO };
    const angulo = (indice / total) * Math.PI * 2 + Math.PI;
    return { x: CENTRO.x + Math.cos(angulo) * 420, y: CENTRO.y + Math.sin(angulo) * 230 };
};

const firmaConteos = (c) => `${c.pasa}/${c.falla}/${c.no_pude}/${c.pendiente}`;

class Armador {
    constructor(memoria) {
        this.memoria = memoria;
        this.nodos = [];
        this.enlaces = [];
        this.porId = new Map();
        this.nuevos = 0;
    }

    nodo(datos, sugerida) {
        const previo = this.memoria.get(datos.id);
        if (!previo) this.nuevos += 1;
        const nodo = { vx: 0, vy: 0, ...sugerida, ...previo, ...datos };
        this.nodos.push(nodo);
        this.porId.set(nodo.id, nodo);
        return nodo;
    }

    enlace(a, b, tipo, extra = {}) {
        if (!a || !b) return;
        this.enlaces.push({ id: `${tipo}:${a.id}:${b.id}`, a, b, tipo, largo: LARGOS[tipo], ...extra });
    }
}

const armarSeccion = (arm, proyecto, nodoSistema, seccion, agrupado) => {
    const id = `sec:${proyecto.clave}:${seccion.id}`;
    const nodo = arm.nodo(
        {
            id,
            tipo: agrupado ? 'grupo' : 'seccion',
            nombre: seccion.titulo,
            color: proyecto.color,
            avance: seccion.avance,
            conteos: seccion.conteos,
            firma: firmaConteos(seccion.conteos),
            r: agrupado ? 10 + seccion.avance * 14 : 6 + seccion.avance * 9,
        },
        cerca(nodoSistema, id, 80),
    );
    arm.enlace(nodoSistema, nodo, 'medio');
    (seccion.casos ?? []).forEach((caso) => {
        const idCaso = `k:${proyecto.clave}:${caso.id}`;
        const nodoCaso = arm.nodo({ id: idCaso, tipo: 'caso', nombre: caso.id, estado: caso.estado, firma: caso.estado, r: 5 }, cerca(nodo, idCaso, 60));
        arm.enlace(nodo, nodoCaso, 'debil');
    });
};

const armarProyecto = (arm, proyecto, indice, total) => {
    const nodo = arm.nodo(
        {
            id: `p:${proyecto.clave}`,
            tipo: 'proyecto',
            nombre: proyecto.nombre,
            color: proyecto.color,
            logo: proyecto.logo,
            avance: proyecto.avance,
            r: 28 + proyecto.avance * 30,
        },
        lugarDeProyecto(indice, total),
    );
    proyecto.sistemas.forEach((sistema, i) => {
        const angulo = (i / Math.max(proyecto.sistemas.length, 1)) * Math.PI * 2;
        const id = `s:${proyecto.clave}:${sistema.nombre}`;
        const nodoSistema = arm.nodo(
            { id, tipo: 'sistema', nombre: sistema.nombre, color: proyecto.color, r: 14 },
            { x: nodo.x + Math.cos(angulo) * 140, y: nodo.y + Math.sin(angulo) * 140 },
        );
        arm.enlace(nodo, nodoSistema, 'fuerte');
        sistema.secciones.forEach((s) => armarSeccion(arm, proyecto, nodoSistema, s, proyecto.agrupado));
    });
};

const destinoDe = (arm, actual) => {
    if (!actual) return null;
    const caso = actual.caso_id ? arm.porId.get(`k:${actual.proyecto}:${actual.caso_id}`) : null;
    return caso ?? arm.porId.get(`sec:${actual.proyecto}:${actual.seccion_id}`) ?? null;
};

const armarPersonas = (arm, personas) => {
    const maximo = Math.max(1, ...personas.map(totalDe));
    const maxParticipa = Math.max(1, ...personas.flatMap((p) => Object.values(p.participa)));
    personas.forEach((persona) => {
        const destino = destinoDe(arm, persona.actual);
        const proyectos = Object.keys(persona.participa).map((c) => arm.porId.get(`p:${c}`)).filter(Boolean);
        const base = destino ?? proyectos[0] ?? CENTRO;
        const id = `u:${persona.id}`;
        const total = totalDe(persona);
        const nodo = arm.nodo(
            {
                id,
                tipo: 'persona',
                nombre: persona.nombre,
                iniciales: persona.iniciales,
                color: persona.color,
                avance: persona.avance,
                total,
                activa: persona.activa,
                r: 16 + 26 * Math.sqrt(total / maximo),
            },
            { x: base.x + 70 + azar(id) * 40, y: base.y - 50 - azar(`${id}y`) * 40 },
        );
        if (destino) arm.enlace(nodo, destino, 'mirada');
        Object.entries(persona.participa).forEach(([clave, valor]) => {
            const proyecto = arm.porId.get(`p:${clave}`);
            arm.enlace(nodo, proyecto, 'participa', { ancho: 1.5 + 8 * (valor / maxParticipa), color: proyecto?.color });
        });
    });
};

export const construir = (datos, memoria) => {
    const arm = new Armador(memoria);
    datos.proyectos.forEach((p, i) => armarProyecto(arm, p, i, datos.proyectos.length));
    armarPersonas(arm, datos.personas);
    return { nodos: arm.nodos, enlaces: arm.enlaces, porId: arm.porId, nuevos: arm.nuevos };
};

export const recordar = (nodos, memoria) => {
    memoria.clear();
    nodos.forEach((n) => memoria.set(n.id, { x: n.x, y: n.y, vx: n.vx, vy: n.vy, firma: n.firma }));
};

export const cambios = (nodos, memoria) => nodos
    .filter((n) => n.firma !== undefined && memoria.has(n.id) && memoria.get(n.id).firma !== undefined && memoria.get(n.id).firma !== n.firma)
    .map((n) => ({ id: n.id, color: n.tipo === 'caso' ? ESTADOS[n.estado] : PALETA.texto }));

export const cifras = (datos) => {
    const total = datos.proyectos.reduce((a, p) => a + p.total, 0);
    const pendientes = datos.proyectos.reduce((a, p) => a + p.conteos.pendiente, 0);
    return {
        marcado: total ? (total - pendientes) / total : 0,
        fallas: datos.proyectos.reduce((a, p) => a + p.conteos.falla, 0),
        activas: datos.personas.filter((p) => p.activa).length,
        casos: total,
    };
};
