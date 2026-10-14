import { useState } from 'react';
import { BotonMas } from '@/components/BotonMas';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { TextField } from '@/components/Field';
import { Tarjeta, Titulo } from '@/components/Tarjeta';
import { AsignacionesEditor } from '@/components/rondas/AsignacionesEditor';
import { FilaRonda } from '@/components/rondas/FilaRonda';
import { QuienVeQue } from '@/components/rondas/QuienVeQue';
import { useRonda } from '@/hooks/useRonda';
import { useCrearRonda } from '@/hooks/useValidacion';

const NuevaRonda = ({ onCreada }) => {
    const crear = useCrearRonda();
    const { elegirRonda } = useRonda();
    const [nombre, setNombre] = useState('');
    const [snapshot, setSnapshot] = useState('');

    const enviar = async (e) => {
        e.preventDefault();
        const ronda = await crear.mutateAsync({ nombre: nombre.trim(), snapshot: snapshot.trim() });
        elegirRonda(ronda.id);
        setNombre('');
        setSnapshot('');
        onCreada();
    };

    return (
        <form onSubmit={enviar} className="flex flex-col">
            <TextField id="ronda-nombre" label="Nombre" placeholder="Ronda 1" required value={nombre} onChange={(e) => setNombre(e.target.value)} />
            <TextField id="ronda-snapshot" label="Snapshot del entorno" tooltip="Nombre del snapshot desde el que se restauró el entorno de prueba para esta ronda." placeholder="entorno-2026-10-08" value={snapshot} onChange={(e) => setSnapshot(e.target.value)} />
            {crear.error && <p className="mt-3 tipo-media text-xs text-error-fuerte">{crear.error.message}</p>}
            <div className="mt-6 flex justify-end">
                <Button label="Abrir ronda" type="submit" disabled={!nombre.trim()} loading={crear.isPending} />
            </div>
        </form>
    );
};

const Rondas = () => {
    const { rondas, ronda } = useRonda();
    const [modal, setModal] = useState(null);
    const cerrar = () => setModal(null);

    return (
        <>
            <Tarjeta>
                <Titulo
                    accion={(
                        <div className="flex items-center gap-2">
                            <Button label="Quién ve qué" small variant="ghost" onClick={() => setModal('acceso')} />
                            <BotonMas etiqueta="Nueva ronda" ayuda="Abrir una ronda nueva cada vez que se restaura el entorno de prueba" onClick={() => setModal('ronda')} />
                        </div>
                    )}
                >
                    Rondas
                </Titulo>
                <ul className="flex flex-col gap-2">
                    {rondas.map((r) => <FilaRonda key={r.id} ronda={r} />)}
                </ul>
            </Tarjeta>
            {ronda && (
                <Tarjeta>
                    <AsignacionesEditor ronda={ronda} />
                </Tarjeta>
            )}
            <Modal abierto={modal === 'ronda'} titulo="Nueva ronda" onCerrar={cerrar} ancho="max-w-lg">
                <NuevaRonda onCreada={cerrar} />
            </Modal>
            <Modal abierto={modal === 'acceso'} titulo="Quién ve qué" onCerrar={cerrar} ancho="max-w-5xl">
                <p className="tipo-media text-sm text-texto-tenue">
                    Inicio lo ve todo el equipo. Lo que da el rol de cada persona aparece marcado; lo que marques aquí es solo de lectura.
                </p>
                <QuienVeQue />
            </Modal>
        </>
    );
};

export default Rondas;
