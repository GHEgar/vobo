import { Component } from 'react';

export class RootErrorBoundary extends Component {
    constructor(props) {
        super(props);
        this.state = { error: null };
    }

    static getDerivedStateFromError(error) {
        return { error };
    }

    componentDidCatch(error, info) {
        console.error('Unhandled render error', error, info?.componentStack);
    }

    render() {
        if (!this.state.error) return this.props.children;
        return (
            <main className="flex min-h-dvh flex-col items-center justify-center gap-4 bg-fondo-pagina p-6 text-center">
                <h1 className="tipo-negrita text-xl text-primario">Algo salió mal</h1>
                <p className="max-w-md tipo-media text-sm text-texto-tenue">
                    La página tuvo un error inesperado. Recarga para continuar; lo que ya marcaste está guardado.
                </p>
                <button type="button" onClick={() => window.location.reload()} className="h-[40px] rounded-full bg-primario px-6 tipo-negrita text-sm text-white">
                    Recargar
                </button>
            </main>
        );
    }
}
