import { arcosDe } from '@/utils/pantalla/arcos';
import { ESTADOS, PALETA } from '@/utils/pantalla/paleta';
import { porcentaje } from '@/utils/pantalla/formato';

const CONTORNO = { paintOrder: 'stroke', stroke: PALETA.fondoGrafo, strokeLinejoin: 'round' };
const NEGRITA = { fontFamily: 'var(--tipo-negrita)', fontWeight: 700 };

const arco = (r, fraccion) => {
    const c = 2 * Math.PI * r;
    return `${Math.max(c * fraccion, 0.01).toFixed(1)} ${c.toFixed(1)}`;
};

const mover = (n) => `translate(${n.x.toFixed(1)} ${n.y.toFixed(1)})`;

const Grupo = ({ nodo, registrar, children }) => (
    <g ref={registrar(nodo.id, nodo)} transform={mover(nodo)}>{children}</g>
);

const Pulso = ({ pulso }) => (pulso ? <circle key={pulso.clave} className="pantalla-pulso" r="6" fill="none" stroke={pulso.color} strokeWidth="3" /> : null);

const MiniAnillo = ({ nodo }) => {
    const radio = nodo.r + 5;
    const total = Object.values(nodo.conteos).reduce((a, b) => a + b, 0);
    const c = 2 * Math.PI * radio;
    return (
        <>
            <circle r={radio} fill="none" stroke={ESTADOS.pendiente} strokeWidth="4" />
            {total > 0 && arcosDe(nodo.conteos, total, c, 1.5).map((a) => (
                <circle key={a.estado} r={radio} fill="none" stroke={a.color} strokeWidth="4" strokeDasharray={a.dash} strokeDashoffset={a.offset} transform="rotate(-90)" />
            ))}
        </>
    );
};

export const Simple = ({ nodo, registrar, pulso }) => {
    if (nodo.tipo === 'caso') {
        return (
            <Grupo nodo={nodo} registrar={registrar}>
                <Pulso pulso={pulso} />
                <circle r={nodo.r} fill={ESTADOS[nodo.estado] ?? ESTADOS.pendiente} stroke={PALETA.fondoGrafo} strokeWidth="1.5" />
            </Grupo>
        );
    }
    if (nodo.tipo === 'grupo') {
        return (
            <Grupo nodo={nodo} registrar={registrar}>
                <Pulso pulso={pulso} />
                <MiniAnillo nodo={nodo} />
                <circle r={nodo.r} fill={PALETA.fondoGrafo} stroke={nodo.color} strokeWidth="2.5" />
            </Grupo>
        );
    }
    if (nodo.tipo === 'seccion') {
        return (
            <Grupo nodo={nodo} registrar={registrar}>
                <circle r={nodo.r} fill={PALETA.fondoGrafo} stroke={nodo.color} strokeWidth="2.5" />
            </Grupo>
        );
    }
    return (
        <Grupo nodo={nodo} registrar={registrar}>
            <circle r={nodo.r} fill={nodo.color} stroke={PALETA.fondoGrafo} strokeWidth="3" />
        </Grupo>
    );
};

export const EtiquetaSistema = ({ nodo, registrar }) => (
    <g ref={registrar(`lbl:${nodo.id}`, nodo)} transform={mover(nodo)}>
        <text y={nodo.r + 24} textAnchor="middle" fontSize="19" fill={PALETA.medio} style={{ ...CONTORNO, strokeWidth: 5 }}>{nodo.nombre}</text>
    </g>
);

const Emblema = ({ nodo }) => {
    if (nodo.logo) {
        const lado = nodo.r * 1.2;
        return <image href={nodo.logo} x={-lado / 2} y={-lado / 2} width={lado} height={lado} preserveAspectRatio="xMidYMid meet" />;
    }
    return (
        <text y={nodo.r * 0.34} textAnchor="middle" fontSize={nodo.r} fill={PALETA.blanco} style={NEGRITA}>
            {nodo.nombre.slice(0, 1).toUpperCase()}
        </text>
    );
};

export const Proyecto = ({ nodo, registrar }) => {
    const anillo = nodo.r + 9;
    return (
        <Grupo nodo={nodo} registrar={registrar}>
            <circle r={nodo.r} fill={nodo.color} stroke={PALETA.fondoGrafo} strokeWidth="4" />
            <circle r={anillo} fill="none" stroke={PALETA.pista} strokeWidth="6" />
            <circle r={anillo} fill="none" stroke={PALETA.texto} strokeWidth="6" strokeLinecap="round" strokeDasharray={arco(anillo, nodo.avance)} transform="rotate(-90)" />
            <Emblema nodo={nodo} />
            <text y={nodo.r + 48} textAnchor="middle" fontSize="30" fill={PALETA.texto} style={{ ...NEGRITA, ...CONTORNO, strokeWidth: 6 }}>{nodo.nombre}</text>
            <text y={nodo.r + 76} textAnchor="middle" fontSize="22" fill={PALETA.medio} style={{ ...CONTORNO, strokeWidth: 6, fontWeight: 600 }}>{porcentaje(nodo.avance)}</text>
        </Grupo>
    );
};

export const Persona = ({ nodo, registrar }) => {
    const anillo = nodo.r + 7;
    return (
        <Grupo nodo={nodo} registrar={registrar}>
            <g opacity={nodo.activa ? 1 : 0.7}>
                <circle r={anillo} fill="none" stroke={PALETA.pista} strokeWidth="5" />
                <circle r={anillo} fill="none" stroke={nodo.avance >= 1 ? ESTADOS.pasa : PALETA.texto} strokeWidth="5" strokeLinecap="round" strokeDasharray={arco(anillo, nodo.avance)} transform="rotate(-90)" />
                <circle r={nodo.r} fill={nodo.color} stroke={PALETA.fondoGrafo} strokeWidth="3" />
                <text y={nodo.r * 0.26} textAnchor="middle" fontSize={Math.round(nodo.r * 0.72)} fill={PALETA.blanco} style={NEGRITA}>{nodo.iniciales}</text>
                <text y={-nodo.r - 18} textAnchor="middle" fontSize="20" fill={PALETA.texto} style={{ ...CONTORNO, strokeWidth: 6, fontWeight: 600 }}>
                    {`${nodo.nombre} · ${nodo.total} ${nodo.total === 1 ? 'caso' : 'casos'}`}
                </text>
            </g>
        </Grupo>
    );
};

const coordenadas = (l) => ({ x1: l.a.x.toFixed(1), y1: l.a.y.toFixed(1), x2: l.b.x.toFixed(1), y2: l.b.y.toFixed(1) });

const estiloEnlace = (l) => {
    if (l.tipo === 'participa') return { stroke: l.color, strokeWidth: l.ancho.toFixed(1), strokeOpacity: 0.35 };
    if (l.tipo === 'debil') return { stroke: PALETA.enlace, strokeWidth: 1, strokeOpacity: 0.45 };
    return { stroke: l.a.color ?? PALETA.enlace, strokeWidth: l.tipo === 'fuerte' ? 2.5 : 1.5, strokeOpacity: 0.6 };
};

export const Enlace = ({ enlace, registrar }) => (
    <line ref={registrar(enlace.id, enlace)} {...coordenadas(enlace)} {...estiloEnlace(enlace)} />
);

export const Mirada = ({ enlace, registrar }) => (
    <line
        ref={registrar(enlace.id, enlace)}
        className="pantalla-flujo"
        {...coordenadas(enlace)}
        stroke={enlace.a.color}
        strokeWidth="2.5"
        strokeDasharray="6 6"
        strokeOpacity="0.9"
    />
);
