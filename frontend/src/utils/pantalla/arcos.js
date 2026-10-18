import { ESTADOS, ORDEN_ESTADOS } from '@/utils/pantalla/paleta';

export const arcosDe = (conteos, total, circunferencia, hueco) => {
    let acumulado = 0;
    return ORDEN_ESTADOS.filter((estado) => conteos[estado] > 0).map((estado) => {
        const largo = (conteos[estado] / total) * circunferencia;
        const arco = { estado, color: ESTADOS[estado], dash: `${Math.max(largo - hueco, 1)} ${circunferencia}`, offset: -acumulado };
        acumulado += largo;
        return arco;
    });
};
