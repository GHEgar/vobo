export const Dato = ({ termino, children }) => (
    <div className="min-w-0">
        <dt className="tipo-media text-[11px] text-texto-apagado">{termino}</dt>
        <dd className="wrap-anywhere tipo-media text-sm text-texto">{children || '—'}</dd>
    </div>
);

export const Detalles = ({ id, abierto, children }) => (
    <dl id={id} hidden={!abierto} className="mt-3 grid grid-cols-1 gap-3 rounded-xl bg-fondo p-4 sm:grid-cols-2 lg:grid-cols-3">
        {children}
    </dl>
);
