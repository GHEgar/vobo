import { useState } from 'react';
import { Edit, Eye } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { Modal } from '@/components/Modal';
import { EditorCaso } from '@/components/editor/EditorCaso';
import { BotonIcono, ListaOrdenable } from '@/components/editor/ListaOrdenable';
import { casoVacio, conPrefijo } from '@/utils/editor';
import { FAMILIAS, SEVERIDADES } from '@/utils/etiquetas';
import { useRuta } from '@/hooks/useProyecto';

export const CasosSeccion = ({ casos, herramientas, procedimientos, errores, bloqueados, guardados, onChange }) => {
    const ruta = useRuta();
    const [editando, setEditando] = useState(null);
    const cerrar = () => setEditando(null);
    const listo = (caso) => {
        onChange(editando.indice === null ? [...casos, caso] : casos.map((c, i) => (i === editando.indice ? caso : c)));
        cerrar();
    };

    return (
        <>
            <ListaOrdenable
                titulo="Casos"
                descripcion="Cada caso es una prueba guiada. Los que ya tienen resultados no se pueden quitar ni cambiar de id."
                items={casos}
                onChange={onChange}
                onAgregar={() => setEditando({ indice: null, caso: casoVacio(herramientas[0]?.id) })}
                etiquetaNuevo="Agregar caso"
                nombre="caso"
                vacio="Esta sección todavía no tiene casos."
                error={errores.get('casos')}
                puedeQuitar={(caso) => !bloqueados.includes(caso?.id)}
            >
                {(caso, i) => {
                    const fallas = conPrefijo(errores, `casos.${i}`).size;
                    return (
                        <div className="flex flex-wrap items-center justify-between gap-2">
                            <div className="min-w-0">
                                <p className="tipo-negrita text-sm text-texto">{caso.titulo || 'Caso sin título'}</p>
                                <p className="tipo-media text-[11px] text-texto-apagado">
                                    {caso.id || 'sin id'} · {FAMILIAS[caso.familia] ?? caso.familia} · {caso.pasos.length} {caso.pasos.length === 1 ? 'paso' : 'pasos'}
                                </p>
                                <div className="mt-1 flex flex-wrap gap-1">
                                    <Chip tono={SEVERIDADES[caso.severidad]?.tono}>{SEVERIDADES[caso.severidad]?.texto ?? caso.severidad}</Chip>
                                    {bloqueados.includes(caso.id) && <Chip tono="aviso">Con resultados</Chip>}
                                    {fallas > 0 && <Chip tono="error">{fallas === 1 ? '1 error' : `${fallas} errores`}</Chip>}
                                </div>
                            </div>
                            <div className="flex shrink-0 gap-1">
                                {guardados.includes(caso.id) && (
                                    <a href={ruta(`/caso/${encodeURIComponent(caso.id)}`)} target="_blank" rel="noreferrer" aria-label={`Ver ${caso.id} como validador`} title="Ver como validador" className="inline-flex h-[30px] w-[30px] items-center justify-center rounded-full border border-gris bg-white text-texto-tenue hover:border-primario hover:text-primario">
                                        <Eye size={16} />
                                    </a>
                                )}
                                <BotonIcono etiqueta={`Editar ${caso.id || 'caso'}`} onClick={() => setEditando({ indice: i, caso })}>
                                    <Edit size={16} />
                                </BotonIcono>
                            </div>
                        </div>
                    );
                }}
            </ListaOrdenable>
            <Modal abierto={Boolean(editando)} titulo={editando?.indice === null ? 'Nuevo caso' : `Editar ${editando?.caso.id}`} onCerrar={cerrar}>
                {editando && (
                    <EditorCaso
                        caso={editando.caso}
                        herramientas={herramientas}
                        procedimientos={procedimientos}
                        errores={editando.indice === null ? new Map() : conPrefijo(errores, `casos.${editando.indice}`)}
                        idBloqueado={editando.indice !== null && bloqueados.includes(editando.caso.id)}
                        onListo={listo}
                        onCancelar={cerrar}
                    />
                )}
            </Modal>
        </>
    );
};
