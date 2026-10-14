export const Spinner = ({ pequeno = false, claro = false, pantalla = false }) => {
    const rueda = (
        <span
            role="status"
            aria-label="Cargando"
            className={`inline-block animate-spin rounded-full border-2 border-t-transparent ${pequeno ? 'h-4 w-4' : 'h-8 w-8'} ${claro ? 'border-white' : 'border-primario'}`}
        />
    );
    if (!pantalla) return rueda;
    return <div className="flex min-h-[60dvh] items-center justify-center">{rueda}</div>;
};
