// Production server: serves the built SPA and accepts feedback posts.
// Zero dependencies (node:http only). Feedback appends JSONL to DATA_DIR —
// on siteplat that's the persistent /app/data mount; read it over SSH.

import { createServer } from 'node:http'
import { createReadStream, existsSync, mkdirSync, appendFileSync, statSync } from 'node:fs'
import { join, extname, normalize } from 'node:path'

const PORT = process.env.PORT || 5000
const BASE_PATH = process.env.BASE_PATH || '/king-county'
const DIST = process.env.DIST_DIR || join(import.meta.dirname, 'dist')
const DATA_DIR = process.env.DATA_DIR || join(import.meta.dirname, 'data')
const FEEDBACK_FILE = join(DATA_DIR, 'feedback.jsonl')
const MAX_BODY = 64 * 1024

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript',
  '.css': 'text/css',
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.woff2': 'font/woff2',
}

mkdirSync(DATA_DIR, { recursive: true })

const CENSUS_GEOCODER =
  'https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress'

const server = createServer((req, res) => {
  if (req.method === 'GET' && req.url.startsWith('/api/geocode')) {
    const { searchParams } = new URL(req.url, 'http://internal')
    const address = (searchParams.get('address') || '').slice(0, 200)
    if (!address) {
      res.writeHead(400, { 'Content-Type': 'application/json' })
      return res.end('{"error":"address required"}')
    }
    const url = `${CENSUS_GEOCODER}?address=${encodeURIComponent(address)}&benchmark=Public_AR_Current&vintage=Current_Current&layers=Counties&format=json`
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`census ${r.status}`)
        return r.json()
      })
      .then((data) => {
        res.writeHead(200, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify(data))
      })
      .catch(() => {
        res.writeHead(502, { 'Content-Type': 'application/json' })
        res.end('{"error":"census geocoder unavailable"}')
      })
    return
  }

  if (req.method === 'POST' && req.url === '/api/feedback') {
    let body = ''
    let dropped = false
    req.on('data', (chunk) => {
      body += chunk
      if (body.length > MAX_BODY && !dropped) {
        dropped = true
        res.writeHead(413).end()
        req.destroy()
      }
    })
    req.on('end', () => {
      if (dropped) return
      try {
        const payload = JSON.parse(body)
        const entry = {
          at: new Date().toISOString(),
          kind: String(payload.kind || 'comment').slice(0, 40),
          contest: payload.contest ? String(payload.contest).slice(0, 120) : undefined,
          candidate: payload.candidate ? String(payload.candidate).slice(0, 120) : undefined,
          message: String(payload.message || '').slice(0, 4000),
          shared_profile: payload.shared_profile,
        }
        appendFileSync(FEEDBACK_FILE, JSON.stringify(entry) + '\n')
        res.writeHead(204).end()
      } catch {
        res.writeHead(400, { 'Content-Type': 'application/json' })
        res.end('{"error":"bad json"}')
      }
    })
    return
  }

  if (req.method !== 'GET' && req.method !== 'HEAD') {
    res.writeHead(405).end()
    return
  }

  if (req.url === '/') {
    res.writeHead(302, { Location: `${BASE_PATH}/` }).end()
    return
  }

  let path = normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '')
  if (path === BASE_PATH) path = `${BASE_PATH}/`
  if (!path.startsWith(`${BASE_PATH}/`)) {
    res.writeHead(404).end()
    return
  }
  path = path.slice(BASE_PATH.length)
  if (path === '/') path = '/index.html'
  let file = join(DIST, path)
  if (!file.startsWith(DIST)) {
    res.writeHead(403).end()
    return
  }
  if (!existsSync(file) || statSync(file).isDirectory()) {
    file = join(DIST, 'index.html') // SPA fallback (hash routing needs only /)
  }
  const ext = extname(file)
  res.writeHead(200, {
    'Content-Type': MIME[ext] || 'application/octet-stream',
    'Cache-Control': ext === '.html' ? 'no-cache' : 'public, max-age=3600',
  })
  if (req.method === 'HEAD') return res.end()
  createReadStream(file).pipe(res)
})

server.listen(PORT, () => console.log(`voter-lifeboat serving on :${PORT}`))
