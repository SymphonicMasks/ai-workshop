import {defineConfig} from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
    preview: {
        port: 8080,
        strictPort: true,
    },
    server: {
        watch: {
            usePolling: true
        },
        port: 3000,
        strictPort: true,
        host: true,
    },
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    plugins: [react()],
})
