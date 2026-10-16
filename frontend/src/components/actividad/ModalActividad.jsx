import { useState } from 'react';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Ahora } from '@/components/actividad/Ahora';
import { Reciente } from '@/components/actividad/Reciente';
import { usePresentes } from '@/hooks/useValidacion';

const Encabezado = ({ children, detalle }) => (
    <h3 className="mb-3 hidden items-baseline gap-2 tipo-negrita text-base text-texto md:flex">
        {children}
        {detalle && <span className="tipo-media text-xs text-texto-apagado">{detalle}</span>}
    </h3>
);

const Contenido = ({ onCerrar }) => {
    const [vista, setVista] = useState('ahora');
    const presentes = usePresentes();
    const activos = presentes.data?.filter((p) => p.estado === 'activo').length ?? 0;
    const detalle = presentes.data ? `${activos === 1 ? '1 activa' : `${activos} activas`} · últimos 10 min` : null;

    return (
        <>
            <div className="flex w-fit gap-1 rounded-full bg-fondo p-1 md:hidden" role="group" aria-label="Vista de actividad">
                <Button label="Ahora" small variant={vista === 'ahora' ? 'primary' : 'link'} pressed={vista === 'ahora'} onClick={() => setVista('ahora')} />
                <Button label="Reciente" small variant={vista === 'reciente' ? 'primary' : 'link'} pressed={vista === 'reciente'} onClick={() => setVista('reciente')} />
            </div>
            <div className="grid min-h-0 grid-cols-1 gap-6 md:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
                <section aria-label="Ahora" className={`min-w-0 md:block md:max-h-[68dvh] md:overflow-y-auto md:pr-1 ${vista === 'ahora' ? '' : 'hidden'}`}>
                    <Encabezado detalle={detalle}>Ahora</Encabezado>
                    <Ahora consulta={presentes} onNavegar={onCerrar} />
                </section>
                <section aria-label="Actividad reciente" className={`min-w-0 md:block md:max-h-[68dvh] md:overflow-y-auto md:pr-1 ${vista === 'reciente' ? '' : 'hidden'}`}>
                    <Encabezado>Actividad reciente</Encabezado>
                    <Reciente presentes={presentes.data ?? []} onNavegar={onCerrar} />
                </section>
            </div>
        </>
    );
};

export const ModalActividad = ({ abierto, onCerrar }) => (
    <Modal abierto={abierto} titulo="Actividad" onCerrar={onCerrar} ancho="max-w-[1100px]">
        {abierto && <Contenido onCerrar={onCerrar} />}
    </Modal>
);
