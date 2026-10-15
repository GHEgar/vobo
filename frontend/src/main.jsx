import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RootErrorBoundary } from '@/components/RootErrorBoundary';
import { SesionProvider } from '@/providers/SesionProvider';
import { MetaInstancia } from '@/components/MetaInstancia';
import AppRoutes from '@/Routes';
import '@npmegar/rotulo';
import './index.css';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: { retry: 1, refetchOnWindowFocus: true, staleTime: 30 * 1000 },
    },
});

createRoot(document.getElementById('root')).render(
    <StrictMode>
        <RootErrorBoundary>
            <QueryClientProvider client={queryClient}>
                <MetaInstancia />
                <BrowserRouter>
                    <SesionProvider>
                        <AppRoutes />
                    </SesionProvider>
                </BrowserRouter>
            </QueryClientProvider>
        </RootErrorBoundary>
    </StrictMode>,
);
