import { NavLink, Outlet, useLocation } from 'react-router';
import { useInstancia } from '@/hooks/useInstancia';
import { useSesion } from '@/hooks/useSesion';
import { useScrollArribaAlNavegar } from '@/hooks/useRecordarScroll';
import { MenuUsuario } from '@/components/MenuUsuario';
import { SelectorRonda } from '@/components/SelectorRonda';
import { Buscador } from '@/components/buscador/Buscador';

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
    const { pathname } = useLocation();
    const { nombre } = useInstancia();
    useScrollArribaAlNavegar();

    return (
        <div className="min-h-dvh">
            <header className="sticky top-0 z-30 mx-auto max-w-6xl px-4 pt-3 md:px-6 md:pt-4">
                <div className="relative rounded-2xl bg-white shadow-[0px_3px_12px_var(--color-sombra-suave)]">
                    <div className="flex items-center justify-between gap-3 px-4 py-3 md:gap-6 md:px-7">
                        <NavLink to="/" className="flex min-w-0 shrink-0 flex-col leading-none" aria-label={nombre ? `Validaciones · ${nombre}, ir a inicio` : 'Validaciones, ir a inicio'}>
                            <span className="tipo-negrita text-lg text-primario sm:text-xl md:text-2xl">Validaciones</span>
                            {nombre && <span className="mt-1 tipo-negrita text-xs text-aviso">{nombre}</span>}
                        </NavLink>
                        {enlaces.length > 1 && <MenuPaginas enlaces={enlaces} className="hidden min-w-0 flex-1 overflow-x-auto [scrollbar-width:none] lg:flex" />}
                        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
                            <Buscador />
                            <MenuUsuario usuario={usuario} onSalir={salir} />
                        </div>
                    </div>
                    {enlaces.length > 1 && (
                        <MenuPaginas
                            enlaces={enlaces}
                            className="flex overflow-x-auto px-4 pb-3 [scrollbar-width:none] [mask-image:linear-gradient(to_right,transparent,black_16px,black_calc(100%-16px),transparent)] md:px-7 lg:hidden"
                        />
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
    );
};
