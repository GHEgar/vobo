const TONOS = {
    neutro: 'bg-fondo-suave text-texto-tenue',
    marca: 'bg-primario-claro text-primario',
    exito: 'bg-pasa-fondo text-pasa',
    error: 'bg-falla-fondo text-falla',
    aviso: 'bg-pendiente-fondo text-pendiente',
};

export const Chip = ({ children, tono = 'neutro', activo = false, onClick, title }) => {
    const clases = `inline-flex min-h-[30px] max-w-full items-center gap-1 rounded-full px-4 py-1 text-left tipo-negrita text-xs ${TONOS[tono]} ${activo ? 'ring-1 ring-aviso' : ''}`;
    if (!onClick) return <span className={clases} title={title}>{children}</span>;
    return (
        <button type="button" onClick={onClick} aria-pressed={activo} title={title} className={`${clases} cursor-pointer hover:shadow-[0px_4px_12px_var(--color-sombra)]`}>
            {children}
        </button>
    );
};
