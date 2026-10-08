import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { existsSync, statSync } from 'node:fs'
import { join } from 'node:path'

const BASE = '/washington-state/'

// Vite's SPA fallback answers a missing /washington-state/data/... file with
// index.html (200), which the app would then fail to parse as JSON. Match
// server.js instead: a data file that does not exist is a 404.
function missingDataIs404(rootDir) {
  return (req, res, next) => {
    const url = (req.url || '').split('?')[0]
    if (!url.startsWith(`${BASE}data/`)) return next()
    const file = join(rootDir, decodeURIComponent(url.slice(BASE.length)))
    if (!file.startsWith(rootDir) || !existsSync(file) || statSync(file).isDirectory()) {
      res.statusCode = 404
      return res.end()
    }
    next()
  }
}

const dataFiles404 = {
  name: 'missing-data-files-404',
  configureServer(server) {
    server.middlewares.use(missingDataIs404(server.config.publicDir))
  },
  configurePreviewServer(server) {
    server.middlewares.use(missingDataIs404(server.config.build.outDir.startsWith('/')
      ? server.config.build.outDir
      : join(server.config.root, server.config.build.outDir)))
  },
}

export default defineConfig({
  base: BASE,
  plugins: [react(), dataFiles404],
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
