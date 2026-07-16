import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/king-county/',
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5373,
    proxy: {
      // dev-only: forward /api to a locally running server.js (default port,
      // matches siteplat's production convention — no PORT override needed)
      '/api': 'http://localhost:5000',
    },
  },
})
