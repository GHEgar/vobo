import { useId, useState } from 'react';
import { FileArchive } from 'tesela/react';
import { Button } from '@/components/Button';
import { Titulo } from '@/components/Tarjeta';
import { ResumenErrores } from '@/components/editor/ResumenErrores';
import { useImportarPaquete } from '@/hooks/useEditor';
import { urlExportar } from '@/services/editor';
import { useProyecto } from '@/hooks/useProyecto';

const ENLACE = 'inline-flex h-[40px] items-center justify-center gap-2 rounded-full px-6 tipo-negrita text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario focus-visible:ring-offset-2';

const GRUPOS = [
    ['secciones', 'Secciones'],
    ['procedimientos', 'Procedimientos'],
    ['media', 'Animaciones'],
];

export const Exportar = () => {
    const { proyecto } = useProyecto();
    const nombre = proyecto?.por_omision ? 'contenido.zip' : `contenido-${proyecto?.clave}.zip`;
    return (
        <a href={urlExportar(proyecto?.clave)} download={nombre} className={`${ENLACE} border border-primario text-primario hover:bg-primario-suave`}>
            <FileArchive size={18} /> Exportar YAML (.zip)
        </a>
    );
};

const Plan = ({ resumen }) => (
    <dl className="mt-3 grid gap-3 sm:grid-cols-3">
        {GRUPOS.map(([clave, nombre]) => {
            const cambios = resumen[clave];
            return (
                <div key={clave} className="rounded-2xl bg-fondo p-3">
                    <dt className="tipo-negrita text-sm text-texto">{nombre}</dt>
                    <dd className="mt-1 tipo-media text-xs text-texto-tenue">
                        {cambios.crear.length} nuevas · {cambios.actualizar.length} cambian · {cambios.borrar.length} se quitan
                        {cambios.borrar.length > 0 && <span className="block text-error-fuerte">Se quitan: {cambios.borrar.join(', ')}</span>}
                    </dd>
                </div>
            );
        })}
    </dl>
);

export const Paquete = () => {
    const id = useId();
    const importar = useImportarPaquete();
    const [archivo, setArchivo] = useState(null);
    const [resumen, setResumen] = useState(null);
    const [confirmando, setConfirmando] = useState(false);

    const analizar = (elegido) => {
        setArchivo(elegido);
        setResumen(null);
        setConfirmando(false);
        if (elegido) importar.mutate({ archivo: elegido, confirmar: false }, { onSuccess: setResumen });
    };

    return (
        <>
            <Titulo descripcion="El .zip tiene la misma estructura que la carpeta de contenido: secciones/*.yaml, procedimientos.yaml y media/.">
                Importar y exportar
            </Titulo>
            <Exportar />
            <section className="mt-8">
                <h3 className="tipo-negrita text-sm text-texto">Importar YAML</h3>
                <p className="mt-1 tipo-media text-xs text-texto-tenue">Reemplaza todo el contenido por el del .zip. Antes de aplicar se muestra qué cambia; cada cambio queda en el historial.</p>
                <label htmlFor={id} className={`${ENLACE} mt-3 cursor-pointer bg-borde text-texto-tenue hover:bg-gris-hover`}>
                    <FileArchive size={18} /> {archivo ? archivo.name : 'Elegir .zip'}
                </label>
                <input id={id} type="file" accept=".zip,application/zip" className="sr-only" onChange={(e) => { analizar(e.target.files?.[0] ?? null); e.target.value = ''; }} />
                {importar.isPending && <p role="status" className="mt-3 tipo-media text-xs text-texto-tenue">Revisando el paquete…</p>}
                <ResumenErrores error={importar.error} />
                {resumen && (
                    <div className="mt-4">
                        {resumen.aplicado && <p role="status" className="tipo-negrita text-sm text-pasa">Contenido importado.</p>}
                        {resumen.sin_cambios && <p role="status" className="tipo-media text-sm text-texto-tenue">El paquete es igual al contenido actual; no hay nada que importar.</p>}
                        {!resumen.sin_cambios && <Plan resumen={resumen} />}
                        {resumen.bloqueos.length > 0 && (
                            <ul role="alert" className="mt-3 flex list-disc flex-col gap-1 rounded-2xl bg-falla-fondo py-3 pr-3 pl-8">
                                {resumen.bloqueos.map((b) => <li key={b} className="tipo-media text-xs text-falla">{b}</li>)}
                            </ul>
                        )}
                        {resumen.ignorados.length > 0 && <p className="mt-2 tipo-media text-xs text-texto-apagado">Se ignoran: {resumen.ignorados.join(', ')}</p>}
                        {!resumen.aplicado && !resumen.sin_cambios && !resumen.bloqueos.length && (
                            <div className="mt-4 flex flex-wrap justify-end gap-2">
                                {!confirmando && <Button label="Reemplazar el contenido" variant="warn" onClick={() => setConfirmando(true)} />}
                                {confirmando && (
                                    <>
                                        <Button label="Cancelar" variant="link" onClick={() => setConfirmando(false)} />
                                        <Button label="Sí, reemplazar todo" variant="danger" loading={importar.isPending} onClick={() => importar.mutate({ archivo, confirmar: true }, { onSuccess: setResumen })} />
                                    </>
                                )}
                            </div>
                        )}
                    </div>
                )}
            </section>
        </>
    );
};
