import { useState } from 'react';
import { Button } from '@/components/Button';
import { Checkbox } from '@/components/Checkbox';
import { Chip } from '@/components/Chip';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import { useAccesos, useGuardarAccesos, useUsuarios } from '@/hooks/useValidacion';
import { PAGINAS_OTORGABLES, rolesDe } from '@/utils/roles';

const Editor = ({ usuarios, inicial }) => {
    const guardar = useGuardarAccesos();
    const [otorgadas, setOtorgadas] = useState(() => Object.fromEntries(inicial.map((a) => [a.usuario_email, a.paginas])));

    const alternar = (email, pagina, marcado) => {
        const actuales = otorgadas[email] ?? [];
        setOtorgadas({ ...otorgadas, [email]: marcado ? [...actuales, pagina] : actuales.filter((p) => p !== pagina) });
    };

    const items = Object.entries(otorgadas).map(([usuario_email, paginas]) => ({ usuario_email, paginas }));

    if (!usuarios.length) return <p className="tipo-media text-sm text-texto-apagado">Nadie ha entrado todavía.</p>;

    return (
        <div className="flex flex-col gap-3">
            <ul className="flex flex-col gap-2">
                {usuarios.map((u) => (
                    <li key={u.email} className="flex flex-col gap-3 rounded-2xl bg-fondo px-4 py-3 md:flex-row md:items-center md:justify-between">
                        <div className="flex flex-wrap items-center gap-2">
                            <span className="flex flex-col">
                                <span className="tipo-negrita text-sm text-texto">{u.nombre}</span>
                                <span className="tipo-media text-[11px] text-texto-apagado">{u.email}</span>
                            </span>
                            {rolesDe(u.permisos).map((r) => <Chip key={r} tono="marca">{r}</Chip>)}
                        </div>
                        <div className="flex flex-wrap gap-x-6 gap-y-2">
                            {PAGINAS_OTORGABLES.map(({ pagina, texto, permiso }) => {
                                const porRol = u.permisos.includes(permiso);
                                return (
                                    <Checkbox
                                        key={pagina}
                                        id={`acceso-${u.email}-${pagina}`}
                                        checked={porRol || (otorgadas[u.email] ?? []).includes(pagina)}
                                        disabled={porRol}
                                        onChange={(marcado) => alternar(u.email, pagina, marcado)}
                                    >
                                        {texto}
                                    </Checkbox>
                                );
                            })}
                        </div>
                    </li>
                ))}
            </ul>
            {guardar.error && <p className="tipo-media text-xs text-error-fuerte">{guardar.error.message}</p>}
            <div className="flex justify-end">
                <Button label={guardar.isSuccess ? 'Guardado' : 'Guardar'} loading={guardar.isPending} onClick={() => guardar.mutate(items)} />
            </div>
        </div>
    );
};

export const QuienVeQue = () => {
    const usuarios = useUsuarios();
    const accesos = useAccesos();
    if (usuarios.isPending || accesos.isPending) return <Spinner />;
    if (usuarios.error || accesos.error) {
        return <ErrorState mensaje={(usuarios.error || accesos.error).message} onReintentar={() => { usuarios.refetch(); accesos.refetch(); }} />;
    }
    return <Editor usuarios={usuarios.data} inicial={accesos.data} />;
};
