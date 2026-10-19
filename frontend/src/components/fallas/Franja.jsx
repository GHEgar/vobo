import { Chip } from '@/components/Chip';
import { SelectField } from '@/components/Field';
import { Label } from '@/components/Label';
import { opciones } from '@/utils/etiquetas';

export const Franja = ({ etiqueta, children }) => (
    <div role="group" aria-label={etiqueta} className="mt-4 flex flex-col gap-4 rounded-xl border border-borde p-4 sm:flex-row sm:flex-wrap sm:items-start sm:gap-x-8">
        {children}
    </div>
);

export const EstadoCampo = ({ id, valor, estados, editable, etiqueta, onCambiar, children }) => {
    const estado = estados[valor] ?? Object.values(estados)[0];
    return (
        <div className="min-w-0 sm:w-[220px]">
            {editable ? (
                <SelectField
                    id={id}
                    label="Estado"
                    aria-label={etiqueta}
                    value={valor}
                    onChange={(e) => onCambiar(e.target.value)}
                    options={opciones(estados)}
                    className="w-full"
                />
            ) : (
                <>
                    <Label as="p" text="Estado" />
                    <p className="mt-3"><Chip tono={estado.tono}>{estado.texto}</Chip></p>
                </>
            )}
            {children && <div className="mt-2">{children}</div>}
        </div>
    );
};
