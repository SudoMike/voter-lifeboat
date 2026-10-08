// HTTP-level tests for server.js: run the real server against a throwaway
// dist/ and data dir.
import test from 'node:test'
import assert from 'node:assert/strict'
import { spawn } from 'node:child_process'
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const index = {
  active: '2026-11-03-general',
  elections: [
    { id: '2026-08-04-primary', app_id: '2026-08-04-primary-special', status: 'archived' },
    { id: '2026-11-03-general', app_id: '2026-11-03-general', status: 'active' },
  ],
}

async function startServer() {
  const root = mkdtempSync(join(tmpdir(), 'vl-server-'))
  const dist = join(root, 'dist')
  mkdirSync(join(dist, 'data/2026-11-03-general'), { recursive: true })
  writeFileSync(join(dist, 'index.html'), '<!doctype html><title>app</title>')
  writeFileSync(join(dist, 'data/elections.json'), JSON.stringify(index))
  writeFileSync(join(dist, 'data/2026-11-03-general/app-data.json'), '{"contests":[]}')
  const dataDir = join(root, 'data')
  const port = 20000 + Math.floor(Math.random() * 20000)
  const child = spawn(process.execPath, [join(import.meta.dirname, 'server.js')], {
    env: { ...process.env, PORT: String(port), DIST_DIR: dist, DATA_DIR: dataDir },
    stdio: ['ignore', 'pipe', 'inherit'],
  })
  await new Promise((resolve, reject) => {
    child.stdout.on('data', (d) => String(d).includes('serving') && resolve())
    child.on('exit', (code) => reject(new Error(`server exited ${code}`)))
  })
  const base = `http://127.0.0.1:${port}`
  const reports = () => {
    const f = join(dataDir, 'reports.jsonl')
    return existsSync(f) ? readFileSync(f, 'utf8').split('\n').filter(Boolean).map(JSON.parse) : []
  }
  return { base, reports, stop: () => child.kill() }
}

const report = (election) =>
  JSON.stringify({ v: 'x', election, coverageStatus: 'statewide_only', answers: { taxes: [1, 2] } })

test('report records for an archived election are rejected; active ones are kept', async (t) => {
  const s = await startServer()
  t.after(s.stop)
  const post = (body) =>
    fetch(`${s.base}/api/report`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body })

  const archivedByAppId = await post(report('2026-08-04-primary-special'))
  assert.equal(archivedByAppId.status, 409)
  const archivedByPackageId = await post(report('2026-08-04-primary'))
  assert.equal(archivedByPackageId.status, 409)
  const live = await post(report('2026-11-03-general'))
  assert.equal(live.status, 204)

  assert.deepEqual(s.reports().map((r) => r.election), ['2026-11-03-general'])
})

test('a missing data file is a real 404, not the SPA page', async (t) => {
  const s = await startServer()
  t.after(s.stop)
  const missing = await fetch(`${s.base}/washington-state/data/nope/app-data.json`)
  assert.equal(missing.status, 404)
  const present = await fetch(`${s.base}/washington-state/data/2026-11-03-general/app-data.json`)
  assert.equal(present.status, 200)
  assert.deepEqual(await present.json(), { contests: [] })
})

test('election routes fall back to the SPA page', async (t) => {
  const s = await startServer()
  t.after(s.stop)
  for (const path of ['/washington-state', '/washington-state/2026-08-04-primary', '/washington-state/no-such']) {
    const r = await fetch(`${s.base}${path}`)
    assert.equal(r.status, 200, path)
    assert.match(await r.text(), /<title>app<\/title>/, path)
  }
})
