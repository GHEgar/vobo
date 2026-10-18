import { lazy, Suspense } from 'react';
import { Navigate, Route, Routes, useMatch } from 'react-router';
import { MainLayout } from '@/layouts/MainLayout';
import { RondaProvider } from '@/providers/RondaProvider';
import { ProyectoProvider } from '@/providers/ProyectoProvider';
import { useSesion } from '@/hooks/useSesion';
import { Spinner } from '@/components/Spinner';
import { ErrorState } from '@/components/Estados';
import Inicio from '@/pages/Inicio';
import Seccion from '@/pages/Seccion';
import Caso from '@/pages/Caso';
import Entrar from '@/pages/Entrar';
import NoEncontrado from '@/pages/NoEncontrado';
import { EdicionProvider } from '@/providers/EdicionProvider';

const Tablero = lazy(() => import('@/pages/Tablero'));
const Fallas = lazy(() => import('@/pages/Fallas'));
const Rondas = lazy(() => import('@/pages/Rondas'));
const Herramientas = lazy(() => import('@/pages/Herramientas'));
const Aprobaciones = lazy(() => import('@/pages/Aprobaciones'));
const Acta = lazy(() => import('@/pages/Acta'));
const InformeFallas = lazy(() => import('@/pages/InformeFallas'));
const Avisos = lazy(() => import('@/pages/Avisos'));
const Invitacion = lazy(() => import('@/pages/Invitacion'));
const Restablecer = lazy(() => import('@/pages/Restablecer'));
const Pantalla = lazy(() => import('@/pages/Pantalla'));
const Admin = lazy(() => import('@/pages/Admin'));
const Editor = lazy(() => import('@/pages/Editor'));

const Diferida = ({ children, pantalla = false }) => <Suspense fallback={<Spinner pantalla={pantalla} />}>{children}</Suspense>;

const ConPagina = ({ pagina, children }) => {
    const { ve } = useSesion();
    return ve(pagina) ? <Diferida>{children}</Diferida> : <Navigate to="/" replace />;
};

const RutasPublicas = () => (
    <Diferida pantalla>
        <Routes>
            <Route path="invitacion/:token" element={<Invitacion />} />
            <Route path="restablecer/:token" element={<Restablecer />} />
            <Route path="pantalla/:token" element={<Pantalla />} />
        </Routes>
    </Diferida>
);

const AppRoutes = () => {
    const { usuario, cargando, error, reintentar } = useSesion();
    const invitacion = useMatch('/invitacion/:token');
    const restablecimiento = useMatch('/restablecer/:token');
    const pantalla = useMatch('/pantalla/:token');

    if (invitacion || restablecimiento || pantalla) return <RutasPublicas />;
    if (cargando) return <Spinner pantalla />;
    if (error) return <ErrorState mensaje={error.message} onReintentar={reintentar} pantalla />;
    if (!usuario) return <Entrar />;

    return (
        <ProyectoProvider>
            <EdicionProvider>
                <RondaProvider>
                    <Routes>
                        <Route path="acta" element={<ConPagina pagina="aprobaciones"><Acta /></ConPagina>} />
                        <Route path="informe-fallas" element={<ConPagina pagina="fallas"><InformeFallas /></ConPagina>} />
                        <Route element={<MainLayout />}>
                            <Route index element={<Inicio />} />
                            <Route path="seccion/:seccionId" element={<Seccion />} />
                            <Route path="caso/:casoId" element={<Caso />} />
                            <Route path="avisos" element={<Diferida><Avisos /></Diferida>} />
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
                            <Route
                                path="admin"
                                element={<ConPagina pagina="admin"><Admin /></ConPagina>}
                            />
                            <Route
                                path="editor"
                                element={<ConPagina pagina="editor"><Editor /></ConPagina>}
                            />
                            <Route path="*" element={<NoEncontrado />} />
                        </Route>
                    </Routes>
                </RondaProvider>
            </EdicionProvider>
        </ProyectoProvider>
    );
};

export default AppRoutes;
