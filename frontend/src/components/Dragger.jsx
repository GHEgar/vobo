import { useEffect, useId, useMemo, useState } from 'react';
import { Close } from 'tesela/react';
import { IconoSubir } from '@/components/Iconos';
import { Label } from '@/components/Label';

const TIPOS = ['image/png', 'image/jpeg', 'image/gif', 'image/webp'];

export const Dragger = ({ label, tooltip, archivos, onChange, maxMB = 5, maxArchivos = 5 }) => {
    const id = useId();
    const [error, setError] = useState('');
    const [arrastrando, setArrastrando] = useState(false);
    const vistas = useMemo(() => archivos.map((a) => ({ archivo: a, url: URL.createObjectURL(a) })), [archivos]);

    useEffect(() => () => vistas.forEach((v) => URL.revokeObjectURL(v.url)), [vistas]);

    const agregar = (lista) => {
        const nuevos = Array.from(lista);
        const invalidos = nuevos.filter((a) => !TIPOS.includes(a.type)).map((a) => a.name);
        const pesados = nuevos.filter((a) => a.size > maxMB * 1024 * 1024).map((a) => a.name);
        const validos = nuevos.filter((a) => TIPOS.includes(a.type) && a.size <= maxMB * 1024 * 1024);
        const total = [...archivos, ...validos].slice(0, maxArchivos);
        const mensajes = [];
        if (invalidos.length) mensajes.push(`No son imágenes: ${invalidos.join(', ')}`);
        if (pesados.length) mensajes.push(`Pesan más de ${maxMB} MB: ${pesados.join(', ')}`);
        if (archivos.length + validos.length > maxArchivos) mensajes.push(`Máximo ${maxArchivos} imágenes`);
        setError(mensajes.join('. '));
        onChange(total);
    };

    return (
        <div className="mt-4">
            <Label htmlFor={id} text={label} tooltip={tooltip} />
            <label
                htmlFor={id}
                onDragOver={(e) => {
                    e.preventDefault();
                    setArrastrando(true);
                }}
                onDragLeave={() => setArrastrando(false)}
                onDrop={(e) => {
                    e.preventDefault();
                    setArrastrando(false);
                    agregar(e.dataTransfer.files);
                }}
                className={`mt-3 flex w-full cursor-pointer items-center gap-6 rounded-2xl border border-dashed border-primario px-6 py-5 hover:bg-fondo md:gap-10 md:px-8 ${arrastrando ? 'bg-primario-suave' : 'bg-white'}`}
            >
                <IconoSubir className="h-12 w-12 shrink-0" />
                <span className="tipo-negrita text-lg/6 text-primario">
                    Sube tus capturas
                    <span className="block tipo-media text-xs text-texto-tenue">
                        Da clic o arrastra las imágenes dentro de este recuadro (PNG, JPG o WebP, hasta {maxMB} MB)
                    </span>
                </span>
                <input
                    id={id}
                    type="file"
                    accept={TIPOS.join(',')}
                    multiple
                    className="hidden"
                    onChange={(e) => {
                        agregar(e.target.files);
                        e.target.value = '';
                    }}
                />
            </label>
            {error && <p className="mt-1 tipo-media text-xs text-error-fuerte">{error}</p>}
            {vistas.length > 0 && (
                <ul className="mt-3 flex flex-wrap gap-3">
                    {vistas.map((v, i) => (
                        <li key={v.url} className="relative">
                            <img src={v.url} alt={v.archivo.name} className="h-20 w-20 rounded-lg object-cover" />
                            <button
                                type="button"
                                aria-label={`Quitar ${v.archivo.name}`}
                                onClick={() => onChange(archivos.filter((_, j) => j !== i))}
                                className="absolute -top-2 -right-2 flex h-6 w-6 items-center justify-center rounded-full bg-white text-error shadow"
                            >
                                <Close size={12} stroke={2.5} />
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};
