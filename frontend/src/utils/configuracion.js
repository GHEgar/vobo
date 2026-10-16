export const cambiados = (borrador, actual) => Object.fromEntries(
    Object.entries(borrador).filter(([clave, valor]) => JSON.stringify(valor) !== JSON.stringify(actual[clave])),
);
