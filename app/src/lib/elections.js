// The app ships one app-data.json per election under public/data/<id>/ and a
// small index, public/data/elections.json, naming the Active Election and
// listing every election with app data (status "active" or "archived").
// Both are written by pipeline/assemble_app_data.py.
//
// Each election has two ids: `id` is the package id used in data paths and
// routes (2026-08-04-primary); `app_id` is the `election.id` inside its
// app-data.json, which report links carry (2026-08-04-primary-special).

export const ELECTION_INDEX_PATH = 'data/elections.json'

/**
 * Routes: `<base>` serves the active election; `<base><election-id>` serves
 * that election. Returns the id named by the path, or null.
 */
export function electionIdFromPath(pathname, base) {
  const root = base.replace(/\/+$/, '')
  if (pathname !== root && !pathname.startsWith(`${root}/`)) return null
  const id = pathname.slice(root.length).split('/').filter(Boolean)[0]
  return id ? decodeURIComponent(id) : null
}

/** The index entry for an election named by package id or app id. */
export function findElection(index, id) {
  if (!id) return null
  return index?.elections?.find((e) => e.id === id || e.app_id === id) || null
}

/** Archived elections listed in the index, newest first. */
export function archivedElections(index) {
  return (index?.elections || [])
    .filter((e) => e.status === 'archived')
    .sort((a, b) => String(b.day).localeCompare(String(a.day)))
}

export const appDataPath = (entry) => `data/${entry.id}/app-data.json`

/** Path, relative to the site base, of the active election's app data. */
export function activeAppDataPath(index) {
  const active = index?.active
  if (!active || !index.elections?.some((e) => e.id === active)) {
    throw new Error(`election index has no loadable active election (${active})`)
  }
  return `data/${active}/app-data.json`
}

/** A route or data file named an election this site does not have. */
export class ElectionNotFound extends Error {
  constructor(electionId) {
    super(`no such election: ${electionId}`)
    this.name = 'ElectionNotFound'
    this.electionId = electionId
  }
}

const jsonGetter = (baseUrl, fetchImpl) => async (path) => {
  const r = await fetchImpl(`${baseUrl}${path}`)
  if (!r.ok) throw new Error(`data ${r.status}`)
  return r.json()
}

/** Fetch the election index, then the active election's app data. */
export async function loadActiveAppData(baseUrl, fetchImpl = fetch) {
  const getJson = jsonGetter(baseUrl, fetchImpl)
  const index = await getJson(ELECTION_INDEX_PATH)
  return getJson(activeAppDataPath(index))
}

/**
 * Pick and load the election to serve.
 *
 * - `routeId` (from the path) wins; an id not in the index is ElectionNotFound.
 * - Otherwise a report link's election (`linkElectionId`, package or app id)
 *   is served if the index lists it, so old links render against their own
 *   election's data.
 * - Otherwise the active election.
 *
 * Resolves to { index, election (index entry), data }.
 */
export async function loadElection(baseUrl, { routeId, linkElectionId } = {}, fetchImpl = fetch) {
  const getJson = jsonGetter(baseUrl, fetchImpl)
  const index = await getJson(ELECTION_INDEX_PATH)
  let entry
  if (routeId) {
    entry = findElection(index, routeId)
    if (!entry) throw new ElectionNotFound(routeId)
  } else {
    entry = findElection(index, linkElectionId) || findElection(index, index.active)
    if (!entry) throw new Error(`election index has no loadable active election (${index.active})`)
  }
  let data
  try {
    data = await getJson(appDataPath(entry))
  } catch {
    // A 404, or an HTML fallback page where JSON was expected.
    throw new ElectionNotFound(entry.id)
  }
  return { index, election: entry, data }
}
