import { useMemo } from 'react';
import { EdicionContext } from '@/contexts/EdicionContext';
import { useEstadoEditor } from '@/hooks/useEditor';
import { useSessionStorageState } from '@/hooks/useLocalStorageState';
import { useSesion } from '@/hooks/useSesion';
import { CLAVE_EDICION } from '@/utils/edicion';
import { PERMISOS } from '@/utils/permisos';

export const EdicionProvider = ({ children }) => {
    const { puede } = useSesion();
    const permitido = puede(PERMISOS.editarContenido);
    const estado = useEstadoEditor(permitido);
    const [guardado, setGuardado] = useSessionStorageState(CLAVE_EDICION, false);
    const disponible = permitido && Boolean(estado.data?.editable);
    const activo = disponible && guardado === true;
    const sistemas = estado.data?.sistemas;

    const valor = useMemo(() => ({
        disponible,
        activo,
        sistemas: sistemas ?? [],
        fijar: (encendido) => setGuardado(Boolean(encendido)),
        alternar: () => setGuardado(!activo),
    }), [disponible, activo, sistemas, setGuardado]);

    return <EdicionContext value={valor}>{children}</EdicionContext>;
};
