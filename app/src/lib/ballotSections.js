// Ballot Sections: the groups a Report divides a Covered Ballot into, in the
// order a Washington ballot lists them. Each Contest belongs to exactly one,
// derived from its pipeline `category`; every Measure, statewide or local,
// belongs to Measures. The Ballot Brief emits the same groups in the same
// order so the AI Report follows the Report.

export const SECTION_ORDER = ['Measures', 'Federal', 'State', 'Courts', 'County', 'Local']

const CATEGORY_SECTION = {
  Federal: 'Federal',
  State: 'State',
  StateSupremeCourt: 'Courts',
  CourtOfAppeals: 'Courts',
  DistrictCourt: 'Courts',
  Judicial: 'Courts',
  County: 'County',
  City: 'Local',
  Port: 'Local',
  PublicUtility: 'Local',
  Local: 'Local',
}

// A category the pipeline adds later lands in Local rather than vanishing
// from the Report; ballotSections.test.js pins that.
export function sectionOf(contest) {
  return CATEGORY_SECTION[contest?.category] || 'Local'
}

// -> [{ name, contests, measures }] for the non-empty sections only, in
// SECTION_ORDER, keeping the callers' order within each section.
export function ballotSections(contests, measures) {
  const byName = Object.fromEntries(SECTION_ORDER.map((name) => [name, { name, contests: [], measures: [] }]))
  for (const m of measures) byName.Measures.measures.push(m)
  for (const c of contests) byName[sectionOf(c)].contests.push(c)
  return SECTION_ORDER.map((name) => byName[name]).filter((s) => s.contests.length || s.measures.length)
}
