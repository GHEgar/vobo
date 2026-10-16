import { useQuery } from '@tanstack/react-query';
import { fetchModo } from '@/services/validacion';

export const useModo = () => {
    const { data } = useQuery({ queryKey: ['modo'], queryFn: fetchModo, staleTime: Infinity });
    const modo = data?.modo ?? '';
    return { modo, conCuentas: modo === 'cuentas' || modo === 'ambos' };
};
