import { useEffect, useEffectEvent } from 'react';

const EDITABLES = 'input, textarea, select, [contenteditable]:not([contenteditable="false"])';

export const useAtajoBuscar = (enfocar) => {
    const alPulsar = useEffectEvent(enfocar);

    useEffect(() => {
        const tecla = (e) => {
            const combinacion = (e.ctrlKey || e.metaKey) && !e.altKey && e.key.toLowerCase() === 'k';
            const enie = (e.key === 'ñ' || e.key === 'Ñ') && !e.ctrlKey && !e.metaKey && !e.altKey
                && !(e.target instanceof Element && e.target.closest(EDITABLES));
            if (!combinacion && !enie) return;
            e.preventDefault();
            alPulsar();
        };
        document.addEventListener('keydown', tecla);
        return () => document.removeEventListener('keydown', tecla);
    }, []);
};
