import { useState } from 'react';
import { Eye, EyeOff } from 'tesela/react';
import { BotonCopiar } from '@/components/BotonCopiar';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { useRonda } from '@/hooks/useRonda';
import { useCuentasPrueba } from '@/hooks/useValidacion';
import { localDeCuenta } from '@/utils/cuentas';

const FilaCuenta = ({ cuenta, resaltada }) => {
    const [visible, setVisible] = useState(false);
    return (
        <li className={`flex flex-col gap-2 rounded-2xl px-4 py-3 md:flex-row md:items-center md:justify-between ${resaltada ? 'bg-primario-claro ring-1 ring-primario' : 'bg-fondo'}`}>
            <div className="min-w-0">
                <p className="truncate tipo-negrita text-sm text-texto">
                    {cuenta.email}
                    {resaltada && <span className="ml-2 tipo-media text-xs text-primario">· para este caso</span>}
                </p>
                <p className="tipo-media text-xs text-texto-tenue">{cuenta.descripcion}</p>
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1">
                <BotonCopiar texto={cuenta.email} etiqueta="Copiar correo" descripcion={`Copiar el correo ${cuenta.email}`} />
                <span className="tipo-media text-sm tracking-wide text-texto" aria-label={visible ? 'Contraseña' : 'Contraseña oculta'}>
                    {visible ? cuenta.password : '••••••'}
                </span>
                <button
                    type="button"
                    onClick={() => setVisible(!visible)}
                    aria-pressed={visible}
                    className="inline-flex items-center gap-1 bg-transparent p-0 tipo-negrita text-xs text-texto-tenue underline underline-offset-4 hover:text-primario"
                >
                    {visible ? <EyeOff size={14} stroke={2} /> : <Eye size={14} stroke={2} />}
                    {visible ? 'Ocultar' : 'Mostrar'}
                </button>
                <BotonCopiar texto={cuenta.password} etiqueta="Copiar contraseña" descripcion={`Copiar la contraseña de ${cuenta.email}`} />
            </div>
        </li>
    );
};

export const ModalCuentasPrueba = ({ abierto, onCerrar, cuentas, resaltar = '' }) => {
    const texto = resaltar.toLowerCase();
    const esDelCaso = (c) => Boolean(texto) && texto.includes(localDeCuenta(c.email));
    const ordenadas = [...cuentas].sort((a, b) => Number(esDelCaso(b)) - Number(esDelCaso(a)));
    return (
        <Modal abierto={abierto} titulo="Cuentas de prueba" onCerrar={onCerrar}>
            <p className="mb-3 tipo-media text-xs text-texto-tenue">Solo existen en el entorno de prueba y se borran al terminar la validación.</p>
            <ul className="flex flex-col gap-2">
                {ordenadas.map((c) => <FilaCuenta key={c.email} cuenta={c} resaltada={esDelCaso(c)} />)}
            </ul>
        </Modal>
    );
};

export const CuentasPrueba = ({ etiqueta, resaltar, className = '' }) => {
    const { ronda } = useRonda();
    const { data } = useCuentasPrueba(ronda?.id);
    const [abierto, setAbierto] = useState(false);
    if (!data?.length) return null;
    return (
        <>
            <Button label={etiqueta ?? `Cuentas de prueba (${data.length})`} small variant="ghost" className={className} onClick={() => setAbierto(true)} />
            <ModalCuentasPrueba abierto={abierto} onCerrar={() => setAbierto(false)} cuentas={data} resaltar={resaltar} />
        </>
    );
};
