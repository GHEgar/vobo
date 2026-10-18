import { arcosDe } from '@/utils/pantalla/arcos';
import { PALETA } from '@/utils/pantalla/paleta';

export const Anillo = ({ conteos, total, tam = 400, grosor = 40, hueco = 4, etiqueta, children }) => {
    const centro = tam / 2;
    const radio = centro - grosor / 2 - 12;
    const circunferencia = 2 * Math.PI * radio;
    const arcos = total > 0 ? arcosDe(conteos, total, circunferencia, hueco) : [];
    return (
        <div className="relative" style={{ width: tam, height: tam }}>
            <svg width={tam} height={tam} viewBox={`0 0 ${tam} ${tam}`} role="img" aria-label={etiqueta} className="block">
                <circle cx={centro} cy={centro} r={radio} fill="none" stroke={PALETA.pista} strokeWidth={grosor} />
                {arcos.map((a) => (
                    <circle
                        key={a.estado}
                        cx={centro}
                        cy={centro}
                        r={radio}
                        fill="none"
                        stroke={a.color}
                        strokeWidth={grosor}
                        strokeDasharray={a.dash}
                        strokeDashoffset={a.offset}
                        transform={`rotate(-90 ${centro} ${centro})`}
                        className="anillo-arco"
                    />
                ))}
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center gap-1">{children}</div>
        </div>
    );
};
