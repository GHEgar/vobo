import { useContext, useEffect, useMemo, useState } from 'react';
import { useLocation } from 'react-router';
import { PresenciaContext } from '@/contexts/PresenciaContext';
import { useRonda } from '@/hooks/useRonda';
import { useSesion } from '@/hooks/useSesion';
import { useClaveProyecto } from '@/hooks/useProyecto';
import { registrarPresencia } from '@/services/validacion';

const INTERVALO_MS = 30 * 1000;
const LARGO_RUTA = 300;

const pasoDeConsulta = (search) => {
    const numero = Number(new URLSearchParams(search).get('paso'));
    return Number.isInteger(numero) && numero >= 1 ? numero : null;
};

const segmento = (pathname, prefijo) => {
    const coincide = pathname.match(new RegExp(`^/${prefijo}/([^/]+)`));
    if (!coincide) return null;
    try {
        return decodeURIComponent(coincide[1]);
    } catch {
        return null;
    }
};

const pantalla = () => `${Math.round(window.innerWidth)}x${Math.round(window.innerHeight)}`;

const construir = ({ pathname, search }, rondaId, proyecto, detalle) => {
    const casoId = segmento(pathname, 'caso');
    const propio = detalle && detalle.casoId === casoId ? detalle : null;
    return {
        ruta: `${pathname}${search}`.slice(0, LARGO_RUTA),
        caso_id: casoId?.slice(0, 60) ?? null,
        paso: casoId ? (propio ? propio.paso : pasoDeConsulta(search)) : null,
        seccion_id: segmento(pathname, 'seccion')?.slice(0, 120) ?? null,
        accion: propio?.accion ?? 'viendo',
        ronda_id: rondaId ?? null,
        proyecto,
    };
};

export const usePresencia = () => {
    const ubicacion = useLocation();
    const { ronda } = useRonda();
    const { csrf } = useSesion();
    const proyecto = useClaveProyecto();
    const [detalle, setDetalle] = useState(null);
    const datos = useMemo(
        () => construir(ubicacion, ronda?.id, proyecto, detalle),
        [ubicacion, ronda?.id, proyecto, detalle],
    );
    const clave = JSON.stringify(datos);

    useEffect(() => {
        if (!csrf) return undefined;
        const cuerpo = JSON.parse(clave);
        const enviar = () => {
            if (document.visibilityState === 'visible') registrarPresencia({ ...cuerpo, pantalla: pantalla() }).catch(() => {});
        };
        enviar();
        const intervalo = setInterval(enviar, INTERVALO_MS);
        document.addEventListener('visibilitychange', enviar);
        return () => {
            clearInterval(intervalo);
            document.removeEventListener('visibilitychange', enviar);
        };
    }, [clave, csrf]);

    return setDetalle;
};

export const useInformarPresencia = ({ casoId, paso, accion }) => {
    const informar = useContext(PresenciaContext);
    useEffect(() => {
        if (!informar) return undefined;
        informar({ casoId, paso, accion });
        return () => informar(null);
    }, [informar, casoId, paso, accion]);
};
