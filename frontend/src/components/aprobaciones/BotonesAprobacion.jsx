import { useState } from 'react';
import { Button } from '@/components/Button';

const CAMPO = 'h-[36px] w-full rounded-[8px] border border-transparent bg-fondo px-3 tipo-media text-[13px] text-primario placeholder-texto-placeholder focus:bg-white focus:outline-none focus:ring-1 focus:ring-primario';

export const BotonesAprobacion = ({ id, etiqueta, onDecidir, guardando, small = false }) => {
    const [comentario, setComentario] = useState('');
    const [conComentario, setConComentario] = useState(false);
    const decidir = (estado) => {
        onDecidir(estado, comentario.trim());
        setComentario('');
        setConComentario(false);
    };
    return (
        <div className="flex flex-col gap-2">
            {conComentario && (
                <input
                    id={id}
                    aria-label={`Comentario para ${etiqueta}`}
                    placeholder="Comentario (opcional)"
                    maxLength={2000}
                    value={comentario}
                    onChange={(e) => setComentario(e.target.value)}
                    className={CAMPO}
                />
            )}
            <div className="flex flex-wrap items-center gap-2">
                <Button label="Aprobar" variant="success" small={small} disabled={guardando} onClick={() => decidir('aprobada')} aria-label={`Aprobar ${etiqueta}`} />
                <Button label="Rechazar" variant="danger" small={small} disabled={guardando} onClick={() => decidir('rechazada')} aria-label={`Rechazar ${etiqueta}`} />
                {!conComentario && <Button label="Comentario" variant="link" small onClick={() => setConComentario(true)} />}
            </div>
        </div>
    );
};
