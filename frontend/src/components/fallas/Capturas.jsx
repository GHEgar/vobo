import { useState } from 'react';
import { Label } from '@/components/Label';
import { MediaImagen } from '@/components/MediaImagen';
import { Modal } from '@/components/Modal';

export const Capturas = ({ evidencias, titulo }) => {
    const [ampliada, setAmpliada] = useState(null);
    if (!evidencias.length) return null;
    return (
        <div className="min-w-0">
            <Label as="p" text={`Capturas (${evidencias.length})`} />
            <ul className="mt-3 flex flex-wrap gap-3">
                {evidencias.map((e, i) => (
                    <li key={e.id}>
                        <button
                            type="button"
                            onClick={() => setAmpliada(e)}
                            aria-label={`Ampliar captura ${i + 1} de ${evidencias.length}`}
                            className="block overflow-hidden rounded-lg border border-borde p-0 hover:border-primario focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario"
                        >
                            <MediaImagen url={e.url} alt={`Captura ${i + 1} de ${titulo}`} className="h-24 w-32 object-cover" />
                        </button>
                    </li>
                ))}
            </ul>
            <Modal abierto={Boolean(ampliada)} titulo={titulo} onCerrar={() => setAmpliada(null)} ancho="max-w-5xl">
                {ampliada && <img src={ampliada.url} alt={`Captura de ${titulo}`} className="max-h-[75dvh] w-full rounded-xl object-contain" />}
            </Modal>
        </div>
    );
};
