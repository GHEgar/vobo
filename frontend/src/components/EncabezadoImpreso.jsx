import { Marca } from '@/components/Marca';
import { useNombreProyecto } from '@/hooks/useInstancia';
import { tituloDocumento } from '@/utils/marca';

export const EncabezadoImpreso = ({ titulo, nombre: propio, children }) => {
    const actual = useNombreProyecto();
    const nombre = propio ?? actual;
    return (
        <header>
            <div className="mb-4 flex items-center">
                <Marca variante="impresion" />
            </div>
            <h1 className="tipo-negrita text-2xl">{tituloDocumento(titulo, nombre)}</h1>
            {children}
        </header>
    );
};
