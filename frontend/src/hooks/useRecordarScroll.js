import { useEffect, useLayoutEffect, useRef } from 'react';
import { useLocation, useNavigationType } from 'react-router';

const PREFIJO = 'validacion.scroll.';

const leer = (clave) => {
    try {
        return Number(window.sessionStorage.getItem(PREFIJO + clave)) || 0;
    } catch {
        return 0;
    }
};

const guardar = (clave, y) => {
    try {
        window.sessionStorage.setItem(PREFIJO + clave, String(Math.round(y)));
    } catch {
        return;
    }
};

export const useRecordarScroll = (clave, listo) => {
    const restaurado = useRef(false);

    useEffect(() => {
        if (!listo) return undefined;
        let marco = 0;
        if (!restaurado.current) {
            const y = leer(clave);
            marco = requestAnimationFrame(() => {
                if (y > 0) window.scrollTo({ top: y, behavior: 'instant' });
                restaurado.current = true;
            });
        }
        const registrar = () => {
            if (restaurado.current) guardar(clave, window.scrollY);
        };
        window.addEventListener('scroll', registrar, { passive: true });
        window.addEventListener('pagehide', registrar);
        return () => {
            cancelAnimationFrame(marco);
            window.removeEventListener('scroll', registrar);
            window.removeEventListener('pagehide', registrar);
        };
    }, [clave, listo]);
};

export const useScrollArribaAlNavegar = () => {
    const { pathname } = useLocation();
    const tipo = useNavigationType();
    const anterior = useRef(pathname);

    useLayoutEffect(() => {
        if (anterior.current === pathname) return;
        anterior.current = pathname;
        if (tipo !== 'POP') window.scrollTo({ top: 0, behavior: 'instant' });
    }, [pathname, tipo]);
};
