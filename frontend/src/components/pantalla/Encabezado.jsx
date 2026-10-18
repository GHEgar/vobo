import { useState } from 'react';
import { useReloj } from '@/hooks/usePantalla';
import { PALETA } from '@/utils/pantalla/paleta';
import { hora } from '@/utils/pantalla/formato';

export const Logo = ({ marca, alto = 52 }) => {
    const [fallo, setFallo] = useState(false);
    if (!marca.logo || fallo) return null;
    return <img src={marca.logo} alt={marca.producto} onError={() => setFallo(true)} style={{ height: alto, width: 'auto' }} />;
};

export const EnVivo = ({ sinConexion }) => (
    <span className="flex items-center gap-3" style={{ fontSize: 24, color: PALETA.tenue }}>
        <span
            aria-hidden="true"
            className="rounded-full"
            style={{
                width: 14,
                height: 14,
                background: sinConexion ? PALETA.apagado : PALETA.vivo,
                boxShadow: sinConexion ? 'none' : '0 0 0 6px rgba(12, 163, 12, 0.18)',
            }}
        />
        {sinConexion ? 'Sin conexión' : 'En vivo'}
    </span>
);

export const Encabezado = ({ config, subtitulo, sinConexion }) => {
    const ahora = useReloj(5000);
    return (
        <header className="flex items-center justify-between px-[72px] pt-10">
            <div className="flex items-center gap-6">
                <Logo marca={config.marca} />
                <div className="flex items-baseline gap-5">
                    <span style={{ fontSize: 44, fontFamily: 'var(--tipo-negrita)', fontWeight: 700, letterSpacing: -0.5 }}>{config.nombre}</span>
                    <span style={{ fontSize: 28, color: PALETA.tenue }}>{subtitulo}</span>
                </div>
            </div>
            <div className="flex items-center gap-7">
                <EnVivo sinConexion={sinConexion} />
                <span style={{ fontSize: 56, fontFamily: 'var(--tipo-negrita)', fontWeight: 600, fontVariantNumeric: 'tabular-nums' }}>{hora(ahora)}</span>
            </div>
        </header>
    );
};
