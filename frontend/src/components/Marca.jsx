import { useState } from 'react';
import { useInstancia } from '@/hooks/useInstancia';

const ALTO = { cabecera: 'h-8 md:h-10', entrada: 'h-10', impresion: 'h-9' };

const TEXTO = {
    cabecera: 'text-lg sm:text-xl md:text-2xl',
    entrada: 'text-2xl',
    impresion: 'text-xl',
};

const Logo = ({ logo, alto, onError }) => (
    <img src={logo.claro} alt={logo.alt} onError={onError} className={`${alto} w-auto max-w-full object-contain object-left`} />
);

export const Marca = ({ variante = 'cabecera' }) => {
    const { producto, logo } = useInstancia();
    const [fallida, setFallida] = useState(null);
    const clave = logo?.claro ?? '';
    if (logo && fallida !== clave) {
        return <Logo logo={logo} alto={ALTO[variante]} onError={() => setFallida(clave)} />;
    }
    return <span className={`tipo-negrita leading-none text-primario ${TEXTO[variante]}`}>{producto}</span>;
};
