import { Desplegable } from '@/components/Desplegable';
import { NombreProyecto } from '@/components/NombreProyecto';
import { useProyecto } from '@/hooks/useProyecto';
import { useNombreProyecto } from '@/hooks/useInstancia';

const COLOR_POR_OMISION = 'var(--color-nombre)';

export const SelectorProyecto = () => {
    const { proyectos, proyecto, elegir } = useProyecto();
    const visible = useNombreProyecto();
    if (!proyecto) return null;
    if (proyectos.length < 2) {
        return visible ? <NombreProyecto nombre={visible} color={proyecto.color_nombre} /> : null;
    }
    return (
        <Desplegable
            aria-label="Proyecto"
            value={proyecto.clave}
            onChange={elegir}
            opciones={proyectos.map((p) => ({ valor: p.clave, texto: p.nombre, color: p.color_nombre ?? COLOR_POR_OMISION }))}
            className="min-w-0 flex-1 sm:w-[240px] sm:flex-none [&_button]:pr-8 [&_button]:pl-3 [&_button]:tipo-negrita [&_button]:text-sm sm:[&_button]:pr-10 sm:[&_button]:pl-4"
        />
    );
};
