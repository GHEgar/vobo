import { Plus } from 'tesela/react';

export const BarraEdicion = ({ etiqueta, onClickCapture, children }) => (
    <div
        role="group"
        aria-label={etiqueta}
        onClickCapture={onClickCapture}
        className="absolute top-2 right-2 z-10 flex max-w-[calc(100%-1rem)] flex-wrap items-center justify-end gap-1 rounded-2xl bg-white p-1 shadow-[0px_2px_8px_var(--color-sombra-suave)] transition-opacity focus-within:opacity-100 [@media(hover:hover)]:opacity-60 [@media(hover:hover)]:group-hover/edicion:opacity-100 [@media(hover:hover)]:group-focus-within/edicion:opacity-100"
    >
        {children}
    </div>
);

export const AgregarFantasma = ({ texto, onClick, className = '' }) => (
    <button
        type="button"
        onClick={onClick}
        className={`mx-auto flex w-fit items-center gap-2 self-center rounded-full border-2 border-dashed border-aviso/70 bg-transparent px-4 py-2 tipo-negrita text-sm text-aviso-texto hover:bg-aviso-fondo/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-aviso-texto ${className}`}
    >
        <Plus size={16} className="shrink-0" />
        {texto}
    </button>
);
