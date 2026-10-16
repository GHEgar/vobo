import { useState } from 'react';
import { Button } from '@/components/Button';
import { Dragger } from '@/components/Dragger';
import { TextField } from '@/components/Field';
import { useGuardarConfiguracion, useQuitarMarca, useSubirMarca } from '@/hooks/useAdmin';
import { tamanoLegible } from '@/utils/editor';
import { COLOR_HEX } from '@/utils/estilos';
import { Encabezado, Origen, PieGuardar } from '@/components/admin/configuracion/Comun';

const TIPOS = ['image/png', 'image/svg+xml', 'image/webp'];

const RANURAS = [
    { ranura: 'logo_claro', titulo: 'Logo', descripcion: 'Va en la cabecera y en la pantalla de entrada, sobre fondo claro.', fondo: 'bg-white' },
    { ranura: 'logo_oscuro', titulo: 'Logo para fondo oscuro', descripcion: 'Si no lo subes se usa el logo claro.', fondo: 'bg-texto' },
    { ranura: 'favicon', titulo: 'Ícono de la pestaña', descripcion: 'Cuadrado; SVG o PNG de al menos 64 px.', fondo: 'bg-white' },
];

const urlActual = (efectiva, ranura) => {
    if (ranura === 'favicon') return efectiva.favicon;
    if (!efectiva.logo) return '';
    return ranura === 'logo_claro' ? efectiva.logo.claro : efectiva.logo.oscuro;
};

const Ranura = ({ ranura, titulo, descripcion, fondo, estado }) => {
    const subir = useSubirMarca();
    const quitar = useQuitarMarca();
    const [archivos, setArchivos] = useState([]);
    const subido = estado.marca[ranura];
    const url = urlActual(estado.efectiva, ranura);
    const error = subir.error ?? quitar.error;

    return (
        <section className="mt-6 rounded-2xl bg-fondo p-4">
            <Encabezado titulo={titulo} descripcion={descripcion} guardada={{}}>
                {subido && <Button label="Quitar" small variant="enlaceRojo" loading={quitar.isPending} onClick={() => quitar.mutate(ranura)} />}
            </Encabezado>
            <Origen guardado={Boolean(subido)} />
            <div className={`mt-3 flex h-20 items-center justify-center rounded-xl border border-borde px-4 ${fondo}`}>
                {url ? <img src={url} alt={`${titulo} actual`} className="max-h-14 w-auto max-w-full object-contain" /> : <span className="tipo-media text-xs text-texto-apagado">Sin imagen; se muestra el nombre del producto</span>}
            </div>
            {subido && <p className="mt-2 tipo-media text-[11px] text-texto-apagado">{subido.archivo} · {tamanoLegible(subido.tamano)}</p>}
            <Dragger
                label={subido ? 'Reemplazar' : 'Subir'}
                archivos={archivos}
                onChange={setArchivos}
                maxMB={2}
                maxArchivos={1}
                tipos={TIPOS}
                titulo={subido ? 'Reemplaza la imagen' : 'Sube la imagen'}
                ayuda="PNG, SVG o WebP, hasta {maxMB} MB."
                sustantivo="imágenes PNG, SVG o WebP"
            />
            {error && <p role="alert" className="mt-2 tipo-media text-xs text-error-fuerte">{error.message}</p>}
            {archivos.length > 0 && (
                <div className="mt-3 flex justify-end">
                    <Button label="Guardar imagen" loading={subir.isPending} onClick={() => subir.mutate({ ranura, archivo: archivos[0] }, { onSuccess: () => setArchivos([]) })} />
                </div>
            )}
        </section>
    );
};

const ColorNavegador = ({ estado }) => {
    const guardar = useGuardarConfiguracion();
    const { efectiva, guardada } = estado;
    const [alt, setAlt] = useState(efectiva.logo?.alt ?? '');
    const [color, setColor] = useState(efectiva.color_tema);
    const valido = COLOR_HEX.test(color);
    const cambios = {
        ...(alt.trim() !== (efectiva.logo?.alt ?? '') ? { logo_alt: alt } : {}),
        ...(valido && color.toUpperCase() !== efectiva.color_tema ? { color_tema: color } : {}),
    };

    return (
        <form
            className="mt-6"
            onSubmit={(e) => {
                e.preventDefault();
                guardar.mutate(cambios);
            }}
        >
            <Encabezado titulo="Texto alternativo del logo" clave="logo_alt" guardada={guardada} />
            <TextField id="config-logo-alt" label="Texto alternativo" tooltip="Lo leen los lectores de pantalla en lugar del logo." value={alt} onChange={(e) => setAlt(e.target.value)} />
            <div className="mt-6">
                <Encabezado titulo="Color del navegador" descripcion="Tiñe la barra del navegador en móviles." clave="color_tema" guardada={guardada} />
                <div className="mt-3 flex flex-wrap items-center gap-3">
                    <input type="color" aria-label="Color del navegador" value={valido ? color : '#000000'} onChange={(e) => setColor(e.target.value.toUpperCase())} className="h-10 w-14 cursor-pointer rounded-lg border border-borde bg-white p-1" />
                    <input aria-label="Color del navegador en hexadecimal" value={color} onChange={(e) => setColor(e.target.value)} className="h-10 w-28 rounded-lg border border-borde bg-white px-3 tipo-media text-[13px] text-texto" />
                    <div aria-hidden="true" style={{ '--color-vista': valido ? color : 'transparent' }} className="flex h-10 w-48 items-center gap-2 rounded-lg bg-[var(--color-vista)] px-3">
                        <span className="h-2 w-2 rounded-full bg-white" />
                        <span className="h-2 flex-1 rounded-full bg-white/70" />
                    </div>
                </div>
                {!valido && <p className="mt-1 tipo-media text-xs text-error-fuerte">Usa el formato #RRGGBB</p>}
            </div>
            <PieGuardar mutacion={guardar} deshabilitado={!Object.keys(cambios).length || !valido} />
        </form>
    );
};

export const Marca = ({ estado }) => (
    <>
        <Encabezado titulo="Marca" descripcion="Imágenes que reemplazan a las del tema de archivos. Quitar una vuelve a la del tema." guardada={{}} />
        {RANURAS.map((r) => <Ranura key={r.ranura} {...r} estado={estado} />)}
        <ColorNavegador key={`${estado.efectiva.color_tema}-${estado.efectiva.logo?.alt ?? ''}`} estado={estado} />
    </>
);
