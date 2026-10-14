import { useState } from 'react';
import { Button } from '@/components/Button';
import { Checkbox } from '@/components/Checkbox';
import { TextField } from '@/components/Field';
import { Modal } from '@/components/Modal';

const correosDe = (texto) => [...new Set(
    texto.split(/[\s,;]+/).map((c) => c.trim().toLowerCase()).filter((c) => /^[^@\s]+@[^@\s]+$/.test(c)),
)];

export const AgregarPersonas = ({ abierto, onCerrar, conocidos, onAgregar }) => {
    const [texto, setTexto] = useState('');
    const [elegidos, setElegidos] = useState([]);
    const escritos = correosDe(texto);
    const total = new Set([...escritos, ...elegidos]);

    const cerrar = () => {
        setTexto('');
        setElegidos([]);
        onCerrar();
    };

    const alternar = (email, marcado) => setElegidos(marcado ? [...elegidos, email] : elegidos.filter((e) => e !== email));

    return (
        <Modal abierto={abierto} titulo="Agregar personas" onCerrar={cerrar}>
            <p className="tipo-media text-sm text-texto-tenue">Se agregan con todas las secciones marcadas; luego puedes quitarles las que no les tocan.</p>
            <TextField
                id="correos-nuevos"
                label="Correos"
                tooltip="Uno o varios, separados por coma, espacio o renglón. Tal como aparecen en el proveedor de identidad."
                placeholder="persona@ejemplo.org, otra@ejemplo.org"
                multiline
                rows={2}
                value={texto}
                onChange={(e) => setTexto(e.target.value)}
            />
            {conocidos.length > 0 && (
                <fieldset className="flex flex-col gap-2">
                    <legend className="mb-2 tipo-media text-sm text-texto">Personas que ya entraron</legend>
                    <div className="rounded-xl bg-fondo px-4 py-3">
                        <Checkbox
                            id="conocidos-todas"
                            checked={elegidos.length === conocidos.length}
                            indeterminado={elegidos.length > 0 && elegidos.length < conocidos.length}
                            onChange={() => setElegidos(elegidos.length === conocidos.length ? [] : conocidos.map((u) => u.email))}
                        >
                            Todas
                        </Checkbox>
                    </div>
                    <ul className="flex max-h-[40dvh] flex-col gap-2 overflow-y-auto px-4">
                        {conocidos.map((u) => (
                            <li key={u.email}>
                                <Checkbox id={`conocido-${u.email}`} checked={elegidos.includes(u.email)} onChange={(marcado) => alternar(u.email, marcado)}>
                                    {u.nombre} <span className="text-xs text-texto-apagado">{u.email}</span>
                                </Checkbox>
                            </li>
                        ))}
                    </ul>
                </fieldset>
            )}
            <div className="flex justify-end gap-3">
                <Button label="Cancelar" variant="secondary" onClick={cerrar} />
                <Button
                    label={total.size ? `Agregar (${total.size})` : 'Agregar'}
                    disabled={!total.size}
                    onClick={() => {
                        onAgregar([...total]);
                        cerrar();
                    }}
                />
            </div>
        </Modal>
    );
};
