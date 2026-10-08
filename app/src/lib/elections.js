// The app ships one app-data.json per election under public/data/<id>/ and a
// small index, public/data/elections.json, naming the Active Election.
// Both are written by pipeline/assemble_app_data.py.

export const ELECTION_INDEX_PATH = 'data/elections.json'

/** Path, relative to the site base, of the active election's app data. */
export function activeAppDataPath(index) {
  const active = index?.active
  if (!active || !index.elections?.some((e) => e.id === active)) {
    throw new Error(`election index has no loadable active election (${active})`)
  }
  return `data/${active}/app-data.json`
}

/** Fetch the election index, then the active election's app data. */
export async function loadActiveAppData(baseUrl, fetchImpl = fetch) {
  const getJson = async (path) => {
    const r = await fetchImpl(`${baseUrl}${path}`)
    if (!r.ok) throw new Error(`data ${r.status}`)
    return r.json()
  }
  const index = await getJson(ELECTION_INDEX_PATH)
  return getJson(activeAppDataPath(index))
}
