import { useState } from 'react';
import { Eye } from 'tesela/react';
import { ModalActividad } from '@/components/actividad/ModalActividad';
import { useResumenActividad } from '@/hooks/useActividad';

const etiqueta = (activos) => {
    if (!activos) return 'Actividad';
    return `Actividad, ${activos === 1 ? '1 persona activa' : `${activos} personas activas`}`;
};

export const BotonActividad = () => {
    const [abierto, setAbierto] = useState(false);
    const { data } = useResumenActividad();
    const activos = data?.activos ?? 0;

    return (
        <>
            <button
                type="button"
                onClick={() => setAbierto(true)}
                aria-label={etiqueta(activos)}
                title={etiqueta(activos)}
                aria-haspopup="dialog"
                className="relative flex h-[36px] w-[36px] shrink-0 items-center justify-center rounded-full border border-borde bg-transparent text-primario hover:border-primario hover:bg-primario-suave focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario"
            >
                <Eye size={18} className="shrink-0" />
                {activos > 0 && (
                    <span aria-hidden="true" className="absolute -top-1 -right-1 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-exito px-1 tipo-negrita text-[10px] text-white ring-2 ring-white">
                        {activos > 99 ? '99+' : activos}
                    </span>
                )}
            </button>
            <ModalActividad abierto={abierto} onCerrar={() => setAbierto(false)} />
        </>
    );
};
