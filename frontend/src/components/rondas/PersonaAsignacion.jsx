import { useState } from 'react';
import { Checkbox } from '@/components/Checkbox';
import { Chip } from '@/components/Chip';
import { Tooltip } from '@/components/Tooltip';
import { useProyectos } from '@/hooks/useInstancia';
import { rolesDe } from '@/utils/roles';
import { seccionesPorProyecto } from '@/utils/proyectos';

const SeleccionarTodo = ({ id, marcadas, total, onFijar, etiqueta, ayuda }) => (
    <span className="group relative inline-flex items-center">
        <Checkbox
            id={id}
            tono="naranja"
            etiqueta={etiqueta}
            describe={`${id}-ayuda`}
            checked={total > 0 && marcadas === total}
            indeterminado={marcadas > 0 && marcadas < total}
            onChange={() => onFijar(marcadas === total && total > 0 ? 'nada' : 'todo')}
        />
        <span
            id={`${id}-ayuda`}
            role="tooltip"
            className="pointer-events-none absolute top-full right-0 z-20 mt-2 hidden w-max max-w-[min(280px,calc(100vw-32px))] rounded bg-neutro px-2 py-1 tipo-negrita text-[11px] text-white group-hover:block group-focus-within:block"
        >
            {ayuda}
        </span>
    </span>
);

const tonoDe = (marcadas, total) => {
    if (marcadas === 0) return 'neutro';
    return marcadas === total ? 'exito' : 'marca';
};

export const PersonaAsignacion = ({ email, usuario, elegidas, secciones, abierto, onAlternarAbierto, onAlternar, onFijar }) => {
    const [filtro, setFiltro] = useState([]);
    const panelId = `secciones-${email}`;
    const proyectos = useProyectos();
    const grupos = seccionesPorProyecto(proyectos, secciones).map((g) => ({
        ...g,
        marcadas: g.secciones.filter((s) => elegidas.includes(s.id)).length,
    }));
    const visibles = filtro.length ? grupos.filter((g) => filtro.includes(g.clave)) : grupos;
    const desplegado = abierto || filtro.length > 0;

    const alternarFiltro = (clave) => setFiltro(filtro.includes(clave) ? filtro.filter((c) => c !== clave) : [...filtro, clave]);
    const fijarProyecto = (grupo, marcar) => {
        const ids = new Set(grupo.secciones.map((s) => s.id));
        const resto = elegidas.filter((id) => !ids.has(id));
        onFijar(marcar ? [...resto, ...ids] : resto);
    };
    const alternarPanel = () => {
        if (desplegado) {
            setFiltro([]);
            if (abierto) onAlternarAbierto();
            return;
        }
        onAlternarAbierto();
    };

    return (
        <section className="rounded-2xl bg-fondo">
            <div className={`flex flex-wrap items-center justify-between gap-3 px-4 pt-3 ${desplegado ? '' : 'pb-3'}`}>
                <button
                    type="button"
                    onClick={alternarPanel}
                    aria-expanded={desplegado}
                    aria-controls={panelId}
                    className="flex min-w-0 items-center gap-3 bg-transparent p-0 text-left"
                >
                    <span aria-hidden="true" className={`inline-block tipo-negrita text-primario transition-transform ${desplegado ? 'rotate-90' : ''}`}>›</span>
                    <span className="flex min-w-0 flex-col">
                        <span className="truncate tipo-negrita text-sm text-texto">{usuario?.nombre ?? email}</span>
                        {usuario && <span className="truncate tipo-media text-[11px] text-texto-apagado">{email}</span>}
                    </span>
                </button>
                <div className="flex flex-wrap items-center gap-2">
                    <span className="tipo-media text-xs text-texto-tenue">{elegidas.length} de {secciones.length} secciones</span>
                    {rolesDe(usuario?.permisos).map((r) => <Chip key={r} tono="marca">{r}</Chip>)}
                    <SeleccionarTodo
                        id={`todas-${email}`}
                        marcadas={elegidas.length}
                        total={secciones.length}
                        onFijar={(accion) => onFijar(accion === 'todo' ? secciones.map((s) => s.id) : [])}
                        etiqueta={`Asignar todas las secciones a ${usuario?.nombre ?? email}`}
                        ayuda="Marca o quita todas las secciones de esta persona. Con guion, tiene solo algunas: al pulsar se marcan todas."
                    />
                </div>
            </div>
            {desplegado && (
                <div className="flex flex-wrap items-center gap-2 px-4 pt-3 pb-3">
                    <Tooltip text="Pulsa un proyecto para ver solo sus secciones; puedes elegir varios. Sin ninguno elegido, al desplegar se ven todos." />
                    {grupos.map((g) => (
                        <Chip
                            key={g.clave}
                            tono={tonoDe(g.marcadas, g.secciones.length)}
                            activo={filtro.includes(g.clave)}
                            onClick={() => alternarFiltro(g.clave)}
                            title={`${g.marcadas} de ${g.secciones.length} secciones asignadas`}
                        >
                            {g.nombre} {g.marcadas}/{g.secciones.length}
                        </Chip>
                    ))}
                </div>
            )}
            {desplegado && (
                <div id={panelId} className="flex flex-col gap-4 px-4 pb-4">
                    {visibles.map((g) => (
                        <fieldset key={g.clave} className="rounded-xl bg-white p-3">
                            <legend className="sr-only">{g.nombre} · {email}</legend>
                            <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
                                <span className="tipo-negrita text-sm text-primario">{g.nombre}</span>
                                <SeleccionarTodo
                                    id={`todo-${email}-${g.clave}`}
                                    marcadas={g.marcadas}
                                    total={g.secciones.length}
                                    onFijar={(accion) => fijarProyecto(g, accion === 'todo')}
                                    etiqueta={`Asignar todo ${g.nombre}`}
                                    ayuda={`Marca o quita todas las secciones de ${g.nombre} para esta persona. Con guion, tiene solo algunas.`}
                                />
                            </div>
                            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
                                {g.secciones.map((s) => (
                                    <Checkbox
                                        key={s.id}
                                        id={`${email}-${s.id}`}
                                        checked={elegidas.includes(s.id)}
                                        onChange={(marcado) => onAlternar(s.id, marcado)}
                                    >
                                        {s.titulo}
                                    </Checkbox>
                                ))}
                            </div>
                        </fieldset>
                    ))}
                </div>
            )}
        </section>
    );
};
