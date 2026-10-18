import { useState } from 'react';
import { Button } from '@/components/Button';
import { BotonMas } from '@/components/BotonMas';
import { Chip } from '@/components/Chip';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Titulo } from '@/components/Tarjeta';
import { EnlaceGenerado } from '@/components/admin/EnlaceGenerado';
import { EditorPantalla } from '@/components/admin/EditorPantalla';
import { useActualizarPantalla, useBorrarPantalla, useCrearPantalla, usePantallas, useRegenerarPantalla } from '@/hooks/useAdmin';
import { formatearRelativa } from '@/utils/formato';
import { NOMBRES_VISTA } from '@/utils/pantalla/formato';

const AVISO = 'Guárdalo ahora: por seguridad no se vuelve a mostrar. Si se pierde, regenera el enlace.';

const Enlace = ({ enlace }) => (
    <EnlaceGenerado
        enlace={enlace}
        descripcion="Abre este enlace en el navegador del televisor, en pantalla completa. Funciona sin iniciar sesión y muestra solo el nombre de pila de cada persona."
        nota={AVISO}
    >
        <a href={enlace} target="_blank" rel="noopener noreferrer" className="tipo-negrita text-xs text-primario underline underline-offset-4 hover:text-primario-hover">
            Abrir
        </a>
    </EnlaceGenerado>
);

const Acciones = ({ pantalla, onEditar, onEnlace }) => {
    const actualizar = useActualizarPantalla();
    const regenerar = useRegenerarPantalla();
    const borrar = useBorrarPantalla();
    const [confirmando, setConfirmando] = useState(false);
    const error = actualizar.error ?? regenerar.error ?? borrar.error;
    return (
        <div className="flex min-w-0 flex-col items-start gap-2 lg:items-end">
            <div className="flex flex-wrap items-center gap-2">
                <Button label="Editar" small variant="ghost" onClick={onEditar} />
                <Button label={pantalla.activa ? 'Desactivar' : 'Activar'} small variant="ghost" loading={actualizar.isPending} onClick={() => actualizar.mutate({ id: pantalla.id, activa: !pantalla.activa })} />
                <Button label="Regenerar enlace" small variant="ghost" loading={regenerar.isPending} onClick={() => regenerar.mutate(pantalla.id, { onSuccess: (r) => onEnlace(r) })} />
                {!confirmando && <Button label="Borrar" small variant="enlaceRojo" onClick={() => setConfirmando(true)} />}
                {confirmando && (
                    <>
                        <Button label="Borrar la pantalla" small variant="danger" loading={borrar.isPending} onClick={() => borrar.mutate(pantalla.id)} />
                        <Button label="Cancelar" small variant="link" onClick={() => setConfirmando(false)} />
                    </>
                )}
            </div>
            {error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{error.message}</p>}
        </div>
    );
};

const FilaPantalla = ({ pantalla, nombres, onEditar, onEnlace }) => (
    <li className="flex flex-col gap-3 rounded-2xl bg-fondo px-4 py-3 lg:flex-row lg:items-start lg:justify-between">
        <div className="flex min-w-0 flex-1 flex-col gap-2">
            <span className="tipo-negrita text-sm text-texto">{pantalla.nombre}</span>
            <div className="flex flex-wrap gap-2">
                <Chip tono={pantalla.activa ? 'exito' : 'aviso'}>{pantalla.activa ? 'Activa' : 'Desactivada'}</Chip>
                <Chip>{pantalla.vistas.map((v) => NOMBRES_VISTA[v].split(':')[0]).join(' → ')}</Chip>
                <Chip>{pantalla.segundos} s por vista</Chip>
                <Chip>{pantalla.proyectos.length ? pantalla.proyectos.map((c) => nombres[c] ?? c).join(', ') : 'Todos los proyectos activos'}</Chip>
            </div>
            <p className="tipo-media text-[11px] text-texto-apagado">
                {pantalla.ultimo_uso ? `Se vio ${formatearRelativa(pantalla.ultimo_uso)}` : 'Aún no se ha abierto'}
            </p>
        </div>
        <Acciones pantalla={pantalla} onEditar={onEditar} onEnlace={onEnlace} />
    </li>
);

const Edicion = ({ editando, onListo, onEnlace }) => {
    const crear = useCrearPantalla();
    const actualizar = useActualizarPantalla();
    const pantalla = editando.pantalla;
    const guardar = pantalla ? actualizar : crear;
    const onGuardar = (datos) => {
        if (pantalla) actualizar.mutate({ id: pantalla.id, ...datos }, { onSuccess: onListo });
        else crear.mutate(datos, { onSuccess: onEnlace });
    };
    return <EditorPantalla pantalla={pantalla} guardar={guardar} onGuardar={onGuardar} />;
};

export const Pantallas = ({ proyectos = [] }) => {
    const estado = usePantallas();
    const [editando, setEditando] = useState(null);
    const [generado, setGenerado] = useState(null);
    const nombres = Object.fromEntries(proyectos.map((p) => [p.clave, p.nombre]));
    const mostrarEnlace = (respuesta) => {
        setEditando(null);
        setGenerado(respuesta);
    };

    if (estado.isPending) return <Spinner />;
    if (estado.error) return <ErrorState mensaje={estado.error.message} onReintentar={estado.refetch} />;

    return (
        <>
            <Titulo
                descripcion="Enlaces para televisores: muestran el avance en vivo sin iniciar sesión. Solo enseñan el nombre de pila de cada persona; desactiva o regenera el enlace para revocarlo."
                accion={<BotonMas etiqueta="Nueva pantalla" ayuda="Crear un enlace de pantalla para un televisor" onClick={() => setEditando({ pantalla: null })} />}
            >
                Pantallas
            </Titulo>
            {estado.data.length === 0 && <p className="rounded-2xl bg-fondo px-4 py-3 tipo-media text-sm text-texto-tenue">Aún no hay pantallas.</p>}
            <ul className="flex flex-col gap-2">
                {estado.data.map((p) => (
                    <FilaPantalla key={p.id} pantalla={p} nombres={nombres} onEditar={() => setEditando({ pantalla: p })} onEnlace={setGenerado} />
                ))}
            </ul>
            <Modal abierto={Boolean(editando)} titulo={editando?.pantalla ? `Editar ${editando.pantalla.nombre}` : 'Nueva pantalla'} onCerrar={() => setEditando(null)} ancho="max-w-lg">
                {editando && <Edicion key={editando.pantalla?.id ?? 'nueva'} editando={editando} onListo={() => setEditando(null)} onEnlace={mostrarEnlace} />}
            </Modal>
            <Modal abierto={Boolean(generado)} titulo={generado ? `Enlace de ${generado.pantalla.nombre}` : ''} onCerrar={() => setGenerado(null)} ancho="max-w-lg">
                {generado && <Enlace enlace={generado.enlace} />}
            </Modal>
        </>
    );
};
