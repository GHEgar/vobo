import { useState } from 'react';
import { TextField } from '@/components/Field';
import { ListaOrdenable } from '@/components/editor/ListaOrdenable';
import { useGuardarConfiguracion } from '@/hooks/useAdmin';
import { claveDesde } from '@/utils/claves';
import { Encabezado, PieGuardar } from '@/components/admin/configuracion/Comun';

const CLAVE = /^[a-z0-9][a-z0-9_-]{0,59}$/;

const repetidas = (valores) => valores.some((v, i) => valores.indexOf(v) !== i);

export const Sistemas = ({ estado }) => {
    const guardar = useGuardarConfiguracion();
    const original = estado.efectiva.proyectos;
    const [sistemas, setSistemas] = useState(original);
    const enUso = new Set(estado.proyectos_en_uso);
    const existentes = new Set(original.map((p) => p.clave));
    const claves = sistemas.map((p) => p.clave);
    const validos = sistemas.every((p) => CLAVE.test(p.clave) && p.nombre.trim()) && !repetidas(claves);
    const sinCambios = JSON.stringify(sistemas) === JSON.stringify(original);

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                guardar.mutate({ proyectos: sistemas });
            }}
        >
            <Encabezado titulo="Sistemas" descripcion="Agrupan las secciones en el inicio y el tablero, en este orden, y valen para todos los proyectos. Un sistema con secciones no se puede quitar." clave="proyectos" guardada={estado.guardada} />
            <ListaOrdenable
                titulo="Lista de sistemas"
                items={sistemas}
                onChange={setSistemas}
                nuevo={() => ({ clave: '', nombre: '' })}
                etiquetaNuevo="Agregar sistema"
                nombre="sistema"
                vacio="Sin sistemas: las secciones se agrupan por su clave tal cual."
                puedeQuitar={(p) => !enUso.has(p.clave)}
            >
                {(p, i, cambiar) => {
                    const fija = existentes.has(p.clave) && enUso.has(p.clave);
                    return (
                        <div className="grid gap-x-3 sm:grid-cols-2">
                            <TextField
                                id={`config-sistema-nombre-${i}`}
                                label="Nombre"
                                required
                                value={p.nombre}
                                onChange={(e) => cambiar({ nombre: e.target.value, clave: existentes.has(p.clave) ? p.clave : claveDesde(e.target.value) })}
                            />
                            <TextField
                                id={`config-sistema-clave-${i}`}
                                label="Clave"
                                tooltip={fija ? 'Hay secciones con esta clave; no se puede cambiar.' : 'La usan las secciones en su campo sistema.'}
                                required
                                disabled={fija}
                                value={p.clave}
                                error={p.clave && !CLAVE.test(p.clave) ? 'Minúsculas, números, - o _' : null}
                                onChange={(e) => cambiar({ ...p, clave: e.target.value })}
                            />
                        </div>
                    );
                }}
            </ListaOrdenable>
            {repetidas(claves) && <p className="mt-2 tipo-media text-xs text-error-fuerte">Hay claves repetidas</p>}
            <PieGuardar mutacion={guardar} deshabilitado={sinCambios || !validos} />
        </form>
    );
};

export const Cuentas = ({ estado }) => {
    const guardar = useGuardarConfiguracion();
    const original = estado.guardada.cuentas ?? estado.archivos.cuentas;
    const [cuentas, setCuentas] = useState(original);
    const validas = cuentas.every((c) => c.prefijo.trim() && c.descripcion.trim()) && !repetidas(cuentas.map((c) => c.prefijo.trim().toLowerCase()));
    const sinCambios = JSON.stringify(cuentas) === JSON.stringify(original);

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                guardar.mutate({ cuentas });
            }}
        >
            <Encabezado titulo="Cuentas de prueba" descripcion="Describen para qué sirve cada cuenta de prueba según el inicio de su correo. Gana el primer prefijo que coincida." clave="cuentas" guardada={estado.guardada} />
            <ListaOrdenable
                titulo="Descripciones"
                items={cuentas}
                onChange={setCuentas}
                nuevo={() => ({ prefijo: '', descripcion: '' })}
                etiquetaNuevo="Agregar descripción"
                nombre="cuenta"
                vacio="Sin descripciones: todas se muestran como «Cuenta de prueba»."
            >
                {(c, i, cambiar) => (
                    <div className="grid gap-x-3 sm:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
                        <TextField id={`config-cuenta-prefijo-${i}`} label="Prefijo del correo" required value={c.prefijo} onChange={(e) => cambiar({ ...c, prefijo: e.target.value })} />
                        <TextField id={`config-cuenta-descripcion-${i}`} label="Descripción" required value={c.descripcion} onChange={(e) => cambiar({ ...c, descripcion: e.target.value })} />
                    </div>
                )}
            </ListaOrdenable>
            <PieGuardar mutacion={guardar} deshabilitado={sinCambios || !validas} />
        </form>
    );
};
