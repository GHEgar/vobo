import { useCallback, useState } from 'react';

const leer = (almacen, clave, inicial) => {
    try {
        const guardado = window[almacen].getItem(clave);
        return guardado === null ? inicial : JSON.parse(guardado);
    } catch {
        return inicial;
    }
};

const useAlmacenado = (almacen, clave, inicial) => {
    const [valor, setValor] = useState(() => leer(almacen, clave, inicial));
    const guardar = useCallback((nuevo) => {
        setValor(nuevo);
        try {
            window[almacen].setItem(clave, JSON.stringify(nuevo));
        } catch {
            return;
        }
    }, [almacen, clave]);
    return [valor, guardar];
};

export const useLocalStorageState = (clave, inicial) => useAlmacenado('localStorage', clave, inicial);

export const useSessionStorageState = (clave, inicial) => useAlmacenado('sessionStorage', clave, inicial);
