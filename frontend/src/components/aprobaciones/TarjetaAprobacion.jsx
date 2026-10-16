import { useState } from 'react';
import { Link } from 'react-router';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { BotonesAprobacion } from '@/components/aprobaciones/BotonesAprobacion';
import { ListaCaracteristicas } from '@/components/aprobaciones/ListaCaracteristicas';
import { QuienCuando } from '@/components/aprobaciones/QuienCuando';
import { APROBACIONES, DECISIONES, HOY, SEVERIDADES, SUGERENCIAS } from '@/utils/etiquetas';
import { useRuta } from '@/hooks/useProyecto';

const Recomendacion = ({ herramienta }) => {
    const decision = herramienta.decision;
    if (decision && decision.decision !== 'pendiente') {
        return (
            <div>
                <Chip tono={DECISIONES[decision.decision].tono}>Recomendación: {DECISIONES[decision.decision].texto}</Chip>
                {decision.motivo && <p className="mt-1 tipo-media text-xs text-texto-tenue">{decision.motivo}</p>}
            </div>
        );
    }
    const sugerida = SUGERENCIAS[herramienta.sugerencia];
    return (
        <div>
            <Chip tono={sugerida.tono}>Sugerida: {sugerida.texto}</Chip>
            <p className="mt-1 tipo-media text-xs text-texto-tenue">{herramienta.sugerencia_motivo} · coordinación aún no confirma</p>
        </div>
    );
};

export const TarjetaAprobacion = ({ herramienta, indice, puedeAprobar, onDecidir, guardando }) => {
    const ruta = useRuta();
    const [abierta, setAbierta] = useState(false);
    const fallas = Object.entries(herramienta.fallas_abiertas).filter(([, n]) => n > 0);
    const estado = APROBACIONES[herramienta.aprobacion.estado];
    const { pasa, falla, no_pude: noPude, pendiente } = herramienta.casos;

    return (
        <li className="flex flex-col gap-3 rounded-2xl bg-fondo p-4">
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="tipo-negrita text-base text-texto">{herramienta.nombre}</span>
                        <Chip tono={HOY[herramienta.hoy].tono}>{HOY[herramienta.hoy].texto}</Chip>
                    </div>
                    <Link to={ruta(`/seccion/${herramienta.seccion_id}`)} className="tipo-media text-xs text-primario hover:underline">{herramienta.seccion_titulo}</Link>
                </div>
                <div className="text-right">
                    <Chip tono={estado.tono}>{estado.texto}</Chip>
                    <QuienCuando registro={herramienta.aprobacion.actual} />
                </div>
            </div>
            <Recomendacion herramienta={herramienta} />
            <div className="flex flex-wrap items-center gap-2 tipo-media text-xs text-texto-tenue">
                <span>{pasa} pasa · {falla} falla · {noPude} no pude{pendiente ? ` · ${pendiente} sin probar` : ''}</span>
                {fallas.map(([severidad, n]) => (
                    <Link key={severidad} to={ruta(`/fallas?sistema=${encodeURIComponent(herramienta.sistema)}&severidad=${severidad}`)}>
                        <Chip tono={SEVERIDADES[severidad].tono}>{n} {SEVERIDADES[severidad].texto.toLowerCase()} abierta(s)</Chip>
                    </Link>
                ))}
            </div>
            <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
                {puedeAprobar ? (
                    <BotonesAprobacion id={`comentario-${herramienta.id}`} etiqueta={herramienta.nombre} guardando={guardando} onDecidir={(valor, comentario) => onDecidir('herramienta', herramienta.id, valor, comentario)} />
                ) : <span />}
                <Button
                    label={`${abierta ? 'Ocultar' : 'Ver'} características (${herramienta.caracteristicas.length})`}
                    variant="ghost"
                    small
                    aria-expanded={abierta}
                    onClick={() => setAbierta(!abierta)}
                />
            </div>
            {abierta && (
                <ListaCaracteristicas
                    caracteristicas={herramienta.caracteristicas}
                    indice={indice}
                    puedeAprobar={puedeAprobar}
                    onDecidir={onDecidir}
                    guardando={guardando}
                />
            )}
        </li>
    );
};
