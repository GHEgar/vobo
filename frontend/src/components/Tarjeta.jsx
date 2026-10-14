export const Tarjeta = ({ children, className = '', as: Etiqueta = 'section', ...rest }) => (
    <Etiqueta className={`rounded-2xl bg-white p-5 shadow-[0px_3px_12px_var(--color-sombra-tenue)] md:p-7 ${className}`} {...rest}>
        {children}
    </Etiqueta>
);

export const Titulo = ({ children, descripcion, accion }) => (
    <div className="mb-4 flex flex-wrap items-start justify-between gap-3 sm:flex-nowrap">
        <div className="min-w-0">
            <h2 className="tipo-negrita text-lg text-texto">{children}</h2>
            {descripcion && <p className="mt-1 tipo-media text-sm text-texto-tenue">{descripcion}</p>}
        </div>
        {accion && <div className="shrink-0">{accion}</div>}
    </div>
);
