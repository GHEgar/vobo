import { Button } from '@/components/Button';

const OPCIONES = [
    ['todas', 'Todas'],
    ['funcional', 'Funcional'],
    ['tecnica', 'Técnico'],
];

export const FiltroAudiencia = ({ valor, onCambiar }) => (
    <div className="flex w-fit gap-1 rounded-full bg-fondo p-1" role="group" aria-label="Tipo de secciones">
        {OPCIONES.map(([clave, texto]) => (
            <Button key={clave} label={texto} small variant={valor === clave ? 'primary' : 'link'} pressed={valor === clave} onClick={() => onCambiar(clave)} />
        ))}
    </div>
);
