import { useState } from 'react';
import { Button } from '@/components/Button';
import { Dragger } from '@/components/Dragger';
import { MediaImagen } from '@/components/MediaImagen';
import { useQuitarAnimacion, useSubirAnimacion } from '@/hooks/useEditor';
import { tamanoLegible } from '@/utils/editor';

const TIPOS = ['image/webp', 'image/gif', 'image/png', 'image/jpeg', 'video/mp4', 'video/webm'];

export const SubirAnimacion = ({ procedimiento }) => {
    const subir = useSubirAnimacion();
    const quitar = useQuitarAnimacion();
    const [archivos, setArchivos] = useState([]);
    const media = procedimiento.media;
    const error = subir.error ?? quitar.error;

    return (
        <section className="mt-6">
            <h3 className="tipo-negrita text-sm text-texto">Animación</h3>
            {media ? (
                <figure className="mt-3 flex flex-col gap-2 rounded-2xl bg-fondo p-3">
                    <MediaImagen url={media.url} alt={procedimiento.datos.titulo || procedimiento.id} tipo={media.mime} carga="eager" className="max-h-[320px] w-full rounded-xl bg-white object-contain" />
                    <figcaption className="flex flex-wrap items-center justify-between gap-2 tipo-media text-xs text-texto-tenue">
                        <span>{media.archivo} · {tamanoLegible(media.tamano)} · {media.autor_email}</span>
                        <Button label="Quitar animación" small variant="enlaceRojo" loading={quitar.isPending} onClick={() => quitar.mutate(procedimiento.id)} />
                    </figcaption>
                </figure>
            ) : (
                <p className="mt-1 tipo-media text-xs text-texto-apagado">Este procedimiento todavía no tiene animación.</p>
            )}
            <Dragger
                label={media ? 'Reemplazar animación' : 'Subir animación'}
                archivos={archivos}
                onChange={setArchivos}
                maxMB={20}
                maxArchivos={1}
                tipos={TIPOS}
                titulo={media ? 'Reemplaza la animación' : 'Sube la animación'}
                ayuda="WebP, GIF, PNG, JPEG, MP4 o WebM, hasta {maxMB} MB. Se guarda con el id del procedimiento."
                sustantivo="animaciones"
            />
            {error && <p role="alert" className="mt-2 tipo-media text-xs text-error-fuerte">{error.message}</p>}
            {archivos.length > 0 && (
                <div className="mt-3 flex justify-end">
                    <Button
                        label={media ? 'Reemplazar' : 'Subir'}
                        loading={subir.isPending}
                        onClick={() => subir.mutate({ id: procedimiento.id, archivo: archivos[0] }, { onSuccess: () => setArchivos([]) })}
                    />
                </div>
            )}
        </section>
    );
};
