import { Marca } from '@/components/Marca';
import { useInstancia } from '@/hooks/useInstancia';
import { tituloDocumento } from '@/utils/marca';

export const EncabezadoImpreso = ({ titulo, children }) => {
    const { nombre, proyecto } = useInstancia();
    return (
        <header>
            <div className="mb-4 flex items-center">
                <Marca variante="impresion" />
            </div>
            <h1 className="tipo-negrita text-2xl">{tituloDocumento(titulo, proyecto?.nombre || nombre)}</h1>
            {children}
        </header>
    );
};
