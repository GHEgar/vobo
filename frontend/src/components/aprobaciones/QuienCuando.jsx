import { formatearFecha } from '@/utils/formato';

export const QuienCuando = ({ registro, prefijo }) => {
    if (!registro) return null;
    return (
        <p className="wrap-anywhere tipo-media text-[11px] text-texto-apagado" title={registro.comentario || undefined}>
            {prefijo ? `${prefijo} · ` : ''}{registro.usuario_nombre || registro.usuario_email} · {formatearFecha(registro.creada)}
            {registro.comentario && <span className="text-texto-tenue"> · «{registro.comentario}»</span>}
        </p>
    );
};
