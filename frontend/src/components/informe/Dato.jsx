import { formatearEsfuerzo } from '@/utils/seguimiento';

export const Dato = ({ termino, children }) => (
    <div>
        <dt className="tipo-media text-[11px] text-texto-apagado">{termino}</dt>
        <dd className="wrap-anywhere text-[13px]">{children || '—'}</dd>
    </div>
);

export const Vencido = ({ activo, texto = 'Vencido' }) => (activo ? <span className="ml-1 tipo-negrita text-falla">· {texto}</span> : null);

export const DatosVinculo = ({ registro }) => (
    <>
        <Dato termino="Esfuerzo">{formatearEsfuerzo(registro.esfuerzo_horas) || 'Sin estimar'}</Dato>
        {registro.principal && <Dato termino="Se resuelve con">{registro.principal.etiqueta}</Dato>}
        {registro.seguidores > 0 && <Dato termino="Lo siguen">{registro.seguidores === 1 ? '1 reporte' : `${registro.seguidores} reportes`}</Dato>}
    </>
);
