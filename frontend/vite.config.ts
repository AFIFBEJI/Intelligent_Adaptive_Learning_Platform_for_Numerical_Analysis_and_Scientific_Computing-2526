import { defineConfig } from 'vite'

export default defineConfig({
  server: {
    port: 4200,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      // Proxy pour les assets servis par le backend FastAPI :
      // /static/animations/*.mp4 (videos Manim). Sans ca, le navigateur
      // tape sur le dev server Vite (port 4200) qui ne connait pas ces
      // fichiers et retourne 404, donc <video> reste vide.
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  // `vite preview` (used by the CI E2E job via `npm run preview`) does NOT
  // inherit `server.proxy`. Without this, the previewed build calls /api on
  // :4200 (no backend there) and every request 404s -> registration and all
  // API-dependent tests fail. We mirror the dev proxy so preview reaches the
  // backend on :8000 exactly like the dev server does.
  preview: {
    port: 4200,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
