import { Label } from '@/components/Label';

export const RadioGroup = ({ name, label, tooltip, options, value, onChange, required, error, vertical = false }) => (
    <fieldset className="mt-4">
        <legend className="contents">
            <Label as="span" text={label} tooltip={tooltip} required={required} />
        </legend>
        <div className={`mt-3 flex flex-col gap-2 ${vertical ? '' : 'md:flex-row md:flex-wrap md:gap-x-8'}`}>
            {options.map((o) => (
                <div key={o.valor} className="flex min-h-[40px] items-start gap-3 py-2">
                    <input
                        type="radio"
                        id={`${name}-${o.valor}`}
                        name={name}
                        value={o.valor}
                        checked={value === o.valor}
                        onChange={() => onChange(o.valor)}
                        className="mt-0.5 h-5 w-5 shrink-0 cursor-pointer appearance-none rounded-full border border-primario checked:border-primario checked:bg-primario checked:shadow-[inset_0_0_0_3px_white] hover:bg-primario-claro"
                    />
                    <label htmlFor={`${name}-${o.valor}`} className="cursor-pointer tipo-media text-xs/5 text-texto">
                        {o.texto}
                    </label>
                </div>
            ))}
        </div>
        {error && <p className="mt-1 tipo-media text-xs text-error-fuerte">{error}</p>}
    </fieldset>
);
