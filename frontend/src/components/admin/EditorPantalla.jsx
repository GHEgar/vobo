import { useState } from 'react';
import { Button } from '@/components/Button';
import { Checkbox } from '@/components/Checkbox';
import { TextField } from '@/components/Field';
import { ControlesOrden } from '@/components/editor/ListaOrdenable';
import { useProyectosAdmin } from '@/hooks/useAdmin';
import { mover } from '@/utils/editor';
import { NOMBRES_VISTA, VISTAS as TODAS } from '@/utils/pantalla/formato';


const inicialVistas = (elegidas) => [
    ...elegidas.map((clave) => ({ clave, activa: true })),
    ...TODAS.filter((c) => !elegidas.includes(c)).map((clave) => ({ clave, activa: false })),
];

const Vistas = ({ vistas, onCambiar }) => (
    <fieldset className="mt-4 flex flex-col gap-2">
        <legend className="tipo-media text-sm text-texto">Vistas y su orden</legend>
        {vistas.map((vista, i) => (
            <div key={vista.clave} className="flex items-center justify-between gap-3 rounded-2xl bg-fondo px-4 py-2">
                <Checkbox
                    id={`pantalla-vista-${vista.clave}`}
                    checked={vista.activa}
                    onChange={(activa) => onCambiar(vistas.map((v) => (v.clave === vista.clave ? { ...v, activa } : v)))}
                >
                    {NOMBRES_VISTA[vista.clave]}
                </Checkbox>
                <ControlesOrden indice={i} total={vistas.length} nombre={NOMBRES_VISTA[vista.clave]} onMover={(delta) => onCambiar(mover(vistas, i, delta))} />
            </div>
        ))}
    </fieldset>
);

const Proyectos = ({ elegidos, onCambiar }) => {
    const estado = useProyectosAdmin();
    const activos = (estado.data?.proyectos ?? []).filter((p) => !p.archivado);
    const alternar = (clave, marcado) => onCambiar(marcado ? [...elegidos, clave] : elegidos.filter((c) => c !== clave));
    return (
        <fieldset className="mt-4 flex flex-col gap-2">
            <legend className="tipo-media text-sm text-texto">Proyectos</legend>
            <p className="tipo-media text-[11px] text-texto-apagado">Sin elegir ninguno, la pantalla muestra todos los proyectos activos. La vista general rota de tres en tres.</p>
            {activos.map((p) => (
                <Checkbox key={p.clave} id={`pantalla-proyecto-${p.clave}`} checked={elegidos.includes(p.clave)} onChange={(marcado) => alternar(p.clave, marcado)}>
                    {p.nombre}
                </Checkbox>
            ))}
        </fieldset>
    );
};

export const EditorPantalla = ({ pantalla, guardar, onGuardar }) => {
    const [nombre, setNombre] = useState(pantalla?.nombre ?? '');
    const [vistas, setVistas] = useState(() => inicialVistas(pantalla?.vistas ?? TODAS));
    const [segundos, setSegundos] = useState(String(pantalla?.segundos ?? 20));
    const [proyectos, setProyectos] = useState(pantalla?.proyectos ?? []);
    const elegidas = vistas.filter((v) => v.activa).map((v) => v.clave);
    const numero = Number(segundos);
    const segundosValidos = Number.isInteger(numero) && numero >= 10 && numero <= 300;
    const valido = nombre.trim() && elegidas.length > 0 && segundosValidos;

    const enviar = (e) => {
        e.preventDefault();
        onGuardar({ nombre: nombre.trim(), vistas: elegidas, segundos: numero, proyectos });
    };

    return (
        <form onSubmit={enviar} className="flex flex-col">
            <TextField id="pantalla-nombre" label="Nombre" required placeholder="Sala de juntas" value={nombre} onChange={(e) => setNombre(e.target.value)} />
            <Vistas vistas={vistas} onCambiar={setVistas} />
            <TextField
                id="pantalla-segundos"
                label="Segundos por vista"
                type="number"
                min={10}
                max={300}
                required
                value={segundos}
                error={segundosValidos ? null : 'Entre 10 y 300 segundos'}
                onChange={(e) => setSegundos(e.target.value)}
            />
            <Proyectos elegidos={proyectos} onCambiar={setProyectos} />
            {guardar.error && <p role="alert" className="mt-3 tipo-media text-xs text-error-fuerte">{guardar.error.message}</p>}
            <div className="mt-6 flex justify-end">
                <Button label={pantalla ? 'Guardar cambios' : 'Crear pantalla'} type="submit" disabled={!valido} loading={guardar.isPending} />
            </div>
        </form>
    );
};
