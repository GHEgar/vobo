import { useState } from 'react';
import { Button } from '@/components/Button';
import { TextField } from '@/components/Field';
import { Modal } from '@/components/Modal';
import { useCrearAviso } from '@/hooks/useAvisos';

const PLANTILLAS = {
    cerrada: (falla) => {
        const nota = falla.nota_resolucion?.trim();
        return {
            titulo: '',
            mensaje: `Tu reporte de ${falla.caso_id} ya fue atendido.${nota ? `\n\nNota de resolución: ${nota}` : ''}`,
        };
    },
    lista_para_revalidar: (falla) => ({
        titulo: `Ya puedes volver a probar ${falla.caso_id}`,
        mensaje: `Ya puedes volver a probar ${falla.caso_id}.`,
    }),
    en_curso: (falla) => ({
        titulo: `Estamos trabajando en tu reporte de ${falla.caso_id}`,
        mensaje: `Estamos trabajando en tu reporte de ${falla.caso_id}.`,
    }),
};

const plantillaAviso = (falla) => PLANTILLAS[falla.estado]?.(falla) ?? { titulo: '', mensaje: '' };

const Formulario = ({ falla, onCerrar, onEnviado }) => {
    const crear = useCrearAviso();
    const [inicial] = useState(() => plantillaAviso(falla));
    const [titulo, setTitulo] = useState(inicial.titulo);
    const [mensaje, setMensaje] = useState(inicial.mensaje);

    const enviar = (e) => {
        e.preventDefault();
        crear.mutate(
            { falla_id: falla.id, titulo: titulo.trim() || null, mensaje: mensaje.trim() },
            { onSuccess: () => onEnviado() },
        );
    };

    return (
        <form onSubmit={enviar} className="flex flex-col gap-2">
            <p className="tipo-media text-sm text-texto-tenue">
                Le llegará a <span className="tipo-negrita text-texto">{falla.usuario_email}</span> en su buzón de avisos, con enlace al caso {falla.caso_id}.
            </p>
            <TextField
                id={`aviso-falla-titulo-${falla.id}`}
                label="Título"
                tooltip={`Opcional. Si lo dejas vacío se usa «Tu reporte de ${falla.caso_id} fue atendido».`}
                maxLength={200}
                value={titulo}
                onChange={(e) => setTitulo(e.target.value)}
            />
            <TextField
                id={`aviso-falla-mensaje-${falla.id}`}
                label="Mensaje"
                required
                multiline
                rows={5}
                maxLength={2000}
                value={mensaje}
                onChange={(e) => setMensaje(e.target.value)}
            />
            {crear.error && <p className="tipo-media text-xs text-error-fuerte">{crear.error.message}</p>}
            <div className="mt-4 flex justify-end gap-3">
                <Button label="Cancelar" variant="secondary" onClick={onCerrar} />
                <Button type="submit" label="Enviar aviso" disabled={!mensaje.trim()} loading={crear.isPending} />
            </div>
        </form>
    );
};

export const AvisarFalla = ({ falla }) => {
    const [abierto, setAbierto] = useState(false);
    const [enviado, setEnviado] = useState(false);

    return (
        <>
            <div className="flex flex-wrap items-center gap-3">
                <Button label="Avisar a quien reportó" variant="ghost" small onClick={() => { setEnviado(false); setAbierto(true); }} />
                <p role="status" className="tipo-media text-xs text-pasa">{enviado ? `Aviso enviado a ${falla.usuario_email}.` : ''}</p>
            </div>
            <Modal abierto={abierto} titulo={`Avisar sobre ${falla.caso_id}`} onCerrar={() => setAbierto(false)}>
                {abierto && (
                    <Formulario
                        falla={falla}
                        onCerrar={() => setAbierto(false)}
                        onEnviado={() => {
                            setAbierto(false);
                            setEnviado(true);
                        }}
                    />
                )}
            </Modal>
        </>
    );
};
