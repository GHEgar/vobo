import { Navigate, Route, Routes } from 'react-router';
import { MainLayout } from '@/layouts/MainLayout';
import { RondaProvider } from '@/providers/RondaProvider';
import { useSesion } from '@/hooks/useSesion';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import Inicio from '@/pages/Inicio';
import Seccion from '@/pages/Seccion';
import Caso from '@/pages/Caso';
import Tablero from '@/pages/Tablero';
import Fallas from '@/pages/Fallas';
import Rondas from '@/pages/Rondas';
import Herramientas from '@/pages/Herramientas';
import Aprobaciones from '@/pages/Aprobaciones';
import Acta from '@/pages/Acta';
import Avisos from '@/pages/Avisos';
import Entrar from '@/pages/Entrar';
import NoEncontrado from '@/pages/NoEncontrado';

const ConPagina = ({ pagina, children }) => {
    const { ve } = useSesion();
    return ve(pagina) ? children : <Navigate to="/" replace />;
};

const AppRoutes = () => {
    const { usuario, cargando, error, reintentar } = useSesion();

    if (cargando) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={reintentar} pantalla />;
    if (!usuario) return <Entrar />;

    return (
        <RondaProvider>
            <Routes>
                <Route path="acta" element={<ConPagina pagina="aprobaciones"><Acta /></ConPagina>} />
                <Route element={<MainLayout />}>
                    <Route index element={<Inicio />} />
                    <Route path="seccion/:seccionId" element={<Seccion />} />
                    <Route path="caso/:casoId" element={<Caso />} />
                    <Route path="avisos" element={<Avisos />} />
                    <Route
                        path="tablero"
                        element={<ConPagina pagina="tablero"><Tablero /></ConPagina>}
                    />
                    <Route
                        path="fallas"
                        element={<ConPagina pagina="fallas"><Fallas /></ConPagina>}
                    />
                    <Route
                        path="herramientas"
                        element={<ConPagina pagina="herramientas"><Herramientas /></ConPagina>}
                    />
                    <Route
                        path="aprobaciones"
                        element={<ConPagina pagina="aprobaciones"><Aprobaciones /></ConPagina>}
                    />
                    <Route
                        path="rondas"
                        element={<ConPagina pagina="rondas"><Rondas /></ConPagina>}
                    />
                    <Route path="*" element={<NoEncontrado />} />
                </Route>
            </Routes>
        </RondaProvider>
    );
};

export default AppRoutes;
