const lugar = (loc) => loc.map((parte) => (typeof parte === 'number' ? parte + 1 : parte)).join(' › ');

export const ResumenErrores = ({ error }) => {
    if (!error) return null;
    if (!error.detalle?.length) return <p role="alert" className="mt-4 tipo-media text-xs text-error-fuerte">{error.message}</p>;
    return (
        <div role="alert" className="mt-4 rounded-2xl bg-falla-fondo p-4">
            <p className="tipo-negrita text-sm text-falla">{error.message}</p>
            <ul className="mt-2 flex list-disc flex-col gap-1 pl-5">
                {error.detalle.map((e) => (
                    <li key={`${lugar(e.loc)}-${e.msg}`} className="tipo-media text-xs text-falla">
                        {e.loc.length > 0 && <span className="tipo-negrita">{lugar(e.loc)}: </span>}
                        {e.msg}
                    </li>
                ))}
            </ul>
        </div>
    );
};
