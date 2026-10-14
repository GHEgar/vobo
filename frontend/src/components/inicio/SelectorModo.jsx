const OPCION = 'h-[30px] rounded-full px-4 tipo-negrita text-xs focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-aviso focus-visible:ring-offset-2';

export const SelectorModo = ({ modo, onCambiar, conteos }) => (
    <div className="flex w-fit gap-1 rounded-full bg-fondo p-1" role="group" aria-label="Tipo de casos">
        {[['funcional', 'Funcional'], ['tecnica', 'Técnico']].map(([valor, texto]) => (
            <button
                key={valor}
                type="button"
                aria-pressed={modo === valor}
                onClick={() => onCambiar(valor)}
                className={`${OPCION} ${modo === valor ? 'bg-aviso text-white' : 'bg-transparent text-texto-tenue hover:text-aviso'}`}
            >
                {texto}{conteos ? ` · ${conteos[valor]}` : ''}
            </button>
        ))}
    </div>
);
