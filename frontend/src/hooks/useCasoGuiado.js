import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { useGuardarResultado } from '@/hooks/useValidacion';
import { conRespuesta, estadoDelCaso, normalizarPasos, pasoInicial, siguienteSinResponder } from '@/utils/pasos';

const PAUSA_MS = 1000;

export const useCasoGuiado = ({ caso, ronda, resultado, siguiente, pasoPedido = null }) => {
    const navigate = useNavigate();
    const guardar = useGuardarResultado();
    const total = caso.pasos.length;
    const [pasos, setPasos] = useState(() => normalizarPasos(resultado?.pasos_marcados));
    const [actual, setActual] = useState(() => pasoPedido ?? pasoInicial(pasos, total));
    const [modo, setModo] = useState('botones');
    const [terminado, setTerminado] = useState(false);

    useEffect(() => {
        if (!terminado || !siguiente) return undefined;
        const espera = setTimeout(() => navigate(`/caso/${encodeURIComponent(siguiente.id)}`), PAUSA_MS);
        return () => clearTimeout(espera);
    }, [terminado, siguiente, navigate]);

    const persistir = (estado, nuevos, comentario = null) => guardar.mutateAsync({
        casoId: caso.id,
        ronda_id: ronda.id,
        estado,
        pasos_marcados: nuevos,
        comentario,
    });

    const responder = async (estadoPaso, comentario) => {
        const estabaCompleto = pasos.length >= total;
        const nuevos = conRespuesta(pasos, { paso: actual, estado: estadoPaso, comentario });
        try {
            await persistir(estadoDelCaso(nuevos, total), nuevos);
        } catch {
            return;
        }
        setPasos(nuevos);
        setModo('botones');
        const pendiente = siguienteSinResponder(nuevos, total, actual);
        if (pendiente !== null) {
            setActual(pendiente);
        } else if (estabaCompleto && actual < total - 1) {
            setActual(actual + 1);
        } else {
            setTerminado(true);
        }
    };

    return { pasos, actual, modo, setModo, terminado, responder, guardar };
};
