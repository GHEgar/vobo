import { lazy, Suspense } from 'react';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { EnlaceEditor } from '@/components/edicion/EnlaceEditor';

const FormularioCaso = lazy(() => import('@/components/edicion/FormularioCaso'));

const TITULOS = { nuevo: 'Nuevo caso', duplicar: 'Duplicar caso', editar: 'Editar caso' };

export const ModalCaso = ({ seccionId, pedido, onCerrar, onGuardado }) => (
    <Modal abierto={Boolean(pedido)} titulo={pedido ? `${TITULOS[pedido.tipo]}${pedido.casoId ? ` · ${pedido.casoId}` : ''}` : ''} onCerrar={onCerrar}>
        {pedido && (
            <>
                <EnlaceEditor seccionId={seccionId} onClick={onCerrar} />
                <Suspense fallback={<Spinner />}>
                    <FormularioCaso key={`${pedido.tipo}-${pedido.casoId ?? ''}`} seccionId={seccionId} pedido={pedido} onCerrar={onCerrar} onGuardado={onGuardado} />
                </Suspense>
            </>
        )}
    </Modal>
);
