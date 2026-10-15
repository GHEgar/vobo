import { useState } from 'react';

export const MediaImagen = ({ url, alt, className = '', carga = 'lazy' }) => {
    const [fallo, setFallo] = useState(false);
    if (!url || fallo) return null;
    return <img src={url} alt={alt} loading={carga} onError={() => setFallo(true)} className={className} />;
};
