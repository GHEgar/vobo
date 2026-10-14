import { Label } from '@/components/Label';

const BASE = 'block w-full rounded-[8px] border border-transparent bg-fondo px-4 py-2 tipo-media text-[13px] text-primario placeholder-texto-placeholder placeholder:tipo-regular hover:border-primario hover:bg-white hover:shadow-[0px_2px_24px_var(--color-sombra-campo)] focus:bg-white focus:outline-none focus:ring-1 focus:ring-primario';

export const TextField = ({ id, label, tooltip, required, error, multiline = false, rows = 4, ...rest }) => {
    const Control = multiline ? 'textarea' : 'input';
    return (
        <div className="mt-4">
            <Label htmlFor={id} text={label} tooltip={tooltip} required={required} />
            <Control
                id={id}
                rows={multiline ? rows : undefined}
                aria-invalid={Boolean(error)}
                className={`mt-3 ${BASE} ${multiline ? 'min-h-[96px] resize-y leading-5' : 'h-[40px]'} ${error ? 'border-error! bg-white' : ''}`}
                {...rest}
            />
            {error && <p className="mt-1 tipo-media text-xs text-error-fuerte">{error}</p>}
        </div>
    );
};

export const SelectField = ({ id, label, tooltip, options, placeholder, className = '', claseControl = '', ...rest }) => (
    <div className={className}>
        {label && <Label htmlFor={id} text={label} tooltip={tooltip} />}
        <select id={id} className={`${label ? 'mt-3' : ''} h-[40px] cursor-pointer ${BASE} ${claseControl}`} {...rest}>
            {placeholder !== undefined && <option value="">{placeholder}</option>}
            {options.map((o) => <option key={o.valor} value={o.valor}>{o.texto}</option>)}
        </select>
    </div>
);
