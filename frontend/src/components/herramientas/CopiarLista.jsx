import { useRef, useState } from 'react';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';

const armarTexto = (grupos, soloDesplegar) => grupos
    .map(([sistema, herramientas]) => [
        sistema,
        herramientas
            .filter((h) => h.id !== 'general')
            .filter((h) => !soloDesplegar || ['desplegar', 'desplegar_con_aviso'].includes(h.decision?.decision))
            .map((h) => h.nombre),
    ])
    .filter(([, nombres]) => nombres.length)
    .map(([sistema, nombres]) => [sistema, ...nombres].join('\n'))
    .join('\n\n');

export const CopiarLista = ({ grupos }) => {
    const [abierto, setAbierto] = useState(false);
    const [soloDesplegar, setSoloDesplegar] = useState(false);
    const [copiado, setCopiado] = useState(false);
    const areaRef = useRef(null);
    const texto = armarTexto(grupos, soloDesplegar);

    const copiar = async () => {
        try {
            await navigator.clipboard.writeText(texto);
        } catch {
            areaRef.current?.select();
            document.execCommand('copy');
        }
        setCopiado(true);
    };

    const elegir = (valor) => {
        setSoloDesplegar(valor);
        setCopiado(false);
    };

    return (
        <>
            <Button label="Copiar lista" variant="outline" small onClick={() => setAbierto(true)} />
            <Modal abierto={abierto} titulo="Lista de herramientas" onCerrar={() => setAbierto(false)}>
                <div className="flex flex-wrap gap-2" role="group" aria-label="Qué herramientas incluir">
                    <Button label="Todas" small variant={soloDesplegar ? 'secondary' : 'primary'} pressed={!soloDesplegar} onClick={() => elegir(false)} />
                    <Button label="Solo las que se despliegan" small variant={soloDesplegar ? 'primary' : 'secondary'} pressed={soloDesplegar} onClick={() => elegir(true)} />
                </div>
                <textarea
                    ref={areaRef}
                    readOnly
                    aria-label="Lista para copiar"
                    value={texto || 'Ninguna herramienta con esta selección.'}
                    onFocus={(e) => e.target.select()}
                    rows={14}
                    className="w-full resize-y rounded-[8px] bg-fondo px-4 py-3 tipo-media text-[13px]/5 text-texto focus:outline-none focus:ring-1 focus:ring-primario"
                />
                <div className="flex justify-end">
                    <Button label={copiado ? 'Copiado' : 'Copiar'} onClick={copiar} disabled={!texto} />
                </div>
            </Modal>
        </>
    );
};
