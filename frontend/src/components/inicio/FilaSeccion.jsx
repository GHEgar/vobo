import { useState } from 'react';
import { Link } from 'react-router';
import { Chip } from '@/components/Chip';
import { ESTADOS_RESULTADO } from '@/utils/etiquetas';
import { estadoDe } from '@/utils/progreso';

export const FilaSeccion = ({ seccion, estados, abiertoInicial = false, destacado }) => {
    const [abierto, setAbierto] = useState(abiertoInicial);
    const panelId = `casos-${seccion.id}`;

    return (
        <li className="rounded-2xl bg-fondo">
            <div className="flex items-center gap-3 px-4 py-3">
                <button
                    type="button"
                    onClick={() => setAbierto(!abierto)}
                    aria-expanded={abierto}
                    aria-controls={panelId}
                    aria-label={abierto ? `Ocultar casos de ${seccion.titulo}` : `Ver casos de ${seccion.titulo}`}
                    className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-transparent tipo-negrita text-primario hover:bg-primario-claro"
                >
                    <span aria-hidden="true" className={`inline-block transition-transform ${abierto ? 'rotate-90' : ''}`}>›</span>
                </button>
                <Link to={`/seccion/${seccion.id}`} className="flex min-w-0 grow flex-wrap items-center justify-between gap-2 hover:underline">
                    <span className="tipo-negrita text-sm text-texto">{seccion.titulo}</span>
                    <span className="tipo-media text-xs text-texto-tenue">{seccion.progreso.hechos} de {seccion.progreso.total}</span>
                </Link>
            </div>
            {abierto && (
                <ul id={panelId} className="flex flex-col gap-1 px-4 pb-4 pl-13">
                    {seccion.casos.map((c) => {
                        const estado = ESTADOS_RESULTADO[estadoDe(estados, c.id)];
                        return (
                            <li key={c.id}>
                                <Link to={`/caso/${encodeURIComponent(c.id)}`} aria-current={c.id === destacado ? 'step' : undefined} className="flex items-center justify-between gap-3 rounded-xl bg-white px-4 py-2 hover:bg-primario-claro">
                                    <span className="flex min-w-0 flex-col">
                                        <span className={`text-[11px] ${c.id === destacado ? 'tipo-negrita text-aviso' : 'tipo-media text-texto-apagado'}`}>{c.id}</span>
                                        <span className="tipo-negrita text-sm text-texto">{c.titulo}</span>
                                    </span>
                                    <Chip tono={estado.tono} activo={c.id === destacado}>{estado.texto}</Chip>
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            )}
        </li>
    );
};
