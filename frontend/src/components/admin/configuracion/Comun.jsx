import { Button } from '@/components/Button';
import { useMutationState } from '@tanstack/react-query';
import { CLAVE_MUTACION, useRestablecerConfiguracion } from '@/hooks/useAdmin';

export const Origen = ({ guardado }) => (
    <span className={`tipo-media text-[11px] ${guardado ? 'text-aviso-texto' : 'text-texto-apagado'}`}>
        {guardado ? 'Guardado en la app' : 'De los archivos de la instalación'}
    </span>
);

export const Restablecer = ({ clave, guardada, etiqueta = 'Restablecer' }) => {
    const restablecer = useRestablecerConfiguracion();
    if (!(clave in guardada)) return null;
    return (
        <span className="inline-flex flex-col items-end">
            <Button label={etiqueta} small variant="link" loading={restablecer.isPending} onClick={() => restablecer.mutate(clave)} />
            {restablecer.error && <span role="alert" className="tipo-media text-xs text-error-fuerte">{restablecer.error.message}</span>}
        </span>
    );
};

export const Encabezado = ({ titulo, descripcion, clave, guardada, children }) => (
    <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0">
            <h3 className="tipo-negrita text-sm text-texto">{titulo}</h3>
            {descripcion && <p className="tipo-media text-xs text-texto-apagado">{descripcion}</p>}
            {clave && <Origen guardado={clave in guardada} />}
        </div>
        <div className="flex shrink-0 items-center gap-2">
            {children}
            {clave && <Restablecer clave={clave} guardada={guardada} />}
        </div>
    </div>
);

export const PieGuardar = ({ mutacion, deshabilitado, etiqueta = 'Guardar' }) => (
    <div className="mt-6 flex flex-col items-end gap-2">
        {mutacion.error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{mutacion.error.message}</p>}
        <Button label={etiqueta} type="submit" disabled={deshabilitado} loading={mutacion.isPending} />
    </div>
);

export const EstadoGuardado = () => {
    const estados = useMutationState({ filters: { mutationKey: CLAVE_MUTACION }, select: (m) => m.state.status });
    const ultimo = estados.at(-1);
    if (ultimo !== 'success') return null;
    return <p role="status" className="tipo-media text-xs text-pasa">Cambios guardados</p>;
};
