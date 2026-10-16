import { lazy, Suspense } from 'react';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { EnlaceEditor } from '@/components/edicion/EnlaceEditor';
import { useEdicion } from '@/hooks/useEdicion';

const FormSeccion = lazy(() => import('@/components/editor/FormSeccion').then((m) => ({ default: m.FormSeccion })));

export const ModalSeccion = ({ pedido, onCerrar }) => {
    const { sistemas } = useEdicion();
    const titulo = pedido?.id ? `Editar ${pedido.titulo ?? 'sección'}` : 'Nueva sección';
    return (
        <Modal abierto={Boolean(pedido)} titulo={titulo} onCerrar={onCerrar} ancho="max-w-5xl">
            {pedido && (
                <>
                    <EnlaceEditor seccionId={pedido.id} onClick={onCerrar} />
                    <Suspense fallback={<Spinner />}>
                        <FormSeccion
                            key={pedido.id ?? 'nueva'}
                            incrustado
                            seccionId={pedido.id}
                            sistemas={sistemas}
                            inicial={pedido.inicial}
                            onGuardada={onCerrar}
                            onVolver={onCerrar}
                        />
                    </Suspense>
                </>
            )}
        </Modal>
    );
};
