export const NombreProyecto = ({ nombre, color, className = '' }) => (
    <span
        title={nombre}
        style={color ? { color } : undefined}
        className={`block min-w-0 truncate tipo-negrita text-sm text-nombre md:text-[15px] ${className}`}
    >
        {nombre}
    </span>
);
