import { useState } from 'react';
import { MediaImagen } from '@/components/MediaImagen';
import { Modal } from '@/components/Modal';

export const Capturas = ({ evidencias, titulo }) => {
    const [ampliada, setAmpliada] = useState(null);
    if (!evidencias.length) return null;
    return (
        <>
            <ul aria-label={`Capturas (${evidencias.length})`} className="flex shrink-0 flex-wrap gap-2 sm:max-w-[272px] sm:justify-end">
                {evidencias.map((e, i) => (
                    <li key={e.id}>
                        <button
                            type="button"
                            onClick={() => setAmpliada(e)}
                            aria-label={`Ampliar captura ${i + 1} de ${evidencias.length}`}
                            className="block overflow-hidden rounded-lg p-0 shadow-[0px_2px_8px_var(--color-sombra-tenue)] hover:ring-2 hover:ring-primario focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario"
                        >
                            <MediaImagen url={e.url} alt={`Captura ${i + 1} de ${titulo}`} className="h-24 w-32 object-cover" />
                        </button>
                    </li>
                ))}
            </ul>
            <Modal abierto={Boolean(ampliada)} titulo={titulo} onCerrar={() => setAmpliada(null)} ancho="max-w-5xl">
                {ampliada && <img src={ampliada.url} alt={`Captura de ${titulo}`} className="max-h-[75dvh] w-full rounded-xl object-contain" />}
            </Modal>
        </>
    );
};
