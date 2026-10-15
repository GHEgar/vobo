import { useEffect, useId, useRef, useState } from 'react';
import { Link } from 'react-router';
import { ArrowRight, Bell, User } from 'tesela/react';
import { useAvisosNoLeidos } from '@/hooks/useAvisos';

const iniciales = (nombre = '') => nombre
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0].toUpperCase())
    .join('') || '?';

const contador = (total) => (total > 99 ? '99+' : String(total));

const etiquetaCuenta = (nombre, total) => {
    if (!total) return `Cuenta de ${nombre}`;
    return `Cuenta de ${nombre}, ${total === 1 ? '1 aviso sin leer' : `${total} avisos sin leer`}`;
};

export const MenuUsuario = ({ usuario, onSalir }) => {
    const [abierto, setAbierto] = useState(false);
    const contenedor = useRef(null);
    const menuId = useId();
    const { data } = useAvisosNoLeidos();
    const total = data?.total ?? 0;

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
                aria-label={etiquetaCuenta(usuario.nombre, total)}
                className="relative flex h-[36px] w-[36px] items-center justify-center rounded-full bg-primario-claro tipo-negrita text-sm text-primario hover:ring-2 hover:ring-primario-anillo focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario"
            >
                {iniciales(usuario.nombre)}
                {total > 0 && (
                    <span aria-hidden="true" className="absolute -top-1 -right-1 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-error px-1 tipo-negrita text-[10px] text-white ring-2 ring-white">
                        {contador(total)}
                    </span>
                )}
            </button>
            {abierto && (
                <div id={menuId} role="menu" className="absolute right-0 z-40 mt-2 w-[240px] rounded-2xl bg-white p-2 shadow-[0px_3px_24px_var(--color-sombra-menu)]">
                    <div className="flex items-start gap-2 px-3 py-2">
                        <User size={18} stroke={1.75} className="mt-px shrink-0 text-primario" />
                        <div className="min-w-0">
                            <p className="tipo-negrita text-sm text-texto">{usuario.nombre}</p>
                            {usuario.email && <p className="truncate tipo-media text-xs text-texto-apagado">{usuario.email}</p>}
                        </div>
                    </div>
                    <Link
                        to="/avisos"
                        role="menuitem"
                        onClick={() => setAbierto(false)}
                        aria-label={total ? `Avisos, ${total} sin leer` : 'Avisos'}
                        className="mt-1 flex w-full items-center gap-2 rounded-xl px-3 py-2 tipo-negrita text-sm text-texto-tenue hover:bg-fondo focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario"
                    >
                        <Bell size={18} stroke={1.75} className="shrink-0 text-primario" />
                        <span className="flex-1">Avisos</span>
                        {total > 0 && (
                            <span aria-hidden="true" className="flex h-[20px] min-w-[20px] items-center justify-center rounded-full bg-error px-1.5 tipo-negrita text-[11px] text-white">
                                {contador(total)}
                            </span>
                        )}
                    </Link>
                    <button
                        type="button"
                        role="menuitem"
                        onClick={onSalir}
                        className="mt-1 flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left tipo-negrita text-sm text-texto-tenue hover:bg-fondo focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario"
                    >
                        <ArrowRight size={18} stroke={1.75} className="shrink-0 text-primario" />
                        Salir
                    </button>
                </div>
            )}
        </div>
    );
};
