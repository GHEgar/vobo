import { useState } from 'react';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { useHistorial, useRestaurarVersion } from '@/hooks/useEditor';
import { ACCIONES } from '@/utils/editor';
import { formatearFecha } from '@/utils/formato';
import { History, Undo } from 'tesela/react';

const resumen = (version) => {
    if (version.tipo === 'media') return version.datos ? `Antes: ${version.datos.archivo}` : 'Sin animación previa';
    if (!version.datos) return 'Sin estado anterior';
    const casos = version.datos.casos?.length;
    return `Antes: «${version.datos.titulo || version.objeto_id}»${casos !== undefined ? ` · ${casos} casos` : ''}`;
};

const Lista = ({ tipo, id, onRestaurada }) => {
    const historial = useHistorial(tipo, id);
    const restaurar = useRestaurarVersion();
    const [confirmando, setConfirmando] = useState(null);

    if (historial.isPending) return <Spinner />;
    if (historial.error) return <ErrorState mensaje={historial.error.message} onReintentar={historial.refetch} />;
    if (!historial.data.length) return <EmptyState icono={History} titulo="Todavía no hay cambios registrados" />;

    return (
        <>
            {restaurar.error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{restaurar.error.message}</p>}
            <ol className="flex flex-col gap-2">
                {historial.data.map((v) => (
                    <li key={v.id} className="flex flex-col gap-2 rounded-2xl bg-fondo px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                        <div className="min-w-0">
                            <p className="tipo-negrita text-sm text-texto">
                                {ACCIONES[v.accion] ?? v.accion}
                                <span className="tipo-media text-[11px] text-texto-apagado"> · {formatearFecha(v.creado)} · {v.autor_email}</span>
                            </p>
                            <p className="tipo-media text-xs text-texto-tenue">{resumen(v)}</p>
                        </div>
                        {v.tipo !== 'media' && v.datos && (
                            <div className="flex shrink-0 gap-2">
                                {confirmando === v.id ? (
                                    <>
                                        <Button label="Confirmar" small variant="warn" loading={restaurar.isPending} onClick={() => restaurar.mutate(v.id, { onSuccess: onRestaurada })} />
                                        <Button label="Cancelar" small variant="link" onClick={() => setConfirmando(null)} />
                                    </>
                                ) : (
                                    <Button label="Restaurar este estado" icono={<Undo size={16} />} small variant="ghost" onClick={() => setConfirmando(v.id)} />
                                )}
                            </div>
                        )}
                        {v.tipo === 'media' && <Chip>Animación</Chip>}
                    </li>
                ))}
            </ol>
        </>
    );
};

export const Historial = ({ abierto, tipo, id, titulo, onCerrar }) => (
    <Modal abierto={abierto} titulo={`Historial de ${titulo || id}`} onCerrar={onCerrar}>
        <p className="tipo-media text-xs text-texto-apagado">Cada fila guarda cómo estaba antes del cambio. Restaurar crea un cambio nuevo; no borra el historial.</p>
        {abierto && <Lista tipo={tipo} id={id} onRestaurada={onCerrar} />}
    </Modal>
);
