import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { EncabezadoImpreso } from '@/components/EncabezadoImpreso';
import { BOTON_IMPRESO as BOTON, HojaImpresa } from '@/components/HojaImpresa';
import { OpcionesInforme } from '@/components/informe/OpcionesInforme';
import { ParticipacionInforme } from '@/components/informe/ParticipacionInforme';
import { ProyectoInforme } from '@/components/informe/ProyectoInforme';
import { ResumenInforme } from '@/components/informe/ResumenInforme';
import { useDatosInforme, useRondasDe } from '@/hooks/useInformeFallas';
import { useProyecto } from '@/hooks/useProyecto';
import { useSistemas } from '@/hooks/useInstancia';
import { formatearFecha } from '@/utils/formato';
import {
    agruparPorHerramienta,
    conOpciones,
    describirOpciones,
    filtrarComentarios,
    filtrarFallas,
    herramientasDe,
    opcionesDe,
    resumenProyecto,
} from '@/utils/informeFallas';
import { nombreSistema } from '@/utils/sistemas';
import { csvInforme, descargarCsv, nombreArchivo } from '@/utils/csvInforme';
import { hoyISO } from '@/utils/seguimiento';
import { ArrowLeft, Document, FileTable, Filter } from 'tesela/react';

const InformeFallas = () => {
    const [params, setParams] = useSearchParams();
    const { proyectos, clave } = useProyecto();
    const sistemas = useSistemas();
    const nombre = (s) => nombreSistema(sistemas, s);
    const opciones = useMemo(() => opcionesDe(params, clave, proyectos), [params, clave, proyectos]);
    const unico = opciones.proyectos.length === 1 ? opciones.proyectos[0] : null;
    const { data: rondas = [] } = useRondasDe(unico, true);
    const ronda = rondas.find((r) => String(r.id) === opciones.ronda);
    const datos = useDatosInforme(opciones.proyectos, opciones.ronda, opciones.incluir.has('comentarios'));
    const [generado] = useState(() => formatearFecha(new Date().toISOString()));

    const cambiar = (cambios) => {
        setParams((previos) => conOpciones(previos, opcionesDe(previos, clave, proyectos), cambios), { replace: true });
    };

    const secciones = datos.porProyecto.map((p) => {
        const fallas = filtrarFallas(p.fallas, opciones);
        const comentarios = filtrarComentarios(p.comentarios, opciones);
        return {
            clave: p.clave,
            nombre: proyectos.find((x) => x.clave === p.clave)?.nombre ?? p.clave,
            fallas,
            comentarios,
            grupos: agruparPorHerramienta(fallas, comentarios, nombre),
            resumen: resumenProyecto(fallas, comentarios),
        };
    });
    const vacio = secciones.every((s) => !s.fallas.length && !s.comentarios.length);
    const nombres = secciones.map((s) => s.nombre).join(', ');
    const archivo = nombreArchivo(secciones.map((s) => s.nombre), hoyISO());

    useEffect(() => {
        let previo = document.title;
        const antes = () => {
            previo = document.title;
            document.title = archivo;
        };
        const despues = () => {
            document.title = previo;
        };
        window.addEventListener('beforeprint', antes);
        window.addEventListener('afterprint', despues);
        return () => {
            window.removeEventListener('beforeprint', antes);
            window.removeEventListener('afterprint', despues);
        };
    }, [archivo]);

    const acciones = (
        <div className="flex flex-wrap gap-2">
            <Link to={`/fallas?${params}`} className={`${BOTON} bg-borde text-texto-tenue`}><ArrowLeft size={18} className="shrink-0" />Volver</Link>
            <button type="button" onClick={() => window.print()} className={`${BOTON} bg-primario text-white`}><Document size={18} className="shrink-0" />Imprimir / guardar PDF</button>
            <button type="button" disabled={datos.isPending || vacio} onClick={() => descargarCsv(csvInforme(secciones), `${archivo}.csv`)} className={`${BOTON} border border-primario bg-white text-primario disabled:opacity-50`}><FileTable size={18} className="shrink-0" />Descargar CSV</button>
        </div>
    );

    return (
        <HojaImpresa acciones={acciones}>
            <OpcionesInforme
                opciones={opciones}
                proyectos={proyectos}
                herramientas={herramientasDe(datos.porProyecto)}
                nombreSistema={nombre}
                rondas={rondas}
                onCambiar={cambiar}
            />
            <EncabezadoImpreso titulo="Informe de fallas y comentarios" nombre={unico ? secciones[0]?.nombre ?? '' : ''}>
                <p className="mt-1 tipo-media text-sm text-texto-tenue">
                    {unico ? 'Proyecto' : 'Proyectos'}: {nombres || '—'} · Ronda: {ronda ? `${ronda.nombre}${ronda.snapshot ? ` (${ronda.snapshot})` : ''}` : 'Todas'} · Generado: {generado}
                </p>
                <p className="mt-1 tipo-media text-xs text-texto-apagado">
                    {describirOpciones(opciones, nombre).map(([k, v]) => `${k}: ${v}`).join(' · ')}
                </p>
            </EncabezadoImpreso>
            {datos.isPending && <div className="mt-8"><Spinner /></div>}
            {datos.error && <div className="mt-8"><ErrorState mensaje={datos.error.message} onReintentar={datos.refetch} /></div>}
            {!datos.isPending && !datos.error && (
                <>
                    {opciones.incluir.has('resumen') && <ResumenInforme proyectos={secciones} incluir={opciones.incluir} />}
                    {opciones.incluir.has('participacion') && <ParticipacionInforme claves={opciones.proyectos} ronda={opciones.ronda} archivo={`participacion-${hoyISO()}`} />}
                    {vacio ? (
                        <p className="mt-8 flex items-center gap-2 text-sm text-texto-tenue"><Filter size={16} className="shrink-0" />No hay fallas ni comentarios con estas opciones.</p>
                    ) : (
                        secciones.map((s) => <ProyectoInforme key={s.clave} proyecto={s} incluir={opciones.incluir} />)
                    )}
                </>
            )}
        </HojaImpresa>
    );
};

export default InformeFallas;
