import { useState } from 'react';
import { useSearchParams } from 'react-router';
import { PestanasVerticales } from '@/components/PestanasVerticales';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { FormSeccion } from '@/components/editor/FormSeccion';
import { ListaSecciones } from '@/components/editor/ListaSecciones';
import { Exportar, Paquete } from '@/components/editor/Paquete';
import { Procedimientos } from '@/components/editor/Procedimientos';
import { useEstadoEditor } from '@/hooks/useEditor';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { Layers, Play, Swap } from 'tesela/react';

const PESTANAS = [
    { clave: 'secciones', nombre: 'Secciones', icono: Layers },
    { clave: 'procedimientos', nombre: 'Procedimientos', icono: Play },
    { clave: 'paquete', nombre: 'Importar y exportar', icono: Swap },
];

const PorArchivos = () => (
    <Tarjeta>
        <Titulo descripcion="Esta instancia lee su contenido de archivos YAML (CONTENIDO_FUENTE=archivos). Para editarlo aquí, configura CONTENIDO_FUENTE=base: el contenido actual se importa la primera vez que arranca.">
            El contenido se gestiona por archivos
        </Titulo>
        <Exportar />
    </Tarjeta>
);

const Secciones = ({ sistemas }) => {
    const [params] = useSearchParams();
    const pedida = params.get('seccion');
    const [editando, setEditando] = useState(pedida ? { id: pedida } : null);
    if (editando) {
        return (
            <FormSeccion
                key={editando.id ?? 'nueva'}
                seccionId={editando.id}
                sistemas={sistemas}
                onGuardada={(id) => setEditando({ id })}
                onVolver={() => setEditando(null)}
            />
        );
    }
    return <ListaSecciones sistemas={sistemas} onEditar={(id) => setEditando({ id })} onNueva={() => setEditando({ id: null })} />;
};

const Editor = () => {
    const estado = useEstadoEditor();
    const [params] = useSearchParams();
    const [guardada, setPestana] = useLocalStorageState('validacion.editor.pestana', 'secciones');
    const [forzada, setForzada] = useState(Boolean(params.get('seccion')));
    const pestana = forzada ? 'secciones' : guardada;
    const elegir = (clave) => {
        setForzada(false);
        setPestana(clave);
    };

    if (estado.isPending) return <Spinner />;
    if (estado.error) return <ErrorState mensaje={estado.error.message} onReintentar={estado.refetch} />;
    if (!estado.data.editable) return <PorArchivos />;

    return (
        <div className="flex flex-col gap-4">
            {estado.data.errores.length > 0 && (
                <ul role="alert" className="flex list-disc flex-col gap-1 rounded-2xl bg-falla-fondo py-3 pr-4 pl-8">
                    {estado.data.errores.map((e) => <li key={e} className="tipo-media text-xs text-falla">{e}</li>)}
                </ul>
            )}
            <PestanasVerticales id="editor" titulo={`Editor de contenido · ${estado.data.proyecto.nombre}`} etiqueta="Partes del contenido" pestanas={PESTANAS} elegida={pestana} onElegir={elegir}>
                {(activa) => {
                    if (activa.clave === 'procedimientos') return <Procedimientos />;
                    if (activa.clave === 'paquete') return <Paquete />;
                    return <Secciones sistemas={estado.data.sistemas} />;
                }}
            </PestanasVerticales>
        </div>
    );
};

export default Editor;
