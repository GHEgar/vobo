import { useState } from 'react';
import { BotonMas } from '@/components/BotonMas';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Titulo } from '@/components/Tarjeta';
import { FilaSeccion } from '@/components/editor/FilaSeccion';
import { Historial } from '@/components/editor/Historial';
import { useDuplicarSeccion, useOrdenarSecciones, useSeccionesEditor } from '@/hooks/useEditor';
import { intercambiar } from '@/utils/editor';
import { seccionesPorSistema } from '@/utils/sistemas';
import { Layers, Undo } from 'tesela/react';

const Duplicar = ({ seccion, onListo }) => {
    const duplicar = useDuplicarSeccion();
    const [nuevo, setNuevo] = useState(`${seccion.id}-copia`);
    return (
        <form
            className="flex flex-col"
            onSubmit={(e) => {
                e.preventDefault();
                duplicar.mutate({ id: seccion.id, nuevo: nuevo.trim() }, { onSuccess: (r) => onListo(r.id) });
            }}
        >
            <p className="tipo-media text-sm text-texto-tenue">Se copian sus herramientas, galería y casos; los ids de casos y herramientas reciben el sufijo «copia».</p>
            <TextField id="duplicar-id" label="Id de la copia" required pattern="[a-z0-9][a-z0-9\-]{0,119}" value={nuevo} onChange={(e) => setNuevo(e.target.value)} />
            {duplicar.error && <p role="alert" className="mt-3 tipo-media text-xs text-error-fuerte">{duplicar.error.detalle?.[0]?.msg ?? duplicar.error.message}</p>}
            <div className="mt-6 flex justify-end">
                <Button label="Duplicar" type="submit" loading={duplicar.isPending} disabled={!nuevo.trim()} />
            </div>
        </form>
    );
};

export const ListaSecciones = ({ sistemas, onEditar, onNueva }) => {
    const secciones = useSeccionesEditor();
    const ordenar = useOrdenarSecciones();
    const [duplicando, setDuplicando] = useState(null);
    const [historial, setHistorial] = useState(null);
    const [borrada, setBorrada] = useState(null);

    if (secciones.isPending) return <Spinner />;
    if (secciones.error) return <ErrorState mensaje={secciones.error.message} onReintentar={secciones.refetch} />;
    const lista = secciones.data;
    const mover = (seccion, grupo, delta) => {
        const vecino = grupo[grupo.indexOf(seccion) + delta];
        ordenar.mutate(intercambiar(lista.map((s) => s.id), seccion.id, vecino.id));
    };

    return (
        <>
            <Titulo
                descripcion="Agrupadas por sistema y en el orden en que las ven quienes validan."
                accion={<BotonMas etiqueta="Nueva sección" ayuda="Crear una sección vacía" onClick={onNueva} />}
            >
                Secciones
            </Titulo>
            {ordenar.error && <p role="alert" className="mb-3 tipo-media text-xs text-error-fuerte">{ordenar.error.message}</p>}
            {borrada && (
                <div role="status" className="mb-3 flex flex-wrap items-center justify-between gap-2 rounded-2xl bg-pendiente-fondo px-4 py-3">
                    <p className="tipo-media text-sm text-pendiente">Se borró «{borrada.titulo}».</p>
                    <div className="flex gap-2">
                        <Button label="Restaurar" icono={<Undo size={16} />} small variant="warn" onClick={() => setHistorial(borrada)} />
                        <Button label="Cerrar" small variant="link" onClick={() => setBorrada(null)} />
                    </div>
                </div>
            )}
            {!lista.length && <EmptyState icono={Layers} titulo="Todavía no hay secciones" />}
            <div className="flex flex-col gap-5">
                {seccionesPorSistema(sistemas, lista).map((grupo) => (
                    <section key={grupo.clave} aria-labelledby={`editor-sistema-${grupo.clave}`}>
                        <h3 id={`editor-sistema-${grupo.clave}`} className="mb-2 tipo-negrita text-sm text-texto-tenue">{grupo.nombre}</h3>
                        <ul className="flex flex-col gap-2">
                            {grupo.secciones.map((s, i) => (
                                <FilaSeccion
                                    key={s.id}
                                    seccion={s}
                                    indice={i}
                                    total={grupo.secciones.length}
                                    onMover={(delta) => mover(s, grupo.secciones, delta)}
                                    onEditar={() => onEditar(s.id)}
                                    onDuplicar={() => setDuplicando(s)}
                                    onHistorial={() => setHistorial(s)}
                                    onBorrada={() => setBorrada(s)}
                                />
                            ))}
                        </ul>
                    </section>
                ))}
            </div>
            <Modal abierto={Boolean(duplicando)} titulo={`Duplicar ${duplicando?.titulo ?? ''}`} onCerrar={() => setDuplicando(null)} ancho="max-w-lg">
                {duplicando && <Duplicar seccion={duplicando} onListo={(id) => { setDuplicando(null); onEditar(id); }} />}
            </Modal>
            <Historial
                abierto={Boolean(historial)}
                tipo="seccion"
                id={historial?.id}
                titulo={historial?.titulo}
                onCerrar={() => {
                    if (historial?.id === borrada?.id) setBorrada(null);
                    setHistorial(null);
                }}
            />
        </>
    );
};
