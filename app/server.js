// Production server: serves the built SPA, accepts feedback posts, and
// records anonymous report completions (answers + ballot context, never address).
// Zero dependencies (node:http only). Both append JSONL to DATA_DIR —
// on siteplat that's the persistent /app/data mount; read it over SSH.
// The reports dataset is public: GET /api/reports returns every record.

import { createServer } from 'node:http'
import {
  createReadStream,
  existsSync,
  mkdirSync,
  appendFileSync,
  statSync,
  readFileSync,
} from 'node:fs'
import { join, extname, normalize } from 'node:path'

const PORT = process.env.PORT || 5000
const BASE_PATH = process.env.BASE_PATH || '/washington-state'
const DIST = process.env.DIST_DIR || join(import.meta.dirname, 'dist')
const DATA_DIR = process.env.DATA_DIR || join(import.meta.dirname, 'data')
const FEEDBACK_FILE = join(DATA_DIR, 'feedback.jsonl')
const REPORTS_FILE = join(DATA_DIR, 'reports.jsonl')
const MAX_BODY = 64 * 1024

// mirrors LAYERS in app/src/lib/geo.js — anything else is dropped
const DISTRICT_KEYS = ['CONGDST', 'LEGDST', 'KCCDST', 'SCCDST', 'JUDDST', 'FIRDST', 'SCHDST', 'CITY']

function readBody(req, res, onJson) {
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
      onJson(JSON.parse(body))
    } catch {
      res.writeHead(400, { 'Content-Type': 'application/json' })
      res.end('{"error":"bad json"}')
    }
  })
}

const COVERAGE_STATUSES = new Set(['full_county', 'partial_county', 'statewide_only'])

// { v, election, coverageStatus, county, districts, answers } -> sanitized record
function sanitizeReport(payload) {
  const districts = {}
  for (const k of DISTRICT_KEYS) {
    if (payload.districts?.[k] != null) districts[k] = String(payload.districts[k]).slice(0, 60)
  }
  const answers = {}
  for (const [axis, pair] of Object.entries(payload.answers || {}).slice(0, 40)) {
    if (!Array.isArray(pair)) continue
    const [v, w] = pair
    if (typeof v !== 'number' || typeof w !== 'number') continue
    answers[String(axis).slice(0, 60)] = [
      Math.max(-2, Math.min(2, v)),
      Math.max(0, Math.min(4, w)),
    ]
  }
  if (!Object.keys(answers).length) return null
  const coverageStatus = COVERAGE_STATUSES.has(payload.coverageStatus)
    ? payload.coverageStatus
    : undefined
  const county = payload.county && typeof payload.county === 'object'
    ? {
        id: payload.county.id ? String(payload.county.id).slice(0, 40) : undefined,
        fips: payload.county.fips ? String(payload.county.fips).slice(0, 10) : undefined,
        name: payload.county.name ? String(payload.county.name).slice(0, 80) : undefined,
      }
    : undefined
  return {
    at: new Date().toISOString(),
    v: payload.v ? String(payload.v).slice(0, 40) : undefined,
    election: payload.election ? String(payload.election).slice(0, 80) : undefined,
    coverageStatus,
    county,
    districts,
    answers,
  }
}

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
    readBody(req, res, (payload) => {
      const entry = {
        at: new Date().toISOString(),
        kind: String(payload.kind || 'comment').slice(0, 40),
        contest: payload.contest ? String(payload.contest).slice(0, 120) : undefined,
        candidate: payload.candidate ? String(payload.candidate).slice(0, 120) : undefined,
        message: String(payload.message || '').slice(0, 4000),
      }
      appendFileSync(FEEDBACK_FILE, JSON.stringify(entry) + '\n')
      res.writeHead(204).end()
    })
    return
  }

  // Anonymous report completion: answers + ballot context, never an address.
  if (req.method === 'POST' && req.url === '/api/report') {
    readBody(req, res, (payload) => {
      const record = sanitizeReport(payload)
      if (!record) {
        res.writeHead(400, { 'Content-Type': 'application/json' })
        return res.end('{"error":"missing answers"}')
      }
      appendFileSync(REPORTS_FILE, JSON.stringify(record) + '\n')
      res.writeHead(204).end()
    })
    return
  }

  // The public dataset: every recorded report, as a JSON array.
  if (req.method === 'GET' && req.url.split('?')[0] === '/api/reports') {
    let reports = []
    if (existsSync(REPORTS_FILE)) {
      reports = readFileSync(REPORTS_FILE, 'utf8')
        .split('\n')
        .filter(Boolean)
        .map((line) => {
          try {
            return JSON.parse(line)
          } catch {
            return null
          }
        })
        .filter(Boolean)
    }
    res.writeHead(200, { 'Content-Type': 'application/json', 'Cache-Control': 'no-cache' })
    return res.end(JSON.stringify({ count: reports.length, reports }))
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
