import { useState } from 'react';
import { Button } from '@/components/Button';
import { Checkbox } from '@/components/Checkbox';
import { TextField } from '@/components/Field';
import { Modal } from '@/components/Modal';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { useCrearAviso, usePersonasAviso } from '@/hooks/useAvisos';

const MAXIMO = 50;

const coincide = (persona, filtro) => {
    const texto = filtro.trim().toLowerCase();
    return !texto || persona.nombre.toLowerCase().includes(texto) || persona.email.toLowerCase().includes(texto);
};

const Formulario = ({ onCerrar, onEnviado }) => {
    const personas = usePersonasAviso();
    const crear = useCrearAviso();
    const [filtro, setFiltro] = useState('');
    const [elegidos, setElegidos] = useState([]);
    const [titulo, setTitulo] = useState('');
    const [mensaje, setMensaje] = useState('');
    const visibles = (personas.data ?? []).filter((p) => coincide(p, filtro));

    const alternar = (email, marcado) => setElegidos(marcado ? [...elegidos, email] : elegidos.filter((e) => e !== email));

    const enviar = (e) => {
        e.preventDefault();
        crear.mutate(
            { destinatarios: elegidos, titulo: titulo.trim() || null, mensaje: mensaje.trim() },
            {
                onSuccess: (avisos) => {
                    onEnviado?.(avisos.length);
                    onCerrar();
                },
            },
        );
    };

    const listo = elegidos.length > 0 && elegidos.length <= MAXIMO && mensaje.trim().length > 0;

    return (
        <form onSubmit={enviar} className="flex flex-col gap-2">
            <fieldset className="flex flex-col gap-2">
                <legend className="mb-2 tipo-media text-sm text-texto">
                    Para quién {elegidos.length > 0 && <span className="text-texto-apagado">({elegidos.length} de {MAXIMO} como máximo)</span>}
                </legend>
                <TextField id="aviso-filtro" label="Buscar persona" placeholder="Nombre o correo" value={filtro} onChange={(e) => setFiltro(e.target.value)} />
                {personas.isPending && <Spinner />}
                {personas.error && <ErrorState mensaje={personas.error.message} onReintentar={personas.refetch} />}
                {personas.data && (
                    <ul className="mt-2 flex max-h-[30dvh] flex-col gap-2 overflow-y-auto rounded-xl bg-fondo px-4 py-3">
                        {!visibles.length && <li className="tipo-media text-sm text-texto-tenue">Nadie coincide con la búsqueda.</li>}
                        {visibles.map((p) => (
                            <li key={p.email}>
                                <Checkbox id={`aviso-persona-${p.email}`} checked={elegidos.includes(p.email)} onChange={(marcado) => alternar(p.email, marcado)}>
                                    {p.nombre} <span className="text-xs text-texto-apagado">{p.email}</span>
                                </Checkbox>
                            </li>
                        ))}
                    </ul>
                )}
            </fieldset>
            <TextField id="aviso-titulo" label="Título" tooltip="Opcional. Si lo dejas vacío se usa «Aviso de coordinación»." maxLength={200} value={titulo} onChange={(e) => setTitulo(e.target.value)} />
            <TextField id="aviso-mensaje" label="Mensaje" required multiline rows={5} maxLength={2000} value={mensaje} onChange={(e) => setMensaje(e.target.value)} />
            {crear.error && <p className="tipo-media text-xs text-error-fuerte">{crear.error.message}</p>}
            <div className="mt-4 flex justify-end gap-3">
                <Button label="Cancelar" variant="secondary" onClick={onCerrar} />
                <Button type="submit" label={elegidos.length > 1 ? `Enviar (${elegidos.length})` : 'Enviar'} disabled={!listo} loading={crear.isPending} />
            </div>
        </form>
    );
};

export const NuevoAviso = ({ abierto, onCerrar, onEnviado }) => (
    <Modal abierto={abierto} titulo="Nuevo aviso" onCerrar={onCerrar}>
        {abierto && <Formulario onCerrar={onCerrar} onEnviado={onEnviado} />}
    </Modal>
);
