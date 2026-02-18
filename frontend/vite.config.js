import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const backendUrl = env.VITE_API_BASE || 'http://localhost:8000';

  return {
    plugins: [react()],
    server: {
      // Only proxy if pointing to localhost; skip proxy for absolute URLs (deployed backend)
      proxy: backendUrl.startsWith('http://localhost')
        ? { '/api': backendUrl }
        : {},
    },
  };
});
