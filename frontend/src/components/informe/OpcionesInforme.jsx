import { Checkbox } from '@/components/Checkbox';
import { SelectField } from '@/components/Field';
import { SEVERIDADES, opciones as aOpciones } from '@/utils/etiquetas';
import { PARTES, SITUACIONES } from '@/utils/informeFallas';

const alternar = (lista, valor, activo) => (activo ? [...lista, valor] : lista.filter((v) => v !== valor));

const Grupo = ({ titulo, children }) => (
    <fieldset className="min-w-0">
        <legend className="tipo-negrita text-sm text-texto">{titulo}</legend>
        <div className="mt-2 flex flex-col gap-2">{children}</div>
    </fieldset>
);

const Todos = ({ id, total, elegidos, onCambiar, children }) => (
    <Checkbox id={id} checked={elegidos === total} indeterminado={elegidos > 0 && elegidos < total} onChange={onCambiar}>
        {children}
    </Checkbox>
);

export const OpcionesInforme = ({ opciones, proyectos, herramientas, nombreSistema, rondas, onCambiar }) => {
    const elegidos = opciones.proyectos;
    const sistemas = opciones.sistemas.length ? opciones.sistemas : herramientas;
    const fijarSistemas = (lista) => lista.length && onCambiar({ sistemas: lista.length === herramientas.length ? [] : lista });
    const fijarProyectos = (lista) => lista.length && onCambiar({ proyectos: lista });
    const parte = (valor) => (activo) => {
        const incluir = new Set(opciones.incluir);
        if (activo) incluir.add(valor);
        else incluir.delete(valor);
        onCambiar({ incluir });
    };

    return (
        <section aria-label="Opciones del informe" className="mb-8 rounded-xl border border-borde bg-fondo p-4 print:hidden md:p-5">
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                <Grupo titulo="Proyectos">
                    {proyectos.length > 1 && (
                        <Todos id="informe-proyectos-todos" total={proyectos.length} elegidos={elegidos.length} onCambiar={(activo) => activo && fijarProyectos(proyectos.map((p) => p.clave))}>
                            Todos
                        </Todos>
                    )}
                    {proyectos.map((p) => (
                        <Checkbox key={p.clave} id={`informe-proyecto-${p.clave}`} checked={elegidos.includes(p.clave)} onChange={(activo) => fijarProyectos(alternar(elegidos, p.clave, activo))}>
                            {p.nombre}{p.archivado ? ' (archivado)' : ''}
                        </Checkbox>
                    ))}
                </Grupo>
                <Grupo titulo="Herramientas">
                    {herramientas.length === 0 && <p className="tipo-media text-xs text-texto-apagado">Sin datos todavía.</p>}
                    {herramientas.length > 1 && (
                        <Todos id="informe-herramientas-todas" total={herramientas.length} elegidos={sistemas.length} onCambiar={(activo) => activo && fijarSistemas(herramientas)}>
                            Todas
                        </Todos>
                    )}
                    {herramientas.map((h) => (
                        <Checkbox key={h} id={`informe-herramienta-${h}`} checked={sistemas.includes(h)} onChange={(activo) => fijarSistemas(alternar(sistemas, h, activo))}>
                            {nombreSistema(h)}
                        </Checkbox>
                    ))}
                </Grupo>
                <Grupo titulo="Incluir">
                    {PARTES.map((p) => (
                        <Checkbox key={p.valor} id={`informe-incluir-${p.valor}`} checked={opciones.incluir.has(p.valor)} onChange={parte(p.valor)}>
                            {p.texto}
                        </Checkbox>
                    ))}
                </Grupo>
            </div>
            <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-3">
                {elegidos.length === 1 ? (
                    <SelectField id="informe-ronda" label="Ronda" value={opciones.ronda} onChange={(e) => onCambiar({ ronda: e.target.value })} placeholder="Todas" options={rondas.map((r) => ({ valor: String(r.id), texto: r.nombre }))} claseControl="bg-white" />
                ) : (
                    <p className="self-end tipo-media text-xs text-texto-apagado">Con varios proyectos se usan todas sus rondas.</p>
                )}
                <SelectField id="informe-situacion" label="Estado" value={opciones.estado ? '' : opciones.situacion} onChange={(e) => onCambiar({ situacion: e.target.value })} placeholder="Todas" options={SITUACIONES} claseControl="bg-white" />
                <SelectField id="informe-severidad" label="Severidad de las fallas" value={opciones.severidad} onChange={(e) => onCambiar({ severidad: e.target.value })} placeholder="Todas" options={aOpciones(SEVERIDADES)} claseControl="bg-white" />
            </div>
        </section>
    );
};
