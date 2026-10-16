import { ArrowDown, ArrowUp, Trash } from 'tesela/react';
import { BotonMas } from '@/components/BotonMas';
import { mover } from '@/utils/editor';

const ICONO = 'inline-flex h-[30px] w-[30px] items-center justify-center rounded-full border border-gris bg-white p-0 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario disabled:cursor-not-allowed disabled:opacity-40';

export const BotonIcono = ({ etiqueta, onClick, disabled, peligro = false, children }) => (
    <button
        type="button"
        aria-label={etiqueta}
        title={etiqueta}
        onClick={onClick}
        disabled={disabled}
        className={`${ICONO} ${peligro ? 'text-error-fuerte hover:border-error' : 'text-texto-tenue hover:border-primario hover:text-primario'}`}
    >
        {children}
    </button>
);

export const ControlesOrden = ({ indice, total, nombre, onMover, onQuitar }) => (
    <div className="flex shrink-0 gap-1">
        <BotonIcono etiqueta={`Subir ${nombre}`} disabled={indice === 0} onClick={() => onMover(-1)}>
            <ArrowUp size={16} />
        </BotonIcono>
        <BotonIcono etiqueta={`Bajar ${nombre}`} disabled={indice === total - 1} onClick={() => onMover(1)}>
            <ArrowDown size={16} />
        </BotonIcono>
        {onQuitar && (
            <BotonIcono etiqueta={`Quitar ${nombre}`} peligro onClick={onQuitar}>
                <Trash size={16} />
            </BotonIcono>
        )}
    </div>
);

export const ListaOrdenable = ({ titulo, descripcion, items, onChange, nuevo, etiquetaNuevo, nombre, vacio, error, onAgregar, puedeQuitar = () => true, children }) => (
    <section className="mt-6">
        <div className="flex items-start justify-between gap-3">
            <div>
                <h3 className="tipo-negrita text-sm text-texto">{titulo}</h3>
                {descripcion && <p className="tipo-media text-xs text-texto-apagado">{descripcion}</p>}
            </div>
            {(nuevo || onAgregar) && <BotonMas etiqueta={etiquetaNuevo} ayuda={etiquetaNuevo} onClick={onAgregar ?? (() => onChange([...items, nuevo()]))} />}
        </div>
        {error && <p className="mt-1 tipo-media text-xs text-error-fuerte">{error}</p>}
        {!items.length && vacio && <p className="mt-3 tipo-media text-xs text-texto-apagado">{vacio}</p>}
        {items.length > 0 && (
            <ol className="mt-3 flex flex-col gap-2">
                {items.map((item, i) => (
                    <li key={i} className="flex flex-col gap-2 rounded-2xl bg-fondo p-3 sm:flex-row sm:items-start">
                        <div className="min-w-0 flex-1 [&>*:first-child]:mt-0">
                            {children(item, i, (valor) => onChange(items.map((x, j) => (j === i ? valor : x))))}
                        </div>
                        <ControlesOrden
                            indice={i}
                            total={items.length}
                            nombre={`${nombre} ${i + 1}`}
                            onMover={(delta) => onChange(mover(items, i, delta))}
                            onQuitar={puedeQuitar(item) ? () => onChange(items.filter((_, j) => j !== i)) : null}
                        />
                    </li>
                ))}
            </ol>
        )}
    </section>
);
