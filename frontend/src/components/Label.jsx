import { Tooltip } from '@/components/Tooltip';

export const Label = ({ htmlFor, text, tooltip, required = false, as: Etiqueta = 'label' }) => (
    <div className="flex items-center gap-1">
        <Etiqueta htmlFor={Etiqueta === 'label' ? htmlFor : undefined} className="block tipo-media text-sm text-texto">
            {text}
            {required && <span className="ml-1 text-error">*</span>}
        </Etiqueta>
        <Tooltip text={tooltip} />
    </div>
);
