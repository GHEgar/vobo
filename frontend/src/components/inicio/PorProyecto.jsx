import { ProgressBar } from '@/components/ProgressBar';

export const AvancePorProyecto = ({ grupos }) => (
    <ul className="mt-4 flex flex-col gap-1">
        {grupos.map((g) => (
            <li key={g.clave} className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-3 gap-y-1 px-3 py-2 sm:grid-cols-[200px_minmax(0,1fr)_auto]">
                <span className="tipo-negrita text-sm text-texto">{g.nombre}</span>
                <span className="order-3 col-span-2 sm:order-none sm:col-span-1"><ProgressBar hechos={g.hechos} total={g.total} delgada /></span>
                <span className="tipo-media text-xs text-texto-tenue">{g.hechos} de {g.total}</span>
            </li>
        ))}
    </ul>
);
