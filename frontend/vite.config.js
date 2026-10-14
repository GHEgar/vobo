import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import { fileURLToPath } from 'url';

const raiz = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, raiz, '');
    const destino = env.VITE_PROXY_TARGET || 'http://localhost:8010';
    return {
        plugins: [react(), tailwindcss()],
        resolve: {
            alias: { '@': path.resolve(raiz, 'src') },
        },
        server: {
            host: true,
            port: Number(env.VITE_DEV_PORT) || 5173,
            proxy: {
                '/api': { target: destino, changeOrigin: false },
                '/media': { target: destino, changeOrigin: false },
            },
        },
    };
});
