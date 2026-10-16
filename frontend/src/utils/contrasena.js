export const MINIMO_CONTRASENA = 10;

export const problemaContrasena = (nueva, confirmacion) => {
    if (nueva.length < MINIMO_CONTRASENA) return `Usa al menos ${MINIMO_CONTRASENA} caracteres.`;
    if (confirmacion && nueva !== confirmacion) return 'Las contraseñas no coinciden.';
    return '';
};
