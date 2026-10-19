import { useRef, useState } from 'react';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';
import { TextoConEnlaces } from '@/components/TextoConEnlaces';
import { useResponder } from '@/hooks/useValidacion';
import { formatearFecha } from '@/utils/formato';
import { describirEvento } from '@/utils/seguimiento';

const Evento = ({ evento, estados, burbuja }) => {
    if (evento.accion !== 'respuesta') {
        return (
            <li className="break-inside-avoid wrap-anywhere tipo-media text-xs text-texto-apagado">
                {describirEvento(evento, estados)} · {formatearFecha(evento.creado)}
            </li>
        );
    }
    return (
        <li className={`min-w-0 break-inside-avoid rounded-xl px-3 py-2 ${burbuja}`}>
            <p className="tipo-negrita text-xs text-texto">
                {evento.autor || evento.autor_email}
                <span className="tipo-media text-texto-apagado"> · {formatearFecha(evento.creado)}</span>
            </p>
            <p className="mt-0.5 whitespace-pre-line wrap-anywhere tipo-regular text-sm text-texto"><TextoConEnlaces texto={evento.texto} /></p>
        </li>
    );
};

export const Seguimiento = ({ objeto, id, eventos = [], estados, editable = false, burbuja = 'bg-fondo' }) => {
    const responder = useResponder(objeto);
    const [texto, setTexto] = useState('');
    const [abierto, setAbierto] = useState(false);
    const boton = useRef(null);
    const campo = `respuesta-${objeto}-${id}`;
    const cerrar = () => {
        setTexto('');
        setAbierto(false);
        requestAnimationFrame(() => boton.current?.focus());
    };
    const abrir = () => {
        setAbierto(true);
        requestAnimationFrame(() => document.getElementById(campo)?.focus());
    };
    const enviar = (e) => {
        e.preventDefault();
        responder.mutate({ id, texto: texto.trim() }, { onSuccess: cerrar });
    };

    if (!eventos.length && !editable) return null;
    return (
        <section aria-label="Seguimiento" className="mt-4 min-w-0 border-t border-borde pt-3">
            <p className="tipo-negrita text-xs text-texto-tenue">Seguimiento</p>
            {eventos.length > 0 ? (
                <ol className="mt-2 flex flex-col gap-2">
                    {eventos.map((e) => <Evento key={e.id} evento={e} estados={estados} burbuja={burbuja} />)}
                </ol>
            ) : (
                <p className="mt-1 tipo-media text-xs text-texto-apagado">Sin respuestas ni cambios todavía.</p>
            )}
            {editable && !abierto && (
                <div className="mt-3 print:hidden">
                    <Button ref={boton} label="Responder" variant="ghost" small onClick={abrir} />
                </div>
            )}
            {editable && abierto && (
                <form onSubmit={enviar} className="flex flex-col gap-2 print:hidden">
                    <TextField id={campo} label="Respuesta" tooltip="Le llega en sus avisos a quien lo escribió." multiline rows={3} maxLength={4000} value={texto} onChange={(e) => setTexto(e.target.value)} />
                    <div className="flex flex-wrap justify-end gap-2">
                        <Button label="Cancelar" variant="secondary" small onClick={cerrar} />
                        <Button type="submit" label="Enviar" variant="outline" small disabled={!texto.trim()} loading={responder.isPending} />
                    </div>
                </form>
            )}
            {responder.error && <p className="mt-2 tipo-media text-xs text-error-fuerte">{responder.error.message}</p>}
        </section>
    );
};
