import { NavLink, Outlet, useLocation } from 'react-router';
import { useInstancia } from '@/hooks/useInstancia';
import { useSesion } from '@/hooks/useSesion';
import { useScrollArribaAlNavegar } from '@/hooks/useRecordarScroll';
import { usePresencia } from '@/hooks/usePresencia';
import { PresenciaContext } from '@/contexts/PresenciaContext';
import { MenuUsuario } from '@/components/MenuUsuario';
import { SelectorRonda } from '@/components/SelectorRonda';
import { Buscador } from '@/components/buscador/Buscador';
import { Marca } from '@/components/Marca';
import { SelectorProyecto } from '@/components/SelectorProyecto';
import { etiquetaInicio } from '@/utils/marca';

const ENLACES = [
    { to: '/', texto: 'Inicio', pagina: null },
    { to: '/tablero', texto: 'Tablero', pagina: 'tablero' },
    { to: '/fallas', texto: 'Fallas', pagina: 'fallas' },
    { to: '/herramientas', texto: 'Herramientas', pagina: 'herramientas' },
    { to: '/aprobaciones', texto: 'Aprobaciones', pagina: 'aprobaciones' },
    { to: '/rondas', texto: 'Rondas', pagina: 'rondas' },
];

const CON_SELECTOR = new Set(['/fallas', '/aprobaciones', '/rondas']);

const MenuPaginas = ({ enlaces, className }) => (
    <nav aria-label="Páginas" className={`gap-2 ${className}`}>
        {enlaces.map((e) => (
            <NavLink
                key={e.to}
                to={e.to}
                end={e.to === '/'}
                className={({ isActive }) => `inline-flex h-[30px] shrink-0 items-center rounded-full px-4 tipo-negrita text-xs ${isActive ? 'bg-primario text-white' : 'bg-transparent text-texto-tenue hover:bg-primario-claro'}`}
            >
                {e.texto}
            </NavLink>
        ))}
    </nav>
);

export const MainLayout = () => {
    const { usuario, ve, salir } = useSesion();
    const enlaces = ENLACES.filter((e) => !e.pagina || ve(e.pagina));
    const variasPaginas = enlaces.length > 1;
    const { pathname } = useLocation();
    const { producto, nombre } = useInstancia();
    useScrollArribaAlNavegar();
    const informarPresencia = usePresencia();

    return (
        <PresenciaContext value={informarPresencia}>
            <div className="min-h-dvh">
                <header className="sticky top-0 z-30 mx-auto max-w-6xl px-4 pt-3 md:px-6 md:pt-4">
                    <div className="@container relative flex flex-col gap-3 rounded-2xl bg-white px-4 py-3 shadow-[0px_3px_12px_var(--color-sombra-suave)] md:px-7">
                        <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
                            <div className="flex min-w-0 flex-1 items-center gap-3">
                                <NavLink to="/" className="flex shrink-0 items-center" aria-label={etiquetaInicio(producto, nombre)}>
                                    <Marca />
                                </NavLink>
                                <SelectorProyecto />
                            </div>
                            {!variasPaginas && <Buscador className="order-last w-full sm:order-none sm:w-[190px] sm:shrink-0" />}
                            <MenuUsuario usuario={usuario} onSalir={salir} />
                        </div>
                        {variasPaginas && (
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
                                <MenuPaginas
                                    enlaces={enlaces}
                                    className="flex min-w-0 overflow-x-auto [scrollbar-width:none] [mask-image:linear-gradient(to_right,black_calc(100%-16px),transparent)] sm:flex-1"
                                />
                                <Buscador className="w-full sm:ml-auto sm:w-[190px] sm:shrink-0" />
                            </div>
                        )}
                    </div>
                </header>
                <main className="mx-auto flex max-w-6xl flex-col gap-5 px-4 pt-5 pb-6 md:px-6">
                    {CON_SELECTOR.has(pathname) && (
                        <div className="flex">
                            <SelectorRonda />
                        </div>
                    )}
                    <Outlet />
                </main>
            </div>
        </PresenciaContext>
    );
};
