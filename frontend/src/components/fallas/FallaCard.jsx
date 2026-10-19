import { Chip } from '@/components/Chip';
import { ChipResultado } from '@/components/ChipResultado';
import { Capturas } from '@/components/fallas/Capturas';
import { Dato, Detalles } from '@/components/fallas/Detalles';
import { EstadoCampo, Franja } from '@/components/fallas/Franja';
import { NotaResolucion } from '@/components/fallas/NotaResolucion';
import { PlazoCampo } from '@/components/fallas/PlazoCampo';
import { Resolucion } from '@/components/fallas/Resolucion';
import { Seguimiento } from '@/components/fallas/Seguimiento';
import { useActualizarFalla } from '@/hooks/useValidacion';
import { ESTADOS_FALLA, REPRODUCIBLE, SEVERIDADES } from '@/utils/etiquetas';
import { describirNavegador, formatearFecha } from '@/utils/formato';

export const FallaCard = ({ falla, editable }) => {
    const actualizar = useActualizarFalla();
    const cambiar = (cambios, alTerminar) => actualizar.mutate({ id: falla.id, ...cambios }, { onSuccess: alTerminar });
    const titulo = falla.seccion_completa ? falla.seccion_titulo : falla.caso_titulo || falla.caso_id;

    return (
        <li className="min-w-0 rounded-2xl bg-white p-5 shadow-[0px_3px_12px_var(--color-sombra-tenue)]">
            <div className="flex flex-wrap items-center gap-2">
                <span className="tipo-media text-xs text-texto-apagado">#{falla.id} · {falla.caso_id}</span>
                <Chip tono={SEVERIDADES[falla.severidad].tono}>{SEVERIDADES[falla.severidad].texto}</Chip>
                <Chip tono="marca">{falla.sistema || 'sin sistema'}</Chip>
                {falla.seccion_completa && <Chip tono="aviso">Sección completa</Chip>}
                {falla.tipo === 'no_pude' && <ChipResultado estado="no_pude" />}
            </div>
            <h3 className="mt-2 wrap-anywhere tipo-negrita text-base text-texto">{titulo}</h3>
            <p className="mt-2 whitespace-pre-line wrap-anywhere tipo-regular text-[15px]/6 text-texto">{falla.obtenido}</p>
            <Franja etiqueta={`Estado, plazo y capturas de la falla ${falla.id}`}>
                <EstadoCampo
                    id={`estado-${falla.id}`}
                    valor={falla.estado}
                    estados={ESTADOS_FALLA}
                    editable={editable}
                    etiqueta="Estado de la falla"
                    onCambiar={(estado) => cambiar({ estado })}
                >
                    <Resolucion en={falla.resuelta_en} por={falla.resuelta_por_nombre || falla.resuelta_por} desde={falla.creada} />
                </EstadoCampo>
                <PlazoCampo
                    id={`falla-${falla.id}`}
                    plazo={falla.plazo}
                    responsable={falla.plazo_por_nombre || falla.plazo_por}
                    resuelto={falla.estado === 'cerrada'}
                    editable={editable}
                    onCambiar={(plazo) => cambiar({ plazo })}
                />
                <Capturas evidencias={falla.evidencias} titulo={`Falla #${falla.id}`} />
            </Franja>
            <NotaResolucion
                id={falla.id}
                nota={falla.nota_resolucion}
                editable={editable}
                guardando={actualizar.isPending}
                onGuardar={(nota, alTerminar) => cambiar({ nota_resolucion: nota }, alTerminar)}
            />
            {actualizar.error && <p className="mt-2 tipo-media text-xs text-error-fuerte">{actualizar.error.message}</p>}
            <Detalles>
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
