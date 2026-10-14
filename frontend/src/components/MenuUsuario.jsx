import { useEffect, useId, useRef, useState } from 'react';

const iniciales = (nombre = '') => nombre
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('') || '?';

export const MenuUsuario = ({ usuario, onSalir }) => {
    const [abierto, setAbierto] = useState(false);
    const contenedor = useRef(null);
    const menuId = useId();

    useEffect(() => {
        if (!abierto) return undefined;
        const fuera = (e) => {
            if (!contenedor.current?.contains(e.target)) setAbierto(false);
        };
        const tecla = (e) => {
            if (e.key === 'Escape') setAbierto(false);
        };
        document.addEventListener('mousedown', fuera);
        document.addEventListener('keydown', tecla);
        return () => {
            document.removeEventListener('mousedown', fuera);
            document.removeEventListener('keydown', tecla);
        };
    }, [abierto]);

    return (
        <div ref={contenedor} className="relative">
            <button
                type="button"
                onClick={() => setAbierto(!abierto)}
                aria-haspopup="menu"
                aria-expanded={abierto}
                aria-controls={menuId}
                aria-label={`Cuenta de ${usuario.nombre}`}
                className="flex h-[36px] w-[36px] items-center justify-center rounded-full bg-primario-claro tipo-negrita text-sm text-primario hover:ring-2 hover:ring-primario-anillo focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario"
            >
                {iniciales(usuario.nombre)}
            </button>
            {abierto && (
                <div id={menuId} role="menu" className="absolute right-0 z-40 mt-2 w-[240px] rounded-2xl bg-white p-2 shadow-[0px_3px_24px_var(--color-sombra-menu)]">
                    <div className="px-3 py-2">
                        <p className="tipo-negrita text-sm text-texto">{usuario.nombre}</p>
                        {usuario.email && <p className="truncate tipo-media text-xs text-texto-apagado">{usuario.email}</p>}
                    </div>
                    <button
                        type="button"
                        role="menuitem"
                        onClick={onSalir}
                        className="mt-1 w-full rounded-xl px-3 py-2 text-left tipo-negrita text-sm text-texto-tenue hover:bg-fondo"
                    >
                        Salir
                    </button>
                </div>
            )}
        </div>
    );
};
