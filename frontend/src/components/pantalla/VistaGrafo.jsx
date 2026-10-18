import { useCallback, useEffect, useMemo, useRef, useSyncExternalStore } from 'react';
import { cifras as calcularCifras } from '@/components/pantalla/grafo/modelo';
import { enfriar, paso } from '@/components/pantalla/grafo/simulacion';
import { almacenDe } from '@/components/pantalla/grafo/almacen';
import { Enlace, EtiquetaSistema, Mirada, Persona, Proyecto, Simple } from '@/components/pantalla/grafo/Nodos';
import { Leyenda, Cifras } from '@/components/pantalla/grafo/Leyenda';
import { Logo } from '@/components/pantalla/Encabezado';
import { useMovimientoReducido } from '@/hooks/usePantalla';
import { ALTO, ANCHO, PALETA } from '@/utils/pantalla/paleta';

const DURACION_PULSO = 5000;

const dibujar = (elementos) => {
    for (const [el, objeto] of elementos) {
        if (objeto.a) {
            el.setAttribute('x1', objeto.a.x.toFixed(1));
            el.setAttribute('y1', objeto.a.y.toFixed(1));
            el.setAttribute('x2', objeto.b.x.toFixed(1));
            el.setAttribute('y2', objeto.b.y.toFixed(1));
        } else {
            el.setAttribute('transform', `translate(${objeto.x.toFixed(1)} ${objeto.y.toFixed(1)})`);
        }
    }
};

const useGrafo = (datos, clave) => {
    const almacen = almacenDe(clave);
    const estado = useSyncExternalStore(almacen.suscribir, almacen.leer, almacen.leer);

    useEffect(() => {
        almacen.actualizar(datos);
    }, [almacen, datos]);

    useEffect(() => {
        if (estado.pulsos.size === 0) return undefined;
        const temporizador = setTimeout(almacen.limpiarPulsos, DURACION_PULSO);
        return () => clearTimeout(temporizador);
    }, [almacen, estado.pulsos]);

    return estado;
};

const useAnimacion = (grafo, elementos, reducido) => {
    useEffect(() => {
        if (!grafo) return undefined;
        dibujar(elementos.current);
        if (reducido) return undefined;
        let alfa = 0.3;
        let cuadro = requestAnimationFrame(function avanzar() {
            paso(grafo, alfa);
            alfa = enfriar(alfa);
            dibujar(elementos.current);
            cuadro = requestAnimationFrame(avanzar);
        });
        return () => cancelAnimationFrame(cuadro);
    }, [grafo, elementos, reducido]);
};

const Lienzo = ({ grafo, pulsos, reducido }) => {
    const elementos = useRef(new Map());
    const registrar = useCallback((_clave, objeto) => (el) => {
        if (!el) return undefined;
        elementos.current.set(el, objeto);
        return () => elementos.current.delete(el);
    }, []);
    useAnimacion(grafo, elementos, reducido);

    const capas = useMemo(() => {
        const de = (tipos) => grafo.nodos.filter((n) => tipos.includes(n.tipo));
        return {
            enlaces: grafo.enlaces.filter((l) => l.tipo !== 'mirada'),
            miradas: grafo.enlaces.filter((l) => l.tipo === 'mirada'),
            simples: de(['caso', 'seccion', 'grupo', 'sistema']),
            sistemas: de(['sistema']),
            proyectos: de(['proyecto']),
            personas: de(['persona']),
        };
    }, [grafo]);

    const casos = capas.simples.filter((n) => n.tipo === 'caso').length;
    const etiqueta = `Grafo de ${capas.proyectos.length} proyectos, ${casos} casos y ${capas.personas.length} personas`;
    return (
        <svg width={ANCHO} height={ALTO} viewBox={`0 0 ${ANCHO} ${ALTO}`} role="img" aria-label={etiqueta} className="absolute inset-0 block">
            <g>{capas.enlaces.map((l) => <Enlace key={l.id} enlace={l} registrar={registrar} />)}</g>
            <g>{capas.miradas.map((l) => <Mirada key={l.id} enlace={l} registrar={registrar} />)}</g>
            <g>{capas.simples.map((n) => <Simple key={n.id} nodo={n} registrar={registrar} pulso={pulsos.get(n.id)} />)}</g>
            <g>{capas.proyectos.map((n) => <Proyecto key={n.id} nodo={n} registrar={registrar} />)}</g>
            <g>{capas.personas.map((n) => <Persona key={n.id} nodo={n} registrar={registrar} />)}</g>
            <g>{capas.sistemas.map((n) => <EtiquetaSistema key={n.id} nodo={n} registrar={registrar} />)}</g>
        </svg>
    );
};

const VistaGrafo = ({ config, datos, token }) => {
    const reducido = useMovimientoReducido();
    const { grafo, pulsos } = useGrafo(datos, token ?? 'pantalla');
    const cifras = calcularCifras(datos);
    return (
        <div className="relative h-full" style={{ background: `radial-gradient(circle at 50% 50%, ${PALETA.halo} 0%, ${PALETA.fondoGrafo} 70%)` }}>
            {grafo && <Lienzo grafo={grafo} pulsos={pulsos} reducido={reducido} />}
            <header className="pointer-events-none absolute left-16 top-10 flex items-center gap-6">
                <Logo marca={config.marca} />
                <div className="flex flex-col gap-1.5">
                    <span style={{ fontSize: 44, fontFamily: 'var(--tipo-negrita)', fontWeight: 700, letterSpacing: -0.5 }}>{config.nombre}</span>
                    <span style={{ fontSize: 24, color: PALETA.tenue }}>Persona: tamaño = cuánto ha participado · anillo = su avance</span>
                </div>
            </header>
            <Cifras cifras={cifras} />
            <Leyenda agrupado={datos.proyectos.some((p) => p.agrupado)} />
        </div>
    );
};

export default VistaGrafo;
