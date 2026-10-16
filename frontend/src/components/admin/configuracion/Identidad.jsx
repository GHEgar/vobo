import { useState } from 'react';
import { TextField } from '@/components/Field';
import { useGuardarConfiguracion } from '@/hooks/useAdmin';
import { Encabezado, PieGuardar, Restablecer } from '@/components/admin/configuracion/Comun';
import { cambiados } from '@/utils/configuracion';

const inicial = ({ efectiva }) => ({
    producto: efectiva.producto,
    nombre: efectiva.nombre,
    descripcion: efectiva.descripcion,
    entrada: { titulo: efectiva.entrada.titulo, mensaje: efectiva.entrada.mensaje },
});

const Campo = ({ clave, guardada, ...rest }) => (
    <div className="relative">
        <TextField {...rest} />
        <div className="absolute top-3 right-0">
            <Restablecer clave={clave} guardada={guardada} />
        </div>
    </div>
);

export const Identidad = ({ estado }) => {
    const guardar = useGuardarConfiguracion();
    const original = inicial(estado);
    const [borrador, setBorrador] = useState(original);
    const cambios = cambiados(borrador, original);
    const fijar = (clave) => (e) => setBorrador({ ...borrador, [clave]: e.target.value });
    const fijarEntrada = (clave) => (e) => setBorrador({ ...borrador, entrada: { ...borrador.entrada, [clave]: e.target.value } });
    const { guardada } = estado;

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                guardar.mutate(cambios);
            }}
        >
            <Encabezado titulo="Identidad" descripcion="Cómo se llama la instancia y qué ve la gente en la pantalla de entrada." guardada={guardada} />
            <Campo id="config-producto" clave="producto" guardada={guardada} label="Producto" required tooltip="Nombre corto que aparece en la cabecera cuando no hay logo y en la pestaña del navegador." value={borrador.producto} onChange={fijar('producto')} />
            <Campo id="config-nombre" clave="nombre" guardada={guardada} label="Nombre de la instancia" tooltip="Se muestra junto a la marca en la cabecera." value={borrador.nombre} onChange={fijar('nombre')} />
            <Campo id="config-descripcion" clave="descripcion" guardada={guardada} label="Descripción" multiline rows={2} value={borrador.descripcion} onChange={fijar('descripcion')} />
            <div className="mt-6">
                <Encabezado titulo="Pantalla de entrada" clave="entrada" guardada={guardada} />
                <TextField id="config-entrada-titulo" label="Título" value={borrador.entrada.titulo} onChange={fijarEntrada('titulo')} />
                <TextField id="config-entrada-mensaje" label="Mensaje" multiline rows={3} value={borrador.entrada.mensaje} onChange={fijarEntrada('mensaje')} />
            </div>
            <PieGuardar mutacion={guardar} deshabilitado={!Object.keys(cambios).length || !borrador.producto.trim()} />
        </form>
    );
};
