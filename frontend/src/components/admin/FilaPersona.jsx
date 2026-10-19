import { Button } from '@/components/Button';
import { Chip } from '@/components/Chip';
import { useFijarCuentaActiva } from '@/hooks/useAdmin';
import { formatearRelativa } from '@/utils/formato';

export const FilaPersona = ({ persona, nombresDeRol, esYo, conCuentas, gestionaCuentas, onRoles, onRestablecer }) => {
    const fijarActiva = useFijarCuentaActiva();
    const { cuenta } = persona;

    return (
        <li className="flex flex-col gap-3 rounded-2xl bg-fondo px-4 py-3 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex min-w-0 flex-col gap-2">
                <div className="min-w-0">
                    <p className="tipo-negrita text-sm text-texto">{persona.nombre}{esYo && <span className="tipo-media text-texto-apagado"> · tú</span>}</p>
                    <p className="truncate tipo-media text-[11px] text-texto-apagado">{persona.email} · entró {formatearRelativa(persona.ultimo_acceso)}</p>
                </div>
                <div className="flex flex-wrap gap-2">
                    {persona.oidc && <Chip>Organización</Chip>}
                    {cuenta && <Chip tono={cuenta.activa ? 'exito' : 'error'}>{cuenta.activa ? 'Contraseña propia' : 'Cuenta desactivada'}</Chip>}
                    {persona.roles.map((clave) => <Chip key={clave} tono="marca">{nombresDeRol[clave] ?? clave}</Chip>)}
                    {!persona.roles.length && <Chip>Sin roles en la app</Chip>}
                </div>
                {fijarActiva.error && <p role="alert" className="tipo-media text-xs text-error-fuerte">{fijarActiva.error.message}</p>}
            </div>
            <div className="flex shrink-0 flex-wrap gap-2">
                {onRoles && <Button label="Roles" small variant="ghost" onClick={onRoles} />}
                {conCuentas && <Button label="Restablecer contraseña" small variant="ghost" onClick={onRestablecer} />}
                {cuenta && !esYo && gestionaCuentas && (
                    <Button
                        label={cuenta.activa ? 'Desactivar cuenta' : 'Activar cuenta'}
                        small
                        variant={cuenta.activa ? 'enlaceRojo' : 'link'}
                        loading={fijarActiva.isPending}
                        onClick={() => fijarActiva.mutate({ id: persona.id, activa: !cuenta.activa })}
                    />
                )}
            </div>
        </li>
    );
};
