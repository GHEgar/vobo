import { useState } from 'react';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { ChipResultado } from '@/components/ChipResultado';
import { AvisarFalla } from '@/components/avisos/AvisarFalla';
import { MediaImagen } from '@/components/MediaImagen';
import { Modal } from '@/components/Modal';
import { SelectField, TextField } from '@/components/Field';
import { useActualizarFalla } from '@/hooks/useValidacion';
import { ESTADOS_FALLA, REPRODUCIBLE, SEVERIDADES, opciones } from '@/utils/etiquetas';
import { describirNavegador, formatearFecha } from '@/utils/formato';

const Dato = ({ termino, children }) => (
    <div>
        <dt className="tipo-media text-[11px] text-texto-apagado">{termino}</dt>
        <dd className="break-words tipo-media text-sm text-texto">{children || '—'}</dd>
    </div>
);

export const FallaCard = ({ falla, editable }) => {
    const actualizar = useActualizarFalla();
    const [nota, setNota] = useState(falla.nota_resolucion);
    const [ampliada, setAmpliada] = useState(null);
    const cambiar = (cambios) => actualizar.mutate({ id: falla.id, ...cambios });

    return (
        <li className="rounded-2xl bg-white p-5 shadow-[0px_3px_12px_var(--color-sombra-tenue)]">
            <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="flex flex-col gap-2">
                    <div className="flex flex-wrap items-center gap-2">
                        <span className="tipo-media text-xs text-texto-apagado">#{falla.id} · {falla.caso_id}</span>
                        <Chip tono={SEVERIDADES[falla.severidad].tono}>{SEVERIDADES[falla.severidad].texto}</Chip>
                        <Chip tono="marca">{falla.sistema || 'sin sistema'}</Chip>
                        {falla.seccion_completa && <Chip tono="aviso">Sección completa</Chip>}
                        {falla.tipo === 'no_pude' && <ChipResultado estado="no_pude" />}
                    </div>
                    <h3 className="tipo-negrita text-base text-texto">
                        {falla.seccion_completa ? falla.seccion_titulo : falla.caso_titulo || falla.caso_id}
                    </h3>
                </div>
                {editable ? (
                    <SelectField
                        id={`estado-${falla.id}`}
                        aria-label="Estado de la falla"
                        value={falla.estado}
                        onChange={(e) => cambiar({ estado: e.target.value })}
                        options={opciones(ESTADOS_FALLA)}
                        className="w-full sm:w-[220px]"
                    />
                ) : (
                    <Chip tono={ESTADOS_FALLA[falla.estado].tono}>{ESTADOS_FALLA[falla.estado].texto}</Chip>
                )}
            </div>
            <p className="mt-3 whitespace-pre-line tipo-regular text-[15px]/6 text-texto">{falla.obtenido}</p>
            <dl className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                <Dato termino="Paso">{falla.paso === null ? 'Fuera de los pasos' : `${falla.paso + 1}. ${falla.paso_texto}`}</Dato>
                {falla.tipo !== 'no_pude' && <Dato termino="Se repite">{REPRODUCIBLE[falla.reproducible]}</Dato>}
                <Dato termino="Reportó">{falla.usuario_email}</Dato>
                <Dato termino="Fecha">{formatearFecha(falla.creada)}</Dato>
                <Dato termino="Navegador"><span title={falla.navegador}>{falla.navegador ? describirNavegador(falla.navegador) : ''}</span></Dato>
                <Dato termino="Versión visible">{falla.version_visible}</Dato>
                <Dato termino="Dirección">{falla.url}</Dato>
            </dl>
            {falla.evidencias.length > 0 && (
                <ul className="mt-4 flex flex-wrap gap-3">
                    {falla.evidencias.map((e) => (
                        <li key={e.id}>
                            <button type="button" onClick={() => setAmpliada(e)} aria-label="Ampliar captura" className="overflow-hidden rounded-lg p-0">
                                <MediaImagen url={e.url} alt={`Captura de la falla ${falla.id}`} className="h-20 w-28 object-cover" />
                            </button>
                        </li>
                    ))}
                </ul>
            )}
            {!editable && falla.nota_resolucion && (
                <p className="mt-4 tipo-media text-sm text-texto-tenue">Nota de resolución: {falla.nota_resolucion}</p>
            )}
            {editable && <div className="mt-2 flex flex-col gap-3 sm:flex-row sm:items-end">
                <div className="grow">
                    <TextField id={`nota-${falla.id}`} label="Nota de resolución" tooltip="Qué se corrigió y en qué versión, para quien revalide." value={nota} onChange={(e) => setNota(e.target.value)} />
                </div>
                <Button label="Guardar nota" variant="outline" disabled={nota === falla.nota_resolucion} loading={actualizar.isPending} onClick={() => cambiar({ nota_resolucion: nota })} />
            </div>}
            {editable && <div className="mt-4"><AvisarFalla falla={falla} /></div>}
            {actualizar.error && <p className="mt-2 tipo-media text-xs text-error-fuerte">{actualizar.error.message}</p>}
            <Modal abierto={Boolean(ampliada)} titulo={`Falla #${falla.id}`} onCerrar={() => setAmpliada(null)} ancho="max-w-5xl">
                {ampliada && <img src={ampliada.url} alt={`Captura de la falla ${falla.id}`} className="max-h-[75dvh] w-full rounded-xl object-contain" />}
            </Modal>
        </li>
    );
};
