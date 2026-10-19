import { useId, useState } from 'react';
import { Edit, Info } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { ChipResultado } from '@/components/ChipResultado';
import { BotonIcono } from '@/components/fallas/BotonIcono';
import { Capturas } from '@/components/fallas/Capturas';
import { ChipsVinculo } from '@/components/fallas/ChipsVinculo';
import { Dato, Detalles } from '@/components/fallas/Detalles';
import { ChipPlazo, EstadoEmergente } from '@/components/fallas/EstadoEmergente';
import { NotaResolucion } from '@/components/fallas/NotaResolucion';
import { Seguimiento } from '@/components/fallas/Seguimiento';
import { useActualizarFalla } from '@/hooks/useValidacion';
import { ESTADOS_FALLA, REPRODUCIBLE, SEVERIDADES } from '@/utils/etiquetas';
import { describirNavegador, formatearFecha } from '@/utils/formato';
import { idRegistro } from '@/utils/seguimiento';

export const FallaCard = ({ falla, editable }) => {
    const actualizar = useActualizarFalla();
    const idDetalles = useId();
    const [detalles, setDetalles] = useState(false);
    const [editandoNota, setEditandoNota] = useState(false);
    const cambiar = (cambios, alTerminar) => actualizar.mutate({ id: falla.id, ...cambios }, { onSuccess: alTerminar });
    const titulo = falla.seccion_completa ? falla.seccion_titulo : falla.caso_titulo || falla.caso_id;
    const abrirNota = () => {
        setEditandoNota(true);
        requestAnimationFrame(() => document.getElementById(`nota-${falla.id}`)?.focus());
    };

    return (
        <li id={idRegistro('falla', falla.id)} tabIndex={-1} className="min-w-0 scroll-mt-24 rounded-2xl bg-white p-5 shadow-[0px_3px_12px_var(--color-sombra-tenue)] focus:outline-none focus-visible:ring-2 focus-visible:ring-primario">
            <div className="flex items-start justify-between gap-3">
                <div className="flex min-w-0 flex-wrap items-center gap-2">
                    <span className="tipo-media text-xs text-texto-apagado">#{falla.id} · {falla.caso_id}</span>
                    <Chip tono={SEVERIDADES[falla.severidad].tono}>{SEVERIDADES[falla.severidad].texto}</Chip>
                    <Chip tono="marca">{falla.sistema || 'sin sistema'}</Chip>
                    {falla.seccion_completa && <Chip tono="aviso">Sección completa</Chip>}
                    {falla.tipo === 'no_pude' && <ChipResultado estado="no_pude" />}
                    <ChipPlazo plazo={falla.plazo} resuelto={falla.estado === 'cerrada'} textoVencido="Vencida" />
                    <ChipsVinculo registro={falla} />
                </div>
                <div className="flex shrink-0 items-center gap-1.5 print:hidden">
                    <EstadoEmergente
                        id={`falla-${falla.id}`}
                        objeto="falla"
                        registro={falla}
                        estados={ESTADOS_FALLA}
                        final="cerrada"
                        editable={editable}
                        etiqueta="Estado, plazo y esfuerzo de la falla"
                        resolucion={{ en: falla.resuelta_en, por: falla.resuelta_por_nombre || falla.resuelta_por, desde: falla.creada }}
                        onCambiar={(cambios) => cambiar(cambios)}
                        textoVencido="Vencida"
                        error={actualizar.error?.message}
                    />
                    {editable && (
                        <BotonIcono
                            etiqueta={falla.nota_resolucion ? 'Editar nota de resolución' : 'Agregar nota de resolución'}
                            icono={Edit}
                            tono={editandoNota ? 'activo' : 'neutro'}
                            aria-pressed={editandoNota}
                            onClick={() => (editandoNota ? setEditandoNota(false) : abrirNota())}
                        />
                    )}
                    <BotonIcono
                        etiqueta="Detalles"
                        icono={Info}
                        tono={detalles ? 'activo' : 'neutro'}
                        aria-expanded={detalles}
                        aria-controls={idDetalles}
                        onClick={() => setDetalles((actual) => !actual)}
                    />
                </div>
            </div>
            <div className="mt-3 flex flex-col gap-4 sm:flex-row sm:items-start">
                <div className="min-w-0 flex-1">
                    <h3 className="wrap-anywhere tipo-negrita text-base text-texto">{titulo}</h3>
                    <p className="mt-2 whitespace-pre-line wrap-anywhere tipo-regular text-[15px]/6 text-texto">{falla.obtenido}</p>
                </div>
                <Capturas evidencias={falla.evidencias} titulo={`Falla #${falla.id}`} />
            </div>
            <NotaResolucion
                key={`${editandoNota}-${falla.nota_resolucion}`}
                id={falla.id}
                nota={falla.nota_resolucion}
                editando={editable && editandoNota}
                guardando={actualizar.isPending}
                onGuardar={(nota, alTerminar) => cambiar({ nota_resolucion: nota }, alTerminar)}
                onCerrar={() => setEditandoNota(false)}
            />
            {actualizar.error && <p className="mt-2 tipo-media text-xs text-error-fuerte">{actualizar.error.message}</p>}
            <Detalles id={idDetalles} abierto={detalles}>
                <Dato termino="Paso">{falla.paso === null ? 'Fuera de los pasos' : `${falla.paso + 1}. ${falla.paso_texto}`}</Dato>
                {falla.tipo !== 'no_pude' && <Dato termino="Se repite">{REPRODUCIBLE[falla.reproducible]}</Dato>}
                <Dato termino="Reportó">{falla.usuario_email}</Dato>
                <Dato termino="Fecha">{formatearFecha(falla.creada)}</Dato>
                <Dato termino="Navegador"><span title={falla.navegador}>{falla.navegador ? describirNavegador(falla.navegador) : ''}</span></Dato>
                <Dato termino="Versión visible">{falla.version_visible}</Dato>
                <Dato termino="Dirección">{falla.url}</Dato>
            </Detalles>
            <Seguimiento objeto="falla" id={falla.id} eventos={falla.seguimiento} estados={ESTADOS_FALLA} editable={editable} />
        </li>
    );
};
