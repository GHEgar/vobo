import { useState } from 'react';
import { History, User } from 'tesela/react';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { Desplegable } from '@/components/Desplegable';
import { Spinner } from '@/components/Spinner';
import { EmptyState, ErrorState } from '@/components/Estados';
import { Evento } from '@/components/actividad/Evento';
import { useActividad } from '@/hooks/useActividad';
import { TIPOS, agruparPorDia, personasDe } from '@/utils/actividad';

const TODAS = '';

const opcionesDePersonas = (eventos, presentes, elegida) => {
    const conocidas = personasDe([
        ...eventos,
        ...presentes.map((p) => ({ usuario: { email: p.email, nombre: p.nombre } })),
        ...(elegida ? [{ usuario: elegida }] : []),
    ]);
    return [{ valor: TODAS, texto: 'Todas las personas' }, ...conocidas.map((p) => ({ valor: p.email, texto: p.nombre }))];
};

const Filtros = ({ opciones, persona, onPersona, tipos, onTipo, onLimpiar }) => (
    <div className="flex flex-col gap-3">
        <Desplegable
            aria-label="Persona"
            opciones={opciones}
            value={persona?.email ?? TODAS}
            onChange={onPersona}
            prefijo={<User size={16} className="text-primario" />}
            className="w-full sm:max-w-[280px]"
        />
        <div role="group" aria-label="Tipos de evento" className="flex flex-wrap gap-1.5">
            {TIPOS.map((t) => {
                const activo = tipos.includes(t.valor);
                return (
                    <Chip key={t.valor} tono={activo ? 'marca' : 'neutro'} activo={activo} onClick={() => onTipo(t.valor)}>
                        {t.texto}
                    </Chip>
                );
            })}
            {(tipos.length > 0 || persona) && <Button label="Quitar filtros" variant="link" small onClick={onLimpiar} />}
        </div>
    </div>
);

export const Reciente = ({ presentes = [], onNavegar }) => {
    const [persona, setPersona] = useState(null);
    const [tipos, setTipos] = useState([]);
    const consulta = useActividad({ usuario: persona?.email ?? null, tipos });
    const todas = useActividad({ usuario: null, tipos });
    const eventos = consulta.data?.pages.flatMap((p) => p.eventos) ?? [];
    const conocidos = todas.data?.pages.flatMap((p) => p.eventos) ?? [];
    const opciones = opcionesDePersonas(conocidos, presentes, persona);
    const filtrando = Boolean(persona) || tipos.length > 0;

    const elegirPersona = (email) => {
        const opcion = opciones.find((o) => o.valor === email);
        setPersona(email ? { email, nombre: opcion?.texto ?? email } : null);
    };
    const alternarTipo = (tipo) => setTipos((actuales) => (actuales.includes(tipo) ? actuales.filter((t) => t !== tipo) : [...actuales, tipo]));
    const limpiar = () => {
        setPersona(null);
        setTipos([]);
    };

    return (
        <div className="flex flex-col gap-4">
            <Filtros opciones={opciones} persona={persona} onPersona={elegirPersona} tipos={tipos} onTipo={alternarTipo} onLimpiar={limpiar} />
            {consulta.isPending && <Spinner />}
            {consulta.error && <ErrorState mensaje={consulta.error.message} onReintentar={consulta.refetch} />}
            {consulta.data && !eventos.length && (
                <EmptyState
                    icono={History}
                    titulo={filtrando ? 'Nada coincide con estos filtros' : 'Todavía no hay actividad'}
                    descripcion={filtrando ? 'Prueba con otra persona u otro tipo de evento.' : 'Cuando el equipo marque casos, reporte fallas o comente, lo verás aquí.'}
                />
            )}
            {agruparPorDia(eventos).map((grupo) => (
                <section key={grupo.clave} aria-label={grupo.titulo}>
                    <h3 className="sticky top-0 z-10 bg-white py-1 tipo-negrita text-xs text-texto-apagado uppercase">{grupo.titulo}</h3>
                    <ul className="divide-y divide-borde">
                        {grupo.eventos.map((e) => <Evento key={e.id} evento={e} onNavegar={onNavegar} />)}
                    </ul>
                </section>
            ))}
            {consulta.hasNextPage && (
                <div className="flex justify-center">
                    <Button label="Cargar más" variant="ghost" small loading={consulta.isFetchingNextPage} onClick={() => consulta.fetchNextPage()} />
                </div>
            )}
        </div>
    );
};
