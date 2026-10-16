import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RootErrorBoundary } from '@/components/RootErrorBoundary';
import { SesionProvider } from '@/providers/SesionProvider';
import { MetaInstancia } from '@/components/MetaInstancia';
import { AvisoVersion } from '@/components/AvisoVersion';
import { fijarAlNoAutenticado, fijarCsrf } from '@/services/api';
import { CLAVE_SESION, vencioLaSesion } from '@/utils/sesion';
import AppRoutes from '@/Routes';
import 'rotulo';
import './index.css';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: { retry: 1, refetchOnWindowFocus: true, staleTime: 30 * 1000 },
    },
});

fijarAlNoAutenticado((ruta) => {
    if (!vencioLaSesion(401, ruta, queryClient.getQueryData(CLAVE_SESION))) return;
    fijarCsrf('');
    queryClient.setQueryData(CLAVE_SESION, null);
});

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <RootErrorBoundary>
            <QueryClientProvider client={queryClient}>
                <MetaInstancia />
                <AvisoVersion />
                <BrowserRouter>
                    <SesionProvider>
                        <AppRoutes />
                    </SesionProvider>
                </BrowserRouter>
            </QueryClientProvider>
        </RootErrorBoundary>
    </StrictMode>,
);
