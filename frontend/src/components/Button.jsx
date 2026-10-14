import { Spinner } from '@/components/Spinner';

const VARIANTES = {
    primary: 'bg-primario text-white hover:shadow-[0px_8px_16px_var(--color-sombra)]',
    secondary: 'bg-borde text-texto-tenue hover:bg-gris-hover hover:shadow-[0px_8px_16px_var(--color-sombra-gris)]',
    outline: 'bg-transparent text-primario border border-primario hover:bg-primario-suave',
    success: 'bg-pasa-fondo text-pasa border border-pasa-borde hover:bg-pasa-hover',
    danger: 'bg-falla-fondo text-falla border border-falla-borde hover:bg-falla-hover',
    warn: 'bg-pendiente-fondo text-pendiente border border-pendiente-borde hover:bg-pendiente-hover',
    link: 'bg-transparent text-primario hover:underline',
    enlaceRojo: 'bg-transparent text-error-fuerte hover:underline',
    ghost: 'bg-transparent text-texto-tenue border border-gris hover:border-primario hover:text-primario',
};

const DESHABILITADO = 'bg-gris text-neutro cursor-not-allowed';

export const Button = ({
    label,
    variant = 'primary',
    type = 'button',
    disabled = false,
    loading = false,
    fullWidth = false,
    small = false,
    grande = false,
    pressed,
    className = '',
    ...rest
}) => (
    <button
        type={type}
        disabled={disabled || loading}
        aria-busy={loading}
        aria-pressed={pressed}
        className={`inline-flex items-center justify-center gap-2 rounded-full tipo-negrita transition-shadow focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primario focus-visible:ring-offset-2 ${small ? 'h-[30px] px-4 text-xs' : grande ? 'h-[44px] px-8 text-base' : 'h-[40px] px-6 text-sm'} ${fullWidth ? 'w-full' : ''} ${disabled ? DESHABILITADO : VARIANTES[variant]} ${className}`}
        {...rest}
    >
        {loading ? <Spinner pequeno claro={variant !== 'secondary'} /> : label}
    </button>
);
