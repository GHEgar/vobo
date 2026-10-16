import { useEffect, useId, useRef, useState } from 'react';
import { Link } from 'react-router';
import { Bell, Edit, Lock, Logout, Refresh, Settings, User } from 'tesela/react';
import { Modal } from '@/components/Modal';
import { CambiarContrasena } from '@/components/cuentas/CambiarContrasena';
import { PildoraEdicion } from '@/components/edicion/PildoraEdicion';
import { useAvisosNoLeidos } from '@/hooks/useAvisos';
import { useEdicion } from '@/hooks/useEdicion';
import { useSesion } from '@/hooks/useSesion';
import { iniciales } from '@/utils/formato';

const ITEM = 'mt-1 flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left tipo-negrita text-sm text-texto-tenue hover:bg-fondo focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario';

const contador = (total) => (total > 99 ? '99+' : String(total));

const etiquetaCuenta = (nombre, total) => {
    if (!total) return `Cuenta de ${nombre}`;
    return `Cuenta de ${nombre}, ${total === 1 ? '1 aviso sin leer' : `${total} avisos sin leer`}`;
};

export const MenuUsuario = ({ usuario, onSalir }) => {
    const [abierto, setAbierto] = useState(false);
    const [cambiando, setCambiando] = useState(Boolean(usuario.debe_cambiar));
    const contenedor = useRef(null);
    const menuId = useId();
    const { data } = useAvisosNoLeidos();
    const { ve } = useSesion();
    const edicion = useEdicion();
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
        <div ref={contenedor} className="relative flex items-center">
            <span role="status" aria-live="polite" className="sr-only">{edicion.activo ? 'Modo edición activado' : ''}</span>
            <div className={`flex items-center rounded-full ${edicion.activo ? 'border-2 border-aviso p-1 pl-0' : ''}`}>
                {edicion.activo && <PildoraEdicion onSalir={() => edicion.fijar(false)} />}
                <button
                    type="button"
                    onClick={() => setAbierto(!abierto)}
                    aria-haspopup="menu"
                    aria-expanded={abierto}
                    aria-controls={menuId}
                    aria-label={etiquetaCuenta(usuario.nombre, total)}
                    className={`relative flex h-[36px] w-[36px] shrink-0 items-center justify-center rounded-full bg-primario-claro tipo-negrita text-sm text-primario focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario ${edicion.activo ? '' : 'hover:ring-2 hover:ring-primario-anillo'}`}
                >
                    {iniciales(usuario.nombre)}
                    {total > 0 && (
                        <span aria-hidden="true" className="absolute -top-1 -right-1 flex h-[18px] min-w-[18px] items-center justify-center rounded-full bg-error px-1 tipo-negrita text-[10px] text-white ring-2 ring-white">
                            {contador(total)}
                        </span>
                    )}
                </button>
            </div>
            {abierto && (
                <div id={menuId} role="menu" className="absolute top-full right-0 z-40 mt-2 w-[240px] rounded-2xl bg-white p-2 shadow-[0px_3px_24px_var(--color-sombra-menu)]">
                    <div className="flex items-start gap-2 px-3 py-2">
                        <User size={18} className="mt-px shrink-0 text-primario" />
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
                        <Bell size={18} className="shrink-0 text-primario" />
                        <span className="flex-1">Avisos</span>
                        {total > 0 && (
                            <span aria-hidden="true" className="flex h-[20px] min-w-[20px] items-center justify-center rounded-full bg-error px-1.5 tipo-negrita text-[11px] text-white">
                                {contador(total)}
                            </span>
                        )}
                    </Link>
                    {ve('rondas') && (
                        <Link to="/rondas" role="menuitem" onClick={() => setAbierto(false)} className={ITEM}>
                            <Refresh size={18} className="shrink-0 text-primario" />
                            Rondas
                        </Link>
                    )}
                    {ve('admin') && (
                        <Link to="/admin" role="menuitem" onClick={() => setAbierto(false)} className={ITEM}>
                            <Settings size={18} className="shrink-0 text-primario" />
                            Administración
                        </Link>
                    )}
                    {ve('editor') && (
                        <Link to="/editor" role="menuitem" onClick={() => setAbierto(false)} className={ITEM}>
                            <Edit size={18} className="shrink-0 text-primario" />
                            Editor de contenido
                        </Link>
                    )}
                    {edicion.disponible && (
                        <button
                            type="button"
                            role="menuitemcheckbox"
                            aria-checked={edicion.activo}
                            onClick={() => {
                                edicion.alternar();
                                setAbierto(false);
                            }}
                            className={ITEM}
                        >
                            <Edit size={18} className="shrink-0 text-primario" />
                            <span className="flex-1">Modo edición</span>
                            <span aria-hidden="true" className={`relative h-[18px] w-[32px] shrink-0 rounded-full transition-colors ${edicion.activo ? 'bg-primario' : 'bg-gris'}`}>
                                <span className={`absolute top-[2px] h-[14px] w-[14px] rounded-full bg-white transition-[left] ${edicion.activo ? 'left-[16px]' : 'left-[2px]'}`} />
                            </span>
                        </button>
                    )}
                    {usuario.tiene_cuenta && (
                        <button
                            type="button"
                            role="menuitem"
                            onClick={() => {
                                setAbierto(false);
                                setCambiando(true);
                            }}
                            className={ITEM}
                        >
                            <Lock size={18} className="shrink-0 text-primario" />
                            Cambiar contraseña
                        </button>
                    )}
                    <button type="button" role="menuitem" onClick={onSalir} className={ITEM}>
                        <Logout size={18} className="shrink-0 text-primario" />
                        Salir
                    </button>
                </div>
            )}
            <Modal abierto={cambiando} titulo="Cambiar contraseña" onCerrar={() => setCambiando(false)} ancho="max-w-lg">
                <CambiarContrasena onListo={() => setCambiando(false)} />
            </Modal>
        </div>
    );
};
