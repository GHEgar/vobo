import { Alert, Logout } from 'tesela/react';

export const PildoraEdicion = ({ onSalir }) => (
    <span className="flex origin-right items-center gap-2.5 pr-2.5 pl-3.5 text-aviso-texto motion-safe:animate-emerger">
        <Alert size={16} className="block shrink-0" aria-hidden="true" />
        <span className="flex h-4 items-center whitespace-nowrap tipo-negrita text-xs leading-none max-sm:sr-only">Modo edición</span>
        <button
            type="button"
            onClick={onSalir}
            aria-label="Salir del modo edición"
            title="Salir del modo edición"
            className="ml-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-aviso-texto text-white hover:bg-aviso focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-aviso focus-visible:ring-offset-1"
        >
            <Logout size={16} aria-hidden="true" />
        </button>
    </span>
);
