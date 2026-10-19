const Celda = ({ children, encabezado }) => {
    if (encabezado) return <th scope="col" className="py-2 pl-3 align-bottom text-right first:w-1/4 first:pl-0 first:text-left">{children}</th>;
    return <td className="wrap-anywhere py-1.5 pl-3 text-right tipo-negrita first:pl-0 first:text-left first:tipo-media">{children}</td>;
};

export const ResumenInforme = ({ proyectos, incluir }) => {
    const tiempos = incluir.has('tiempos');
    const comentarios = incluir.has('comentarios');
    const columnas = [
        ['Proyecto', (p) => p.nombre],
        [tiempos ? 'Fallas abiertas / resueltas / vencidas' : 'Fallas abiertas / resueltas', (p) => [p.resumen.fallasAbiertas, p.resumen.fallasResueltas, ...(tiempos ? [p.resumen.fallasVencidas] : [])].join(' / ')],
        ...(tiempos ? [['Tiempo medio', (p) => p.resumen.tiempoMedio || '—']] : []),
        ...(comentarios ? [[tiempos ? 'Comentarios abiertos / resueltos / vencidos' : 'Comentarios abiertos / resueltos', (p) => [p.resumen.comentariosAbiertos, p.resumen.comentariosResueltos, ...(tiempos ? [p.resumen.comentariosVencidos] : [])].join(' / ')]] : []),
        ['Esfuerzo total', (p) => p.resumen.esfuerzoTotal],
        ['Esfuerzo pendiente', (p) => p.resumen.esfuerzoPendiente],
    ];
    return (
        <section className="mt-8 break-inside-avoid-page">
            <h2 className="border-b border-borde pb-1 tipo-negrita text-lg text-primario">Resumen</h2>
            <div className="mt-2 overflow-x-auto print:overflow-visible">
                <table className="w-full table-fixed border-collapse text-left text-[13px] print:text-[11px]">
                    <thead>
                        <tr className="tipo-negrita text-[11px] text-texto-apagado">
                            {columnas.map(([titulo]) => <Celda key={titulo} encabezado>{titulo}</Celda>)}
                        </tr>
                    </thead>
                    <tbody>
                        {proyectos.map((p) => (
                            <tr key={p.clave} className="border-t border-borde">
                                {columnas.map(([titulo, valor]) => <Celda key={titulo}>{valor(p)}</Celda>)}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
};
