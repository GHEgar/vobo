import { useEffect, useEffectEvent } from 'react';

const EDITABLES = 'input, textarea, select, [contenteditable]:not([contenteditable="false"])';

export const useAtajoBuscar = (enfocar) => {
    const alPulsar = useEffectEvent(enfocar);

    useEffect(() => {
        const tecla = (e) => {
            const combinacion = (e.ctrlKey || e.metaKey) && !e.altKey && e.key.toLowerCase() === 'k';
            const barra = e.key === '/' && !e.ctrlKey && !e.metaKey && !e.altKey
                && !(e.target instanceof Element && e.target.closest(EDITABLES));
            if (!combinacion && !barra) return;
            e.preventDefault();
            alPulsar();
        };
        document.addEventListener('keydown', tecla);
        return () => document.removeEventListener('keydown', tecla);
    }, []);
};
