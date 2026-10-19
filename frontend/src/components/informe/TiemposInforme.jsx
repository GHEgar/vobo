import { Dato, Vencido } from '@/components/informe/Dato';
import { formatearFecha } from '@/utils/formato';
import { duracion, formatearDia, vencido } from '@/utils/seguimiento';

export const TiemposInforme = ({ plazo, responsable, resueltoEn, resolvio, desde, resuelto, texto }) => (
    <>
        <Dato termino="Plazo">{plazo && <>{formatearDia(plazo)}<Vencido activo={vencido(plazo, resuelto)} texto={texto} /></>}</Dato>
        <Dato termino="Responsable">{plazo ? responsable : ''}</Dato>
        <Dato termino="Resuelto">{resueltoEn && `${formatearFecha(resueltoEn)} · ${resolvio || '—'}`}</Dato>
        <Dato termino="Tiempo de solución">{resueltoEn && duracion(desde, resueltoEn)}</Dato>
    </>
);
