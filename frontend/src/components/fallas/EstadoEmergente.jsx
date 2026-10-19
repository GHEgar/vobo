import { Alert, Chat, CheckCircle, Eye, Refresh } from 'tesela/react';
import { BotonEmergente } from '@/components/fallas/BotonIcono';
import { EsfuerzoCampo } from '@/components/fallas/EsfuerzoCampo';
import { EstadoCampo } from '@/components/fallas/EstadoCampo';
import { PlazoCampo } from '@/components/fallas/PlazoCampo';
import { Resolucion } from '@/components/fallas/Resolucion';
import { VinculoCampo } from '@/components/fallas/VinculoCampo';
import { formatearDia, formatearEsfuerzo, vencido } from '@/utils/seguimiento';

const ICONOS = {
    nueva: Alert,
    nuevo: Chat,
    en_curso: Refresh,
    lista_para_revalidar: Eye,
    cerrada: CheckCircle,
    resuelto: CheckCircle,
};

export const EstadoEmergente = ({ id, objeto, registro, estados, final, editable, etiqueta, resolucion, verbo, onCambiar, textoVencido, error }) => {
    const estado = estados[registro.estado] ?? Object.values(estados)[0];
    const resuelto = registro.estado === final;
    const atrasado = vencido(registro.plazo, resuelto);
    const plazo = registro.plazo ? `, plazo ${formatearDia(registro.plazo)}${atrasado ? `, ${textoVencido.toLowerCase()}` : ''}` : '';
    const esfuerzo = registro.esfuerzo_horas != null ? `, esfuerzo ${formatearEsfuerzo(registro.esfuerzo_horas)}` : '';
    return (
        <BotonEmergente
            etiqueta={`Estado: ${estado.texto}${plazo}${esfuerzo}`}
            titulo={etiqueta}
            icono={ICONOS[registro.estado] ?? Alert}
            tono={estado.tono}
            marca={atrasado}
        >
            <EstadoCampo
                id={`estado-${id}`}
                valor={registro.estado}
                estados={estados}
                editable={editable}
                etiqueta={etiqueta}
                onCambiar={(valor) => onCambiar({ estado: valor })}
            >
                <Resolucion verbo={verbo} en={resolucion.en} por={resolucion.por} desde={resolucion.desde} />
            </EstadoCampo>
            <PlazoCampo
                id={id}
                plazo={registro.plazo}
                responsable={registro.plazo_por_nombre || registro.plazo_por}
                resuelto={resuelto}
                editable={editable}
                onCambiar={(valor) => onCambiar({ plazo: valor })}
                textoVencido={textoVencido}
            />
            <EsfuerzoCampo
                id={id}
                horas={registro.esfuerzo_horas}
                editable={editable}
                onCambiar={(valor) => onCambiar({ esfuerzo_horas: valor })}
            />
            <VinculoCampo objeto={objeto} registro={registro} editable={editable} onCambiar={onCambiar} />
            {error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{error}</p>}
        </BotonEmergente>
    );
};

export const ChipPlazo = ({ plazo, resuelto, textoVencido }) => {
    if (!plazo) return null;
    const atrasado = vencido(plazo, resuelto);
    return (
        <span className={`inline-flex min-h-[30px] items-center rounded-full px-4 py-1 tipo-negrita text-xs ${atrasado ? 'bg-falla-fondo text-falla' : 'bg-fondo-suave text-texto-tenue'}`}>
            {atrasado ? `${textoVencido} · ` : 'Plazo · '}{formatearDia(plazo)}
        </span>
    );
};
