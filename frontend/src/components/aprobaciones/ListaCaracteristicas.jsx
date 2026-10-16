import { useState } from 'react';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { ChipResultado } from '@/components/ChipResultado';
import { MediaImagen } from '@/components/MediaImagen';
import { Modal } from '@/components/Modal';
import { BotonesAprobacion } from '@/components/aprobaciones/BotonesAprobacion';
import { QuienCuando } from '@/components/aprobaciones/QuienCuando';
import { APROBACIONES } from '@/utils/etiquetas';
import { animacionDe } from '@/utils/aprobaciones';
import { Play } from 'tesela/react';

export const ListaCaracteristicas = ({ caracteristicas, indice, puedeAprobar, onDecidir, guardando }) => {
    const [viendo, setViendo] = useState(null);
    return (
        <>
            <ul className="flex flex-col gap-2">
                {caracteristicas.map((c) => {
                    const animacion = animacionDe(indice, c.caso_id);
                    const aprobacion = APROBACIONES[c.aprobacion.estado];
                    return (
                        <li key={c.caso_id} className="flex flex-col gap-2 rounded-xl bg-white px-4 py-3 md:flex-row md:items-center md:justify-between">
                            <div className="min-w-0">
                                <p className="tipo-negrita text-sm text-texto">{c.titulo}</p>
                                <div className="mt-1 flex flex-wrap items-center gap-2">
                                    <span className="tipo-media text-[11px] text-texto-apagado">{c.caso_id}</span>
                                    <ChipResultado estado={c.estado} />
                                    {c.fallas_abiertas > 0 && <Chip tono="error">{c.fallas_abiertas} falla(s) abierta(s)</Chip>}
                                    <Chip tono={aprobacion.tono}>{aprobacion.texto}</Chip>
                                    {animacion && <Button label="Ver cómo" icono={<Play size={16} />} variant="link" small onClick={() => setViendo({ titulo: c.titulo, animacion })} />}
                                </div>
                                <QuienCuando registro={c.aprobacion.actual} prefijo={c.aprobacion.origen === 'herramienta' ? 'Por la herramienta' : null} />
                            </div>
                            {puedeAprobar && (
                                <BotonesAprobacion id={`comentario-${c.caso_id}`} etiqueta={c.titulo} small guardando={guardando} onDecidir={(estado, comentario) => onDecidir('caracteristica', c.caso_id, estado, comentario)} />
                            )}
                        </li>
                    );
                })}
            </ul>
            <Modal abierto={Boolean(viendo)} titulo={viendo?.titulo} onCerrar={() => setViendo(null)} ancho="max-w-5xl">
                {viendo && <MediaImagen url={viendo.animacion.url} alt={viendo.animacion.titulo || viendo.titulo} className="max-h-[75dvh] w-full rounded-xl object-contain" />}
            </Modal>
        </>
    );
};
