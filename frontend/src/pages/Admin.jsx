import { PestanasVerticales } from '@/components/PestanasVerticales';
import { useSesion } from '@/hooks/useSesion';
import { PERMISOS } from '@/utils/permisos';
import { Personas } from '@/components/admin/Personas';
import { Roles } from '@/components/admin/Roles';
import { Configuracion } from '@/components/admin/Configuracion';
import { Proyectos } from '@/components/admin/Proyectos';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { Folder, Lock, Settings, User } from 'tesela/react';

const PESTANAS = [
    { clave: 'personas', nombre: 'Personas', icono: User, permisos: [PERMISOS.gestionarPersonas, PERMISOS.gestionarRoles] },
    { clave: 'roles', nombre: 'Roles', icono: Lock, permisos: [PERMISOS.gestionarRoles] },
    { clave: 'proyectos', nombre: 'Proyectos', icono: Folder, permisos: [PERMISOS.gestionarProyectos] },
    { clave: 'configuracion', nombre: 'Configuración', icono: Settings, permisos: [PERMISOS.editarIdentidad, PERMISOS.editarConfiguracion] },
];

const Contenido = ({ clave }) => {
    if (clave === 'roles') return <Roles />;
    if (clave === 'proyectos') return <Proyectos />;
    if (clave === 'configuracion') return <Configuracion />;
    return <Personas />;
};

const Admin = () => {
    const { puede } = useSesion();
    const pestanas = PESTANAS.filter((p) => p.permisos.some(puede));
    const [guardada, setPestana] = useLocalStorageState('validacion.admin.pestana', 'personas');
    const pestana = pestanas.some((p) => p.clave === guardada) ? guardada : pestanas[0]?.clave;
    return (
        <PestanasVerticales id="admin" titulo="Administración" etiqueta="Secciones de administración" pestanas={pestanas} elegida={pestana} onElegir={setPestana}>
            {(activa) => <Contenido clave={activa.clave} />}
        </PestanasVerticales>
    );
};

export default Admin;
