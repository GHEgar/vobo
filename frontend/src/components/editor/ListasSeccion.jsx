import { SelectField, TextField } from '@/components/Field';
import { ListaOrdenable } from '@/components/editor/ListaOrdenable';
import { HOY, opciones } from '@/utils/etiquetas';

const MensajeError = ({ texto }) => (texto ? <p className="mt-1 tipo-media text-xs text-error-fuerte">{texto}</p> : null);

export const QueCambia = ({ items, onChange, errores }) => (
    <ListaOrdenable
        titulo="Qué cambia"
        descripcion="Una idea por renglón; se muestra como lista al abrir la sección."
        items={items}
        onChange={onChange}
        nuevo={() => ''}
        etiquetaNuevo="Agregar renglón"
        nombre="renglón"
        vacio="Sin renglones."
    >
        {(texto, i, cambiar) => (
            <TextField id={`que-cambia-${i}`} label={`Renglón ${i + 1}`} value={texto} error={errores.get(`que_cambia.${i}`)} onChange={(e) => cambiar(e.target.value)} />
        )}
    </ListaOrdenable>
);

export const Herramientas = ({ items, onChange, errores, bloqueadas }) => (
    <ListaOrdenable
        titulo="Herramientas"
        descripcion="Los casos se agrupan por herramienta. Las que tienen decisiones o aprobaciones no cambian de id."
        items={items}
        onChange={onChange}
        nuevo={() => ({ id: '', nombre: '', hoy: 'prod' })}
        etiquetaNuevo="Agregar herramienta"
        nombre="herramienta"
        error={errores.get('herramientas')}
        puedeQuitar={(h) => !bloqueadas.includes(h.id)}
    >
        {(herramienta, i, cambiar) => (
            <div className="grid gap-x-3 sm:grid-cols-[1fr_1fr_160px]">
                <TextField
                    id={`herramienta-${i}-id`}
                    label="Id"
                    required
                    disabled={bloqueadas.includes(herramienta.id)}
                    value={herramienta.id}
                    error={errores.get(`herramientas.${i}.id`)}
                    onChange={(e) => cambiar({ ...herramienta, id: e.target.value.trim() })}
                />
                <TextField id={`herramienta-${i}-nombre`} label="Nombre" value={herramienta.nombre} onChange={(e) => cambiar({ ...herramienta, nombre: e.target.value })} />
                <div className="mt-4">
                    <SelectField id={`herramienta-${i}-hoy`} label="Hoy" options={opciones(HOY)} value={herramienta.hoy} onChange={(e) => cambiar({ ...herramienta, hoy: e.target.value })} />
                </div>
            </div>
        )}
    </ListaOrdenable>
);

export const MediaGaleria = ({ items, onChange, errores, procedimientos }) => (
    <ListaOrdenable
        titulo="Galería"
        descripcion="Animaciones de procedimientos que se muestran al abrir la sección."
        items={items}
        onChange={onChange}
        nuevo={() => ({ procedimiento: procedimientos[0]?.id ?? '', pie: '' })}
        etiquetaNuevo="Agregar a la galería"
        nombre="animación"
        vacio="Sin animaciones en la galería."
    >
        {(item, i, cambiar) => (
            <div className="grid gap-x-3 sm:grid-cols-2">
                <div className="mt-4">
                    <SelectField
                        id={`media-${i}-procedimiento`}
                        label="Procedimiento"
                        options={procedimientos.map((p) => ({ valor: p.id, texto: `${p.datos.titulo || p.id}${p.media ? '' : ' (sin animación)'}` }))}
                        value={item.procedimiento}
                        onChange={(e) => cambiar({ ...item, procedimiento: e.target.value })}
                    />
                    <MensajeError texto={errores.get(`media.${i}.procedimiento`)} />
                </div>
                <TextField id={`media-${i}-pie`} label="Pie" value={item.pie} onChange={(e) => cambiar({ ...item, pie: e.target.value })} />
            </div>
        )}
    </ListaOrdenable>
);
