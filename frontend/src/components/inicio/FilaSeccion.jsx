import { Link } from 'react-router';
import { ChevronRight } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { ChipResultado } from '@/components/ChipResultado';
import { contornoEdicion } from '@/utils/edicion';
import { useSessionStorageState } from '@/hooks/useLocalStorageState';
import { estadoDe } from '@/utils/progreso';
import { useRuta } from '@/hooks/useProyecto';

export const FilaSeccion = ({ seccion, estados, abiertoInicial = false, destacado, acciones }) => {
    const ruta = useRuta();
    const [abierto, setAbierto] = useSessionStorageState(`validacion.inicio.abierta.${seccion.id}`, abiertoInicial);
    const panelId = `casos-${seccion.id}`;

    return (
        <li className={`rounded-2xl bg-fondo ${contornoEdicion(Boolean(acciones))}`}>
            <div className={`flex flex-wrap items-center gap-3 px-4 py-3 ${acciones ? 'pt-13 sm:pt-3 sm:pr-[192px]' : ''}`}>
                {seccion.oculta ? (
                    <>
                        <span aria-hidden="true" className="h-6 w-6 shrink-0" />
                        <span className="flex min-w-0 grow flex-wrap items-center gap-2 opacity-60">
                            <span className="tipo-negrita text-sm text-texto">{seccion.titulo}</span>
                            <Chip tono="aviso">Oculta</Chip>
                        </span>
                    </>
                ) : (
                    <>
                        <button
                            type="button"
                            onClick={() => setAbierto(!abierto)}
                            aria-expanded={abierto}
                            aria-controls={panelId}
                            aria-label={abierto ? `Ocultar casos de ${seccion.titulo}` : `Ver casos de ${seccion.titulo}`}
                            className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-transparent tipo-negrita text-primario hover:bg-primario-claro"
                        >
                            <ChevronRight size={16} className={`transition-transform ${abierto ? 'rotate-90' : ''}`} />
                        </button>
                        <Link to={ruta(`/seccion/${seccion.id}`)} className="flex min-w-0 grow basis-48 flex-wrap items-center justify-between gap-2 hover:underline">
                            <span className="tipo-negrita text-sm text-texto">{seccion.titulo}</span>
                            <span className="tipo-media text-xs text-texto-tenue">{seccion.progreso.hechos} de {seccion.progreso.total}</span>
                        </Link>
                    </>
                )}
            </div>
            {acciones}
            {abierto && !seccion.oculta && (
                <ul id={panelId} className="flex flex-col gap-1 px-4 pb-4 pl-13">
                    {seccion.casos.map((c) => {
                        const estado = estadoDe(estados, c.id);
                        return (
                            <li key={c.id}>
                                <Link to={ruta(`/caso/${encodeURIComponent(c.id)}`)} aria-current={c.id === destacado ? 'step' : undefined} className="flex items-center justify-between gap-3 rounded-xl bg-white px-4 py-2 hover:bg-primario-claro">
                                    <span className="flex min-w-0 flex-col">
                                        <span className={`text-[11px] ${c.id === destacado ? 'tipo-negrita text-aviso' : 'tipo-media text-texto-apagado'}`}>{c.id}</span>
                                        <span className="tipo-negrita text-sm text-texto">{c.titulo}</span>
                                    </span>
                                    <ChipResultado estado={estado} activo={c.id === destacado} />
                                </Link>
                            </li>
                        );
                    })}
                </ul>
            )}
        </li>
    );
};
