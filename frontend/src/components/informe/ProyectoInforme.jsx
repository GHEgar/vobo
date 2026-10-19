import { ComentarioInforme } from '@/components/informe/ComentarioInforme';
import { FallaInforme } from '@/components/informe/FallaInforme';
import { subtotalEsfuerzo } from '@/utils/informeFallas';

const cuenta = (n, uno, varios) => `${n} ${n === 1 ? uno : varios}`;

const conteo = (fallas, comentarios) => [
    fallas.length && cuenta(fallas.length, 'falla', 'fallas'),
    comentarios.length && cuenta(comentarios.length, 'comentario', 'comentarios'),
    subtotalEsfuerzo([...fallas, ...comentarios]),
].filter(Boolean).join(' · ');

export const ProyectoInforme = ({ proyecto, incluir }) => (
    <section className="mt-10">
        <h2 className="border-b-2 border-primario pb-1 tipo-negrita text-xl text-primario">
            {proyecto.nombre}
            <span className="ml-2 tipo-media text-sm text-texto-tenue">{conteo(proyecto.fallas, proyecto.comentarios)}</span>
        </h2>
        {proyecto.grupos.length === 0 && <p className="mt-3 text-sm text-texto-tenue">Sin fallas ni comentarios con estas opciones.</p>}
        {proyecto.grupos.map((g) => (
            <section key={g.clave || 'sin-herramienta'} className="mt-6">
                <h3 className="break-after-avoid border-b border-borde pb-1 tipo-negrita text-lg">
                    {g.nombre}
                    <span className="ml-2 tipo-media text-xs text-texto-apagado">{conteo(g.fallas, g.comentarios)}</span>
                </h3>
                {g.fallas.map((f) => <FallaInforme key={`f-${f.id}`} falla={f} incluir={incluir} />)}
                {g.comentarios.map((c) => <ComentarioInforme key={`c-${c.id ?? `${c.caso_id}-${c.usuario_email}-${c.tipo}-${c.paso}`}`} comentario={c} incluir={incluir} />)}
            </section>
        ))}
    </section>
);
