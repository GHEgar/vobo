import { Button } from '@/components/Button';
import { useVersionNueva } from '@/hooks/useVersionNueva';

export const AvisoVersion = () => {
    const nueva = useVersionNueva();
    if (!nueva) return null;
    return (
        <div role="status" className="fixed inset-x-0 bottom-4 z-50 flex justify-center px-4 print:hidden">
            <div className="flex items-center gap-3 rounded-full bg-white py-2 pr-2 pl-5 shadow-[0px_8px_24px_var(--color-sombra)]">
                <span className="tipo-media text-sm text-texto">Hay una versión nueva.</span>
                <Button label="Recargar" small onClick={() => window.location.reload()} />
            </div>
        </div>
    );
};
