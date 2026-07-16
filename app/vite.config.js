import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // dev-only: forward feedback posts to a locally running server.js
      '/api': 'http://localhost:8080',
    },
  },
})
