import { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/Button';
import { BotonMas } from '@/components/BotonMas';
import { Titulo } from '@/components/Tarjeta';
import { AgregarPersonas } from '@/components/rondas/AgregarPersonas';
import { Spinner } from '@/components/Spinner';
import { PersonaAsignacion } from '@/components/rondas/PersonaAsignacion';
import { useAsignaciones, useContenido, useGuardarAsignaciones, useUsuarios } from '@/hooks/useValidacion';

const agrupar = (asignaciones) => asignaciones.reduce((mapa, a) => {
    mapa[a.usuario_email] = [...(mapa[a.usuario_email] ?? []), a.seccion_id];
    return mapa;
}, {});

const EstadoGuardado = ({ guardar }) => {
    if (guardar.isPending) return <span role="status" className="tipo-media text-xs text-texto-apagado">Guardando…</span>;
    if (guardar.isError) return <span role="alert" className="tipo-media text-xs text-error-fuerte">No se guardó: {guardar.error.message}</span>;
    if (guardar.isSuccess) return <span role="status" className="tipo-media text-xs text-pasa">Cambios guardados ✓</span>;
    return null;
};

const Editor = ({ ronda, inicial, secciones, usuarios }) => {
    const guardar = useGuardarAsignaciones();
    const [porPersona, setPorPersona] = useState(() => agrupar(inicial));
    const [agregando, setAgregando] = useState(false);
    const [abiertos, setAbiertos] = useState(() => {
        const iniciales = Object.keys(agrupar(inicial));
        return new Set(iniciales.length > 3 ? [] : iniciales);
    });
    const personas = Object.keys(porPersona).sort();
    const porEmail = new Map(usuarios.map((u) => [u.email, u]));
    const todosAbiertos = personas.length > 0 && personas.every((e) => abiertos.has(e));

    const alternarAbierto = (email) => {
        const siguiente = new Set(abiertos);
        if (siguiente.has(email)) siguiente.delete(email);
        else siguiente.add(email);
        setAbiertos(siguiente);
    };

    const alternarTodo = () => setAbiertos(new Set(todosAbiertos ? [] : personas));

    const alternar = (email, seccionId, marcado) => {
        const actuales = porPersona[email] ?? [];
        setPorPersona({ ...porPersona, [email]: marcado ? [...actuales, seccionId] : actuales.filter((s) => s !== seccionId) });
    };

    const todas = secciones.map((s) => s.id);

    const fijarSecciones = (email, ids) => setPorPersona({ ...porPersona, [email]: ids });

    const guardado = useRef(JSON.stringify(porPersona));
    const { mutate } = guardar;

    useEffect(() => {
        const actual = JSON.stringify(porPersona);
        if (actual === guardado.current) return undefined;
        const lista = Object.entries(porPersona).flatMap(([email, ids]) => ids.map((seccion_id) => ({ usuario_email: email, seccion_id })));
        const espera = setTimeout(() => {
            guardado.current = actual;
            mutate({ rondaId: ronda.id, items: lista });
        }, 600);
        return () => clearTimeout(espera);
    }, [porPersona, mutate, ronda.id]);

    const agregar = (emails) => {
        const nuevos = emails.filter((email) => !porPersona[email]);
        if (!nuevos.length) return;
        setPorPersona({ ...porPersona, ...Object.fromEntries(nuevos.map((email) => [email, todas])) });
        if (personas.length + nuevos.length <= 3) setAbiertos(new Set([...abiertos, ...nuevos]));
    };

    const conocidos = usuarios.filter((u) => !porPersona[u.email]);

    return (
        <div className="flex flex-col gap-4">
            <Titulo
                descripcion="Quien no tiene secciones asignadas ve todas."
                accion={(
                    <span className="flex items-center gap-2">
                        <EstadoGuardado guardar={guardar} />
                        {personas.length > 0 && <Button label={todosAbiertos ? 'Plegar todo' : 'Expandir todo'} small variant="ghost" onClick={alternarTodo} />}
                        <BotonMas etiqueta="Agregar personas" ayuda="Agrega personas a esta ronda; quien no tiene secciones asignadas ve todas" onClick={() => setAgregando(true)} />
                    </span>
                )}
            >
                Asignaciones de {ronda.nombre}
            </Titulo>
            <AgregarPersonas abierto={agregando} onCerrar={() => setAgregando(false)} conocidos={conocidos} onAgregar={agregar} />
            {!personas.length && <p className="tipo-media text-sm text-texto-apagado">Nadie asignado: todo el equipo ve todas las secciones.</p>}
            {personas.map((email) => (
                <PersonaAsignacion
                    key={email}
                    email={email}
                    usuario={porEmail.get(email)}
                    elegidas={porPersona[email] ?? []}
                    secciones={secciones}
                    abierto={abiertos.has(email)}
                    onAlternarAbierto={() => alternarAbierto(email)}
                    onAlternar={(seccionId, marcado) => alternar(email, seccionId, marcado)}
                    onFijar={(ids) => fijarSecciones(email, ids)}
                />
            ))}
        </div>
    );
};

export const AsignacionesEditor = ({ ronda }) => {
    const asignaciones = useAsignaciones(ronda.id);
    const contenido = useContenido();
    const usuarios = useUsuarios();
    if (asignaciones.isPending || contenido.isPending || usuarios.isPending) return <Spinner />;
    const validas = new Set((contenido.data?.secciones ?? []).map((s) => s.id));
    return (
        <Editor
            key={ronda.id}
            ronda={ronda}
            inicial={(asignaciones.data ?? []).filter((a) => validas.has(a.seccion_id))}
            secciones={contenido.data?.secciones ?? []}
            usuarios={usuarios.data ?? []}
        />
    );
};
