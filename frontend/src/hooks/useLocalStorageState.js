import { useCallback, useState } from 'react';

const leer = (clave, inicial) => {
    try {
        const guardado = window.localStorage.getItem(clave);
        return guardado === null ? inicial : JSON.parse(guardado);
    } catch {
        return inicial;
    }
};

export const useLocalStorageState = (clave, inicial) => {
    const [valor, setValor] = useState(() => leer(clave, inicial));
    const guardar = useCallback((nuevo) => {
        setValor(nuevo);
        try {
            window.localStorage.setItem(clave, JSON.stringify(nuevo));
        } catch {
            return;
        }
    }, [clave]);
    return [valor, guardar];
};
