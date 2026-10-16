export const BOTON_IMPRESO = 'inline-flex h-[36px] items-center gap-2 rounded-full px-5 tipo-negrita text-sm';

export const HojaImpresa = ({ acciones, children }) => (
    <div className="min-h-dvh bg-fondo-pagina print:min-h-0 print:bg-white">
        <div className="sticky top-0 z-20 border-b border-borde bg-fondo-pagina shadow-[0px_2px_8px_var(--color-sombra-tenue)] print:hidden">
            <div role="toolbar" aria-label="Acciones del documento" className="mx-auto flex max-w-5xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3 md:px-6">
                {acciones}
            </div>
        </div>
        <div className="px-3 py-4 md:px-6 md:py-8 print:p-0">
            <main className="mx-auto max-w-5xl min-w-0 rounded-2xl bg-white p-5 text-texto shadow-[0px_3px_12px_var(--color-sombra-tenue)] md:p-10 print:max-w-none print:rounded-none print:p-0 print:shadow-none">
                {children}
            </main>
        </div>
    </div>
);
