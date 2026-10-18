import { Anillo } from '@/components/pantalla/Anillo';
import { Cinta } from '@/components/pantalla/Cinta';
import { Encabezado } from '@/components/pantalla/Encabezado';
import { useRotacion } from '@/hooks/usePantalla';
import { ESTADOS, PALETA } from '@/utils/pantalla/paleta';
import { enGrupos, porcentaje } from '@/utils/pantalla/formato';

const POR_GRUPO = 3;

const Punto = ({ color, tam }) => <span aria-hidden="true" className="inline-block shrink-0 rounded-full" style={{ width: tam, height: tam, background: color }} />;

const Leyenda = ({ color, children }) => (
    <span className="flex items-center gap-2">
        <span aria-hidden="true" className="rounded" style={{ width: 16, height: 16, background: color }} />
        {children}
    </span>
);

const Cifra = ({ titulo, children }) => (
    <div className="flex min-w-0 flex-col gap-1.5 rounded-[20px] px-4 py-4" style={{ background: PALETA.tarjetaAlta }}>
        <span className="truncate" style={{ fontSize: 17, color: PALETA.tenue }}>{titulo}</span>
        <span className="flex items-center gap-2.5 whitespace-nowrap" style={{ fontSize: 36, fontFamily: 'var(--tipo-negrita)', fontWeight: 700 }}>{children}</span>
    </div>
);

const Alerta = () => (
    <svg aria-hidden="true" width="26" height="26" viewBox="0 0 24 24" fill="none" stroke={ESTADOS.falla} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 3 2 20h20L12 3z" />
        <path d="M12 10v4" />
        <path d="M12 17.5v.5" />
    </svg>
);

const Tarjeta = ({ proyecto }) => {
    const { conteos, total } = proyecto;
    const marcados = total - conteos.pendiente;
    const pct = porcentaje(proyecto.avance);
    const etiqueta = `${proyecto.nombre}: ${pct} marcado; ${conteos.pasa} pasan, ${conteos.falla} fallan, ${conteos.no_pude} no pude`;
    return (
        <section className="flex w-[560px] flex-col items-center gap-6 rounded-[32px] px-6 py-8" style={{ background: PALETA.tarjeta }}>
            <h2 className="m-0 flex max-w-full items-center gap-4" style={{ fontSize: 38, fontFamily: 'var(--tipo-negrita)', fontWeight: 600 }}>
                <Punto color={proyecto.color} tam={22} />
                <span className="truncate">{proyecto.nombre}</span>
            </h2>
            <Anillo conteos={conteos} total={total} etiqueta={etiqueta}>
                <span style={{ fontSize: 112, fontFamily: 'var(--tipo-negrita)', fontWeight: 700, lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>{pct}</span>
                <span style={{ fontSize: 24, color: PALETA.tenue }}>{marcados} de {total} casos</span>
            </Anillo>
            <div className="flex gap-5" style={{ fontSize: 22, color: PALETA.medio }}>
                <Leyenda color={ESTADOS.pasa}>{conteos.pasa} pasan</Leyenda>
                <Leyenda color={ESTADOS.falla}>{conteos.falla} fallan</Leyenda>
                <Leyenda color={ESTADOS.no_pude}>{conteos.no_pude} no pude</Leyenda>
            </div>
            <div className="grid w-full grid-cols-[1fr_1.25fr_1fr] gap-3">
                <Cifra titulo={proyecto.ronda?.nombre ?? 'Sin ronda abierta'}>{proyecto.ronda ? `día ${proyecto.ronda.dia}` : '—'}</Cifra>
                <Cifra titulo="Fallas abiertas"><Alerta />{proyecto.fallas_abiertas}</Cifra>
                <Cifra titulo="En línea"><Punto color={PALETA.vivo} tam={14} />{proyecto.en_linea}</Cifra>
            </div>
        </section>
    );
};

const VistaGeneral = ({ config, datos, sinConexion, segundos }) => {
    const grupos = enGrupos(datos.proyectos, POR_GRUPO);
    const indice = useRotacion(grupos.length, Math.max(6, Math.floor(segundos / Math.max(grupos.length, 1))));
    const visibles = grupos[indice] ?? [];
    return (
        <div className="flex h-full flex-col">
            <Encabezado config={config} subtitulo="Avance de los proyectos" sinConexion={sinConexion} />
            <main className="flex min-h-0 grow items-start justify-center gap-12 px-[72px] pb-8 pt-10">
                {visibles.map((p) => <Tarjeta key={p.clave} proyecto={p} />)}
                {visibles.length === 0 && <span style={{ fontSize: 32, color: PALETA.tenue }}>No hay proyectos activos en esta pantalla</span>}
            </main>
            <Cinta eventos={datos.eventos} />
        </div>
    );
};

export default VistaGeneral;
