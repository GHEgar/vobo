import { useEscala } from '@/hooks/usePantalla';
import { ALTO, ANCHO, PALETA } from '@/utils/pantalla/paleta';

export const Escalado = ({ cursorOculto, children }) => {
    const escala = useEscala();
    return (
        <div className="fixed inset-0 overflow-hidden" style={{ background: PALETA.fondoGrafo, cursor: cursorOculto ? 'none' : 'default' }}>
            <div
                className="absolute left-1/2 top-1/2 overflow-hidden"
                style={{
                    width: ANCHO,
                    height: ALTO,
                    transform: `translate(-50%, -50%) scale(${escala})`,
                    transformOrigin: 'center center',
                    background: PALETA.fondo,
                    color: PALETA.texto,
                    fontFamily: 'var(--tipo-media)',
                }}
            >
                {children}
            </div>
        </div>
    );
};

export const Indicador = ({ vistas, actual, sinConexion }) => (
    <div className="pointer-events-none absolute top-3 left-1/2 flex -translate-x-1/2 items-center gap-3" style={{ fontSize: 16, color: PALETA.apagado }}>
        {vistas.length > 1 && vistas.map((vista, i) => (
            <span
                key={vista}
                aria-hidden="true"
                className="rounded-full transition-all duration-500"
                style={{ width: i === actual ? 28 : 8, height: 8, background: i === actual ? PALETA.medio : PALETA.pista }}
            />
        ))}
        {sinConexion && (
            <span role="status" className="flex items-center gap-2">
                <span aria-hidden="true" className="rounded-full" style={{ width: 8, height: 8, background: PALETA.apagado }} />
                sin conexión
            </span>
        )}
    </div>
);

export const Mensaje = ({ titulo, detalle }) => (
    <div className="flex h-full flex-col items-center justify-center gap-6 text-center">
        <span style={{ fontSize: 56, fontFamily: 'var(--tipo-negrita)', fontWeight: 700 }}>{titulo}</span>
        {detalle && <span style={{ fontSize: 28, color: PALETA.tenue }}>{detalle}</span>}
    </div>
);
