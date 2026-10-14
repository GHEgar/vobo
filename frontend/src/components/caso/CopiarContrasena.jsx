import { BotonCopiar } from '@/components/BotonCopiar';
import { useRonda } from '@/hooks/useRonda';
import { useCuentasPrueba } from '@/hooks/useValidacion';
import { localDeCuenta } from '@/utils/cuentas';

export const CopiarContrasena = ({ cuenta }) => {
    const { ronda } = useRonda();
    const { data } = useCuentasPrueba(ronda?.id);
    const texto = (cuenta ?? '').toLowerCase();
    const encontrada = texto && data?.find((c) => texto.includes(localDeCuenta(c.email)));
    if (!encontrada) return null;
    return (
        <span className="ml-3 inline-flex">
            <BotonCopiar texto={encontrada.password} etiqueta="Copiar contraseña" descripcion={`Copiar la contraseña de ${encontrada.email}`} />
        </span>
    );
};
