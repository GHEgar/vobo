import { PestanasVerticales } from '@/components/PestanasVerticales';
import { Personas } from '@/components/admin/Personas';
import { Roles } from '@/components/admin/Roles';
import { Configuracion } from '@/components/admin/Configuracion';
import { Proyectos } from '@/components/admin/Proyectos';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { Folder, Lock, Settings, User } from 'tesela/react';

const PESTANAS = [
    { clave: 'personas', nombre: 'Personas', icono: User },
    { clave: 'roles', nombre: 'Roles', icono: Lock },
    { clave: 'proyectos', nombre: 'Proyectos', icono: Folder },
    { clave: 'configuracion', nombre: 'Configuración', icono: Settings },
];

const Contenido = ({ clave }) => {
    if (clave === 'roles') return <Roles />;
    if (clave === 'proyectos') return <Proyectos />;
    if (clave === 'configuracion') return <Configuracion />;
    return <Personas />;
};

const Admin = () => {
    const [pestana, setPestana] = useLocalStorageState('validacion.admin.pestana', 'personas');
    return (
        <PestanasVerticales id="admin" titulo="Administración" etiqueta="Secciones de administración" pestanas={PESTANAS} elegida={pestana} onElegir={setPestana}>
            {(activa) => <Contenido clave={activa.clave} />}
        </PestanasVerticales>
    );
};

export default Admin;
