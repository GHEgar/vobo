import { Chip } from '@/components/Chip';
import { SelectField } from '@/components/Field';
import { Label } from '@/components/Label';
import { opciones } from '@/utils/etiquetas';

export const EstadoCampo = ({ id, valor, estados, editable, etiqueta, onCambiar, children }) => {
    const estado = estados[valor] ?? Object.values(estados)[0];
    return (
        <div className="min-w-0 [&>div]:mt-0">
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
