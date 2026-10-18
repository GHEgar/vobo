import { cambios, construir, recordar } from '@/components/pantalla/grafo/modelo';
import { asentar } from '@/components/pantalla/grafo/simulacion';

const PASOS_INICIALES = 360;

const crearAlmacen = () => {
    const memoria = new Map();
    const oyentes = new Set();
    let datosActuales = null;
    let estado = { grafo: null, pulsos: new Map(), version: 0 };

    const avisar = () => oyentes.forEach((oyente) => oyente());

    return {
        suscribir: (oyente) => {
            oyentes.add(oyente);
            return () => oyentes.delete(oyente);
        },
        leer: () => estado,
        actualizar: (datos) => {
            if (datos === datosActuales) return;
            datosActuales = datos;
            if (estado.grafo) recordar(estado.grafo.nodos, memoria);
            const primero = memoria.size === 0;
            const grafo = construir(datos, memoria);
            const nuevos = cambios(grafo.nodos, memoria);
            if (primero) asentar(grafo, PASOS_INICIALES);
            else if (grafo.nuevos > 0) asentar(grafo, Math.min(120, 20 + grafo.nuevos * 2));
            const version = estado.version + 1;
            const pulsos = new Map(nuevos.map((p) => [p.id, { ...p, clave: `${p.id}:${version}` }]));
            estado = { grafo, pulsos, version };
            avisar();
        },
        limpiarPulsos: () => {
            if (estado.pulsos.size === 0) return;
            estado = { ...estado, pulsos: new Map() };
            avisar();
        },
    };
};

const almacenes = new Map();

export const almacenDe = (clave) => {
    if (!almacenes.has(clave)) almacenes.set(clave, crearAlmacen());
    return almacenes.get(clave);
};
