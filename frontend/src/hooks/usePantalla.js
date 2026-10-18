import { useEffect, useState, useSyncExternalStore } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchDatosPantalla, fetchPantalla } from '@/services/pantalla';
import { ALTO, ANCHO } from '@/utils/pantalla/paleta';

export const REFRESCO = 15 * 1000;
const OCULTAR_CURSOR = 3000;

const reintentar = (fallos, error) => error?.estado !== 404 && fallos < 2;

export const usePantallaConfig = (token) => useQuery({
    queryKey: ['pantalla', token, 'config'],
    queryFn: () => fetchPantalla(token),
    refetchInterval: 60 * 1000,
    refetchIntervalInBackground: true,
    staleTime: 0,
    retry: reintentar,
});

export const useDatosPantalla = (token, activa) => useQuery({
    queryKey: ['pantalla', token, 'datos'],
    queryFn: () => fetchDatosPantalla(token),
    enabled: activa,
    refetchInterval: REFRESCO,
    refetchIntervalInBackground: true,
    staleTime: 0,
    retry: reintentar,
});

const suscribirTamano = (avisar) => {
    window.addEventListener('resize', avisar);
    return () => window.removeEventListener('resize', avisar);
};

const leerEscala = () => Math.min(window.innerWidth / ANCHO, window.innerHeight / ALTO);

export const useEscala = () => useSyncExternalStore(suscribirTamano, leerEscala, () => 1);

const consultaMovimiento = '(prefers-reduced-motion: reduce)';

const suscribirMovimiento = (avisar) => {
    const consulta = window.matchMedia(consultaMovimiento);
    consulta.addEventListener('change', avisar);
    return () => consulta.removeEventListener('change', avisar);
};

export const useMovimientoReducido = () => useSyncExternalStore(
    suscribirMovimiento,
    () => window.matchMedia(consultaMovimiento).matches,
    () => false,
);

export const useCursorOculto = () => {
    const [oculto, setOculto] = useState(false);
    useEffect(() => {
        let temporizador = setTimeout(() => setOculto(true), OCULTAR_CURSOR);
        const mover = () => {
            setOculto(false);
            clearTimeout(temporizador);
            temporizador = setTimeout(() => setOculto(true), OCULTAR_CURSOR);
        };
        window.addEventListener('mousemove', mover);
        window.addEventListener('pointerdown', mover);
        return () => {
            clearTimeout(temporizador);
            window.removeEventListener('mousemove', mover);
            window.removeEventListener('pointerdown', mover);
        };
    }, []);
    return oculto;
};

export const useReloj = (cada = 1000) => {
    const [ahora, setAhora] = useState(() => new Date());
    useEffect(() => {
        const intervalo = setInterval(() => setAhora(new Date()), cada);
        return () => clearInterval(intervalo);
    }, [cada]);
    return ahora;
};

export const useRotacion = (total, segundos) => {
    const [estado, setEstado] = useState({ indice: 0, total });
    const indice = estado.total === total ? estado.indice % Math.max(total, 1) : 0;
    useEffect(() => {
        if (total <= 1) return undefined;
        const intervalo = setInterval(() => {
            setEstado((previo) => ({ indice: ((previo.total === total ? previo.indice : 0) + 1) % total, total }));
        }, segundos * 1000);
        return () => clearInterval(intervalo);
    }, [total, segundos]);
    return indice;
};
