import { ESTADOS, NOMBRES_ESTADO, PALETA, translucido } from '@/utils/pantalla/paleta';
import { porcentaje } from '@/utils/pantalla/formato';

const Punto = ({ color, tam = 16, borde }) => (
    <span aria-hidden="true" className="inline-block shrink-0 rounded-full" style={{ width: tam, height: tam, background: color, border: borde }} />
);

const Anillado = () => (
    <svg aria-hidden="true" width="26" height="26" viewBox="-13 -13 26 26">
        <circle r="10" fill="none" stroke={ESTADOS.pendiente} strokeWidth="4" />
        <circle r="10" fill="none" stroke={ESTADOS.pasa} strokeWidth="4" strokeDasharray="30 63" transform="rotate(-90)" />
        <circle r="6" fill={PALETA.fondoGrafo} stroke={PALETA.medio} strokeWidth="2" />
    </svg>
);

export const Leyenda = ({ agrupado }) => (
    <footer className="pointer-events-none absolute bottom-10 left-16 flex max-w-[1792px] flex-wrap items-center gap-x-7 gap-y-2 rounded-[28px] px-7 py-3.5" style={{ fontSize: 22, color: PALETA.medio, background: translucido(0.85) }}>
        {['pasa', 'falla', 'no_pude', 'pendiente'].map((estado) => (
            <span key={estado} className="flex items-center gap-2.5"><Punto color={ESTADOS[estado]} />{NOMBRES_ESTADO[estado]}</span>
        ))}
        {agrupado && <span className="flex items-center gap-2.5"><Anillado />Sección con muchos casos: anillo = sus estados</span>}
        <span className="flex items-center gap-2.5">
            <Punto color={PALETA.leyendaPersona} tam={22} borde={`3px solid ${PALETA.texto}`} />
            Persona: tamaño = casos marcados, anillo = su avance, línea a cada proyecto en que participa
        </span>
    </footer>
);

const Cifra = ({ texto, valor, color = PALETA.texto }) => (
    <div className="flex min-w-[150px] flex-col gap-1 rounded-[20px] px-[22px] py-4" style={{ background: translucido(0.85) }}>
        <span style={{ fontSize: 18, color: PALETA.tenue }}>{texto}</span>
        <span style={{ fontSize: 40, fontFamily: 'var(--tipo-negrita)', fontWeight: 700, color }}>{valor}</span>
    </div>
);

export const Cifras = ({ cifras }) => (
    <aside className="pointer-events-none absolute right-16 top-10 flex gap-4">
        <Cifra texto="Casos marcados" valor={porcentaje(cifras.marcado)} />
        <Cifra texto="Fallas" valor={cifras.fallas} color={PALETA.fallaTexto} />
        <Cifra texto="Validando ahora" valor={cifras.activas} />
    </aside>
);
