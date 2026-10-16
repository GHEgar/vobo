import { useState } from 'react';

const VIDEO = /\.(mp4|webm)(\?|$)/i;

const esVideo = (url, tipo = '') => tipo.startsWith('video/') || VIDEO.test(url ?? '');

export const MediaImagen = ({ url, alt, className = '', carga = 'lazy', tipo }) => {
    const [fallo, setFallo] = useState(false);
    if (!url || fallo) return null;
    if (esVideo(url, tipo)) {
        return <video src={url} aria-label={alt} autoPlay loop muted playsInline preload={carga === 'lazy' ? 'metadata' : 'auto'} onError={() => setFallo(true)} className={className} />;
    }
    return <img src={url} alt={alt} loading={carga} onError={() => setFallo(true)} className={className} />;
};
