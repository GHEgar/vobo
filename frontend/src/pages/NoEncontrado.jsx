import { Link } from 'react-router';
import { EmptyState } from '@/components/Estados';

const NoEncontrado = () => (
    <EmptyState
        titulo="Esta página no existe"
        accion={<Link to="/" className="tipo-negrita text-sm text-primario hover:underline">Volver al inicio</Link>}
    />
);

export default NoEncontrado;
