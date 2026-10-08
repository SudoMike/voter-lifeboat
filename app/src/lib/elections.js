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

/** The route serving one election: `<base><id>`. */
export const electionHref = (base, entry) => `${base.replace(/\/+$/, '')}/${entry.id}`

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]
const parseDay = (day) => {
  const [y, m, d] = day.split('-').map(Number)
  return new Date(Date.UTC(y, m - 1, d))
}

/** '2026-08-04' -> 'August 4, 2026' */
export function formatElectionDay(day) {
  const date = parseDay(day)
  return `${MONTHS[date.getUTCMonth()]} ${date.getUTCDate()}, ${date.getUTCFullYear()}`
}

/**
 * Washington county auditors mail ballots at least 18 days before election
 * day (RCW 29A.40.070). '2026-11-03' -> 'Oct 16'
 */
export function ballotsMailBy(day) {
  return shortDay(day, -18)
}

/**
 * Online and mail registration (and updates) close 8 days before election day
 * (RCW 29A.08.140); in-person registration runs until 8 p.m. on the day.
 * '2026-11-03' -> 'Oct 26'
 */
export function registerOnlineBy(day) {
  return shortDay(day, -8)
}

/** '2026-11-03' -> 'Nov 3'; `offset` shifts by whole days. */
export function shortDay(day, offset = 0) {
  const date = parseDay(day)
  date.setUTCDate(date.getUTCDate() + offset)
  return `${MONTHS[date.getUTCMonth()].slice(0, 3)} ${date.getUTCDate()}`
}

const WEEKDAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

/** '2026-11-03' -> 'Tuesday, November 3, 2026' */
export function longElectionDay(day) {
  return `${WEEKDAYS[parseDay(day).getUTCDay()]}, ${formatElectionDay(day)}`
}

/** 'Explore the August primary guide' for 2026-08-04-primary. */
export function guideLinkText(entry) {
  const month = MONTHS[parseDay(entry.day || entry.id.slice(0, 10)).getUTCMonth()]
  const kind = entry.id.split('-').slice(3).join(' ') || 'election'
  return `Explore the ${month} ${kind} guide`
}

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
