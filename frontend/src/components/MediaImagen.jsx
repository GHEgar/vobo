import { useState } from 'react';

export const MediaImagen = ({ url, alt, className = '' }) => {
    const [fallo, setFallo] = useState(false);
    if (!url || fallo) return null;
    return <img src={url} alt={alt} loading="lazy" onError={() => setFallo(true)} className={className} />;
};
