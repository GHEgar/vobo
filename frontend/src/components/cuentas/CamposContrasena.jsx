import { TextField } from '@/components/Field';
import { MINIMO_CONTRASENA, problemaContrasena } from '@/utils/contrasena';

export const CamposContrasena = ({ prefijo, nueva, confirmacion, onNueva, onConfirmacion, etiqueta = 'Contraseña nueva' }) => {
    const problema = nueva && confirmacion ? problemaContrasena(nueva, confirmacion) : '';
    return (
        <>
            <TextField
                id={`${prefijo}-nueva`}
                label={etiqueta}
                type="password"
                autoComplete="new-password"
                required
                minLength={MINIMO_CONTRASENA}
                tooltip={`Al menos ${MINIMO_CONTRASENA} caracteres; evita contraseñas comunes.`}
                value={nueva}
                onChange={(e) => onNueva(e.target.value)}
            />
            <TextField
                id={`${prefijo}-confirmacion`}
                label="Repite la contraseña"
                type="password"
                autoComplete="new-password"
                required
                value={confirmacion}
                error={problema}
                onChange={(e) => onConfirmacion(e.target.value)}
            />
        </>
    );
};
