import { Button } from '@/components/Button';
import { MediaImagen } from '@/components/MediaImagen';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { CheckCircle, CloseCircle } from 'tesela/react';

const ENLACE = 'bg-transparent p-0 tipo-negrita text-xs text-primario hover:underline disabled:cursor-not-allowed disabled:text-texto-deshabilitado';


const varianteDe = (opcion, elegido) => {
    const propia = opcion === 'pasa' ? 'success' : 'danger';
    if (!elegido || elegido === 'comentario') return propia;
    const esta = opcion === 'pasa' ? elegido === 'pasa' : elegido === 'falla' || elegido === 'no_pude';
    return esta ? propia : 'ghost';
};

export const PasoActual = ({
    caso, indice, procedimiento, elegido, modo, onModo, onResponder,
    editable, guardando,
}) => {
    const paso = caso.pasos[indice];
    const ultimo = indice === caso.pasos.length - 1;

    return (
        <div className="flex flex-col gap-4">
            <div>
                <p className="tipo-media text-lg/7 text-texto md:text-xl/8"><TextoConEnlaces texto={paso.texto} /></p>
            </div>
            {procedimiento?.url && (
                <figure className="overflow-hidden rounded-2xl bg-fondo">
                    <MediaImagen url={procedimiento.url} alt={procedimiento.titulo || `Cómo hacer el paso ${indice + 1}`} className="max-h-[60dvh] w-full object-contain" />
                    {procedimiento.titulo && <figcaption className="px-4 py-2 tipo-media text-xs text-texto-tenue">{procedimiento.titulo}</figcaption>}
                </figure>
            )}
            {ultimo && (
                <div className="rounded-2xl border border-primario-borde px-4 py-3">
                    <p className="tipo-media text-xs text-primario">Lo que debe pasar</p>
                    <p className="mt-1 tipo-negrita text-sm/6 text-texto"><TextoConEnlaces texto={caso.esperado} /></p>
                </div>
            )}
            {['botones', 'enviado'].includes(modo) && (
                <div className="flex flex-col gap-2">
                    <div className="grid grid-cols-1 items-center gap-3 sm:grid-cols-2">
                        <Button label="Pasa" icono={<CheckCircle size={20} />} variant={varianteDe('pasa', elegido)} pressed={elegido === 'pasa'} grande onClick={() => onResponder('pasa', null)} disabled={!editable} loading={guardando} fullWidth />
                        <Button label="Falla" icono={<CloseCircle size={20} />} variant={varianteDe('falla', elegido)} pressed={elegido === 'falla' || elegido === 'no_pude'} grande onClick={() => onModo('falla')} disabled={!editable} fullWidth />
                    </div>
                    <div className="flex flex-wrap justify-center gap-x-5 gap-y-1 sm:justify-start">
                        {[['comentario', 'Comentario']].map(([clave, texto]) => (
                            <button
                                key={clave}
                                type="button"
                                onClick={() => onModo(clave)}
                                disabled={!editable}
                                className={ENLACE}
                            >
                                {texto}
                            </button>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};
