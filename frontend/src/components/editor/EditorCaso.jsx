import { useState } from 'react';
import { Button } from '@/components/Button';
import { SelectField, TextField } from '@/components/Field';
import { ListaOrdenable } from '@/components/editor/ListaOrdenable';
import { FAMILIAS, MODOS, SEVERIDADES, opciones } from '@/utils/etiquetas';
import { pasoVacio } from '@/utils/editor';

const Fila = ({ children }) => <div className="grid gap-x-4 sm:grid-cols-2">{children}</div>;

const NOTA = 'Los cambios del caso se guardan al guardar la sección.';

export const EditorCaso = ({ caso, herramientas, procedimientos, errores, idBloqueado, onListo, onCancelar, etiquetaListo = 'Listo', guardando = false, nota = NOTA, children }) => {
    const [borrador, setBorrador] = useState(caso);
    const valor = (nombre) => ({
        value: borrador[nombre] ?? '',
        onChange: (e) => setBorrador({ ...borrador, [nombre]: e.target.value }),
    });
    const campo = (nombre) => ({ ...valor(nombre), error: errores.get(nombre) });
    const opcionesProcedimiento = procedimientos.map((p) => ({ valor: p.id, texto: p.datos.titulo || p.id }));

    return (
        <form
            className="flex flex-col"
            onSubmit={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onListo({ ...borrador, id: borrador.id.trim() });
            }}
        >
            <Fila>
                <TextField
                    id="caso-id"
                    label="Id del caso"
                    required
                    tooltip={idBloqueado ? 'Este caso ya tiene resultados guardados; su id no cambia.' : 'Por ejemplo C-CAT-04. Debe ser único en todo el contenido.'}
                    disabled={idBloqueado}
                    maxLength={60}
                    {...campo('id')}
                />
                <TextField id="caso-titulo" label="Título" required {...campo('titulo')} />
            </Fila>
            <Fila>
                <div className="mt-4">
                    <SelectField id="caso-familia" label="Familia" options={opciones(FAMILIAS).map((o) => ({ ...o, texto: `${o.valor} · ${o.texto}` }))} {...valor('familia')} />
                </div>
                <div className="mt-4">
                    <SelectField id="caso-severidad" label="Severidad si falla" options={opciones(SEVERIDADES)} {...valor('severidad')} />
                </div>
                <div className="mt-4">
                    <SelectField id="caso-herramienta" label="Herramienta" options={herramientas.map((h) => ({ valor: h.id, texto: h.nombre || h.id }))} {...valor('herramienta')} />
                    {errores.get('herramienta') && <p className="mt-1 tipo-media text-xs text-error-fuerte">{errores.get('herramienta')}</p>}
                </div>
                <div className="mt-4">
                    <SelectField id="caso-modo" label="Modo" options={opciones(MODOS)} {...valor('modo')} />
                </div>
                <TextField id="caso-rol" label="Rol" placeholder="Por ejemplo Cliente" {...campo('rol')} />
                <TextField id="caso-cuenta" label="Cuenta" placeholder="Por ejemplo val-cliente-01" {...campo('cuenta')} />
            </Fila>
            <TextField id="caso-antes" label="Antes de empezar" multiline rows={2} {...campo('antes')} />
            <ListaOrdenable
                titulo="Pasos"
                descripcion="Lo que hace la persona, en orden. Cada paso puede enlazar un procedimiento con su animación."
                items={borrador.pasos}
                onChange={(pasos) => setBorrador({ ...borrador, pasos })}
                nuevo={pasoVacio}
                etiquetaNuevo="Agregar paso"
                nombre="paso"
                error={errores.get('pasos')}
            >
                {(paso, i, cambiar) => (
                    <>
                        <TextField
                            id={`caso-paso-${i}`}
                            label={`Paso ${i + 1}`}
                            multiline
                            rows={2}
                            required
                            value={paso.texto}
                            error={errores.get(`pasos.${i}.texto`)}
                            onChange={(e) => cambiar({ ...paso, texto: e.target.value })}
                        />
                        <div className="mt-3">
                            <SelectField
                                id={`caso-paso-${i}-procedimiento`}
                                label="Procedimiento"
                                placeholder="Sin procedimiento"
                                options={opcionesProcedimiento}
                                value={paso.procedimiento ?? ''}
                                onChange={(e) => cambiar({ ...paso, procedimiento: e.target.value || null })}
                            />
                            {errores.get(`pasos.${i}.procedimiento`) && <p className="mt-1 tipo-media text-xs text-error-fuerte">{errores.get(`pasos.${i}.procedimiento`)}</p>}
                        </div>
                    </>
                )}
            </ListaOrdenable>
            <TextField id="caso-esperado" label="Resultado esperado" multiline rows={2} required {...campo('esperado')} />
            {nota && <p className="mt-4 tipo-media text-xs text-texto-apagado">{nota}</p>}
            {children}
            <div className="mt-4 flex justify-end gap-2">
                <Button label="Cancelar" variant="link" onClick={onCancelar} />
                <Button label={etiquetaListo} type="submit" loading={guardando} disabled={!borrador.id.trim() || !borrador.titulo.trim()} />
            </div>
        </form>
    );
};
