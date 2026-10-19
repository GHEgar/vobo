export const Dato = ({ termino, children }) => (
    <div>
        <dt className="tipo-media text-[11px] text-texto-apagado">{termino}</dt>
        <dd className="wrap-anywhere text-[13px]">{children || '—'}</dd>
    </div>
);

export const Vencido = ({ activo, texto = 'Vencido' }) => (activo ? <span className="ml-1 tipo-negrita text-falla">· {texto}</span> : null);
