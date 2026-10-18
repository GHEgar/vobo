import { CENTRO } from '@/components/pantalla/grafo/modelo';

const LIMITES = { x0: 90, x1: 1840, y0: 210, y1: 930 };
const ALCANCE = 90000;
const FRICCION = 0.82;
const PISO = 0.02;

const holgura = (a, b) => {
    if (a.tipo === 'proyecto' && b.tipo === 'proyecto') return 340;
    if (a.tipo === 'persona' || b.tipo === 'persona') return 34;
    return 6;
};

const repeler = (nodos, alfa) => {
    for (let i = 0; i < nodos.length; i += 1) {
        const a = nodos[i];
        for (let j = i + 1; j < nodos.length; j += 1) {
            const b = nodos[j];
            let dx = b.x - a.x;
            let dy = b.y - a.y;
            let d2 = dx * dx + dy * dy;
            const minimo = a.r + b.r + holgura(a, b);
            if (d2 > ALCANCE && d2 > minimo * minimo) continue;
            if (d2 < 1) {
                dx = 0.5;
                dy = 0.5;
                d2 = 0.5;
            }
            const d = Math.sqrt(d2);
            const f = ((a.r + b.r + 16) * 40 / d2) * alfa;
            const empuje = d < minimo ? ((minimo - d) / d) * 0.12 : 0;
            const fx = (dx / d) * f + dx * empuje;
            const fy = (dy / d) * f + dy * empuje;
            a.vx -= fx;
            a.vy -= fy;
            b.vx += fx;
            b.vy += fy;
        }
    }
};

const atraer = (enlaces, alfa) => {
    for (const l of enlaces) {
        const { a, b } = l;
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d = Math.sqrt(dx * dx + dy * dy) || 1;
        const k = ((d - l.largo) / d) * 0.06 * alfa;
        a.vx += dx * k;
        a.vy += dy * k;
        b.vx -= dx * k;
        b.vy -= dy * k;
    }
};

const mover = (nodos, alfa) => {
    for (const n of nodos) {
        if (n.tipo === 'proyecto') {
            n.vx += (CENTRO.x - n.x) * 0.0006 * alfa;
            n.vy += (CENTRO.y - n.y) * 0.0006 * alfa;
        }
        n.vx *= FRICCION;
        n.vy *= FRICCION;
        n.x = Math.min(LIMITES.x1, Math.max(LIMITES.x0, n.x + n.vx));
        n.y = Math.min(LIMITES.y1, Math.max(LIMITES.y0, n.y + n.vy));
    }
};

export const paso = (grafo, alfa) => {
    repeler(grafo.nodos, alfa);
    atraer(grafo.enlaces, alfa);
    mover(grafo.nodos, alfa);
};

export const asentar = (grafo, pasos) => {
    for (let s = 0; s < pasos; s += 1) paso(grafo, 1 - s / pasos);
};

export const enfriar = (alfa) => Math.max(PISO, alfa * 0.985);
