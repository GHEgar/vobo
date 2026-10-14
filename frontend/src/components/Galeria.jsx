import { useState } from 'react';
import { MediaImagen } from '@/components/MediaImagen';
import { Modal } from '@/components/Modal';

export const Galeria = ({ items }) => {
    const [abierta, setAbierta] = useState(null);
    const conImagen = items.filter((m) => m.url);
    const sinImagen = items.filter((m) => !m.url);
    if (!items.length) return null;

    return (
        <>
            {conImagen.length > 0 && (
                <ul className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {conImagen.map((m) => (
                        <li key={m.procedimiento}>
                            <figure className="flex h-full flex-col gap-2 rounded-2xl bg-fondo p-3">
                                <button type="button" onClick={() => setAbierta(m)} className="overflow-hidden rounded-xl bg-white p-0" aria-label={`Ampliar: ${m.pie}`}>
                                    <MediaImagen url={m.url} alt={m.pie} className="aspect-video w-full object-contain" />
                                </button>
                                <figcaption className="tipo-media text-xs/5 text-texto-tenue">{m.pie}</figcaption>
                            </figure>
                        </li>
                    ))}
                </ul>
            )}
            {sinImagen.length > 0 && (
                <ul className="mt-3 flex list-disc flex-col gap-1 pl-5">
                    {sinImagen.map((m) => (
                        <li key={m.procedimiento} className="tipo-media text-sm text-texto-tenue">{m.pie}</li>
                    ))}
                </ul>
            )}
            <Modal abierto={Boolean(abierta)} titulo={abierta?.pie} onCerrar={() => setAbierta(null)} ancho="max-w-5xl">
                {abierta && <MediaImagen url={abierta.url} alt={abierta.pie} className="max-h-[75dvh] w-full rounded-xl object-contain" />}
            </Modal>
        </>
    );
};
