import { History, Layers, Link as Enlace } from 'tesela/react';
import { Chip } from '@/components/Chip';
import { formatearEsfuerzo, idRegistro } from '@/utils/seguimiento';

const irA = (principal) => {
    const destino = document.getElementById(idRegistro(principal.objeto, principal.id));
    if (!destino) return;
    destino.scrollIntoView({ behavior: 'smooth', block: 'center' });
    destino.focus({ preventScroll: true });
};

const corto = (principal) => (principal.objeto === 'falla' ? `#${principal.id}` : principal.etiqueta);

export const ChipsVinculo = ({ registro }) => {
    const esfuerzo = formatearEsfuerzo(registro.esfuerzo_horas);
    const { principal, seguidores = 0 } = registro;
    return (
        <>
            {esfuerzo && (
                <Chip title={principal ? 'Esfuerzo estimado; no cuenta en las sumas porque sigue a otro reporte' : 'Esfuerzo estimado'}>
                    <History size={14} className="shrink-0" />{esfuerzo}
                </Chip>
            )}
            {principal && (
                <Chip tono="marca" title={`Se resuelve con ${principal.etiqueta}`} onClick={() => irA(principal)}>
                    <Enlace size={14} className="shrink-0" />Sigue a {corto(principal)}
                </Chip>
            )}
            {seguidores > 0 && (
                <Chip tono="marca" title={`Se ${seguidores === 1 ? 'resuelve 1 reporte' : `resuelven ${seguidores} reportes`} con este`}>
                    <Layers size={14} className="shrink-0" />+{seguidores} {seguidores === 1 ? 'reporte' : 'reportes'}
                </Chip>
            )}
        </>
    );
};
