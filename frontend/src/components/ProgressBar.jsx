export const ProgressBar = ({ hechos, total, delgada = false, etiqueta }) => {
    const porcentaje = total ? Math.round((hechos / total) * 100) : 0;
    return (
        <div
            role="progressbar"
            aria-valuemin={0}
            aria-valuemax={100}
            aria-valuenow={porcentaje}
            aria-label={etiqueta ?? `${hechos} de ${total}`}
            className={`w-full overflow-hidden rounded-full bg-borde ${delgada ? 'h-1.5' : 'h-3'}`}
        >
            <div className={`h-full rounded-full ${porcentaje === 100 ? 'bg-pasa-barra' : 'bg-primario-medio'}`} style={{ width: `${porcentaje}%` }} />
        </div>
    );
};
