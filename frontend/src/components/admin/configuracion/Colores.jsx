import { useState } from 'react';
import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { RadioGroup } from '@/components/RadioGroup';
import { useGuardarConfiguracion } from '@/hooks/useAdmin';
import { COLOR_HEX, colorActual, variablesDeColor, variablesDeFuente } from '@/utils/estilos';
import { NombreProyecto } from '@/components/NombreProyecto';
import { Encabezado, PieGuardar, Restablecer } from '@/components/admin/configuracion/Comun';

const NOMBRES = {
    primario: 'Primario',
    'primario-hover': 'Primario al pasar el cursor',
    'primario-suave': 'Primario suave (fondos)',
    'primario-claro': 'Primario claro (chips y realces)',
    'primario-borde': 'Primario de bordes',
    texto: 'Texto',
    'texto-tenue': 'Texto tenue',
    'fondo-pagina': 'Fondo de la página',
    aviso: 'Aviso',
    error: 'Error',
    exito: 'Éxito',
    nombre: 'Nombre del proyecto',
};

const FUENTES = {
    tema: 'La del tema de archivos',
    producto: 'Rotulo, la incluida en la app',
    sistema: 'La del sistema operativo',
};

const SelectorColor = ({ token, valor, guardado, onCambiar, onQuitar }) => {
    const valido = COLOR_HEX.test(valor);
    return (
        <li className="flex flex-wrap items-center gap-3 rounded-2xl bg-fondo px-4 py-3">
            <input type="color" aria-label={NOMBRES[token]} value={valido ? valor : '#000000'} onChange={(e) => onCambiar(e.target.value.toUpperCase())} className="h-9 w-12 shrink-0 cursor-pointer rounded-lg border border-borde bg-white p-1" />
            <div className="min-w-0 flex-1">
                <p className="tipo-negrita text-xs text-texto">{NOMBRES[token]}</p>
                <p className={`tipo-media text-[11px] ${guardado ? 'text-aviso-texto' : 'text-texto-apagado'}`}>--color-{token} · {guardado ? 'cambiado en la app' : 'del tema'}</p>
            </div>
            <input aria-label={`${NOMBRES[token]} en hexadecimal`} value={valor} onChange={(e) => onCambiar(e.target.value)} aria-invalid={!valido} className={`h-9 w-24 rounded-lg border bg-white px-2 tipo-media text-xs text-texto ${valido ? 'border-borde' : 'border-error'}`} />
            {guardado && <Button label="Restablecer" small variant="link" onClick={onQuitar} />}
        </li>
    );
};

const VistaPrevia = ({ colores, fuente }) => (
    <div style={{ ...variablesDeColor(colores), ...variablesDeFuente(fuente) }} className="rounded-2xl bg-fondo-pagina p-4">
        <p className="mb-3 tipo-negrita text-xs text-texto-tenue">Vista previa, sin guardar</p>
        <div className="rounded-2xl bg-white p-5 shadow-[0px_3px_12px_var(--color-sombra-tenue)]">
            <div className="mb-4 flex items-center gap-3 border-b border-borde pb-3">
                <span className="tipo-negrita text-sm text-primario">Marca</span>
                <span aria-hidden="true" className="h-5 w-px bg-borde" />
                <NombreProyecto nombre="Nombre del proyecto" />
            </div>
            <p className="tipo-negrita text-base text-texto">Tarjeta de ejemplo</p>
            <p className="mt-1 tipo-media text-sm text-texto-tenue">Así se ve el texto tenue dentro de una tarjeta.</p>
            <div className="mt-4 flex flex-wrap items-center gap-2">
                <Chip tono="marca">Chip de la marca</Chip>
                <span className="tipo-negrita text-xs text-aviso">Aviso</span>
                <span className="tipo-negrita text-xs text-error">Error</span>
                <span className="tipo-negrita text-xs text-exito">Éxito</span>
            </div>
            <div className="mt-4 flex flex-wrap gap-2 rounded-xl bg-primario-suave p-3">
                <span className="inline-flex h-10 items-center rounded-full bg-primario px-6 tipo-negrita text-sm text-white">Botón principal</span>
                <span className="inline-flex h-10 items-center rounded-full bg-primario-hover px-6 tipo-negrita text-sm text-white">Al pasar el cursor</span>
                <span className="inline-flex h-10 items-center rounded-full border border-primario-borde bg-primario-claro px-6 tipo-negrita text-sm text-primario">Realce</span>
            </div>
        </div>
    </div>
);

export const Colores = ({ estado }) => {
    const guardar = useGuardarConfiguracion();
    const [colores, setColores] = useState(estado.colores);
    const [fuente, setFuente] = useState(estado.fuente);
    const [base] = useState(() => Object.fromEntries(estado.tokens.map((t) => [t, colorActual(t)])));
    const validos = Object.values(colores).every((c) => COLOR_HEX.test(c));
    const sinCambios = JSON.stringify(colores) === JSON.stringify(estado.colores) && fuente === estado.fuente;
    const quitar = (token) => {
        const resto = Object.fromEntries(Object.entries(colores).filter(([t]) => t !== token));
        setColores(resto);
        if (token in estado.colores) guardar.mutate({ colores: Object.fromEntries(Object.entries(estado.colores).filter(([t]) => t !== token)) });
    };

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                guardar.mutate({ colores, fuente });
            }}
        >
            <Encabezado titulo="Colores y fuente" descripcion="Reemplazan a los del tema de archivos. Lo que no cambies sigue saliendo del tema." clave="colores" guardada={estado.guardada} />
            <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
                <ul className="flex flex-col gap-2">
                    {estado.tokens.map((t) => (
                        <SelectorColor
                            key={t}
                            token={t}
                            valor={colores[t] ?? base[t]}
                            guardado={t in estado.colores}
                            onCambiar={(valor) => setColores({ ...colores, [t]: valor })}
                            onQuitar={() => quitar(t)}
                        />
                    ))}
                </ul>
                <div className="flex flex-col gap-4">
                    <VistaPrevia colores={colores} fuente={fuente} />
                    <div>
                        <RadioGroup name="config-fuente" label="Fuente" vertical options={estado.fuentes.map((f) => ({ valor: f, texto: FUENTES[f] ?? f }))} value={fuente} onChange={setFuente} />
                        <Restablecer clave="fuente" guardada={estado.guardada} etiqueta="Restablecer fuente" />
                    </div>
                </div>
            </div>
            {!validos && <p className="mt-2 tipo-media text-xs text-error-fuerte">Cada color debe tener el formato #RRGGBB</p>}
            <PieGuardar mutacion={guardar} deshabilitado={sinCambios || !validos} />
        </form>
    );
};
