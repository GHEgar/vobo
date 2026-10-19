import { Chip } from '@/components/Chip';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { Titulo } from '@/components/Tarjeta';
import { Identidad } from '@/components/admin/configuracion/Identidad';
import { Marca } from '@/components/admin/configuracion/Marca';
import { Colores } from '@/components/admin/configuracion/Colores';
import { Cuentas, Sistemas } from '@/components/admin/configuracion/Listas';
import { EstadoGuardado } from '@/components/admin/configuracion/Comun';
import { useConfiguracion } from '@/hooks/useAdmin';
import { useLocalStorageState } from '@/hooks/useLocalStorageState';
import { useSesion } from '@/hooks/useSesion';
import { PERMISOS } from '@/utils/permisos';

const PARTES = [
    { clave: 'identidad', nombre: 'Identidad', permiso: PERMISOS.editarIdentidad, Componente: Identidad, firma: (e) => [e.efectiva.producto, e.efectiva.nombre, e.efectiva.descripcion, e.efectiva.entrada] },
    { clave: 'marca', nombre: 'Marca', permiso: PERMISOS.editarIdentidad, Componente: Marca, firma: () => [] },
    { clave: 'colores', nombre: 'Colores', permiso: PERMISOS.editarIdentidad, Componente: Colores, firma: (e) => [e.colores, e.fuente] },
    { clave: 'sistemas', nombre: 'Sistemas', permiso: PERMISOS.editarConfiguracion, Componente: Sistemas, firma: (e) => [e.efectiva.proyectos] },
    { clave: 'cuentas', nombre: 'Cuentas de prueba', permiso: PERMISOS.editarConfiguracion, Componente: Cuentas, firma: (e) => [e.guardada.cuentas ?? e.archivos.cuentas] },
];

export const Configuracion = () => {
    const configuracion = useConfiguracion();
    const { puede } = useSesion();
    const partes = PARTES.filter((p) => puede(p.permiso));
    const [elegida, setElegida] = useLocalStorageState('validacion.admin.configuracion', 'identidad');
    const parte = partes.find((p) => p.clave === elegida) ?? partes[0];

    if (configuracion.isPending) return <Spinner />;
    if (configuracion.error) return <ErrorState mensaje={configuracion.error.message} onReintentar={configuracion.refetch} />;
    const { Componente } = parte;

    return (
        <>
            <Titulo accion={<EstadoGuardado />} descripcion="Lo que guardes aquí gana sobre los archivos de la instalación. Restablecer vuelve al valor de los archivos o al de la app.">
                Configuración
            </Titulo>
            <div role="group" aria-label="Partes de la configuración" className="mb-5 flex flex-wrap gap-2">
                {partes.map((p) => (
                    <Chip key={p.clave} tono={p.clave === parte.clave ? 'marca' : 'neutro'} activo={p.clave === parte.clave} onClick={() => setElegida(p.clave)}>
                        {p.nombre}
                    </Chip>
                ))}
            </div>
            <Componente key={JSON.stringify(parte.firma(configuracion.data))} estado={configuracion.data} />
        </>
    );
};
