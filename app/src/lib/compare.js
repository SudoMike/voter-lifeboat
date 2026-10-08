// "See how these values would have applied to the <archived> ballot" (issue
// #18): the Results page's link from the active election to an archived one,
// and how the archived page reads the answers it receives.
//
// No translation table between rubrics (epic #1): an axis id answered on one
// election is applied as-is wherever the other election's rubric has the same
// id, and ignored where it does not. The note below says so.

import { archivedElections, electionHref, electionKind, monthDay } from './elections.js'
import { encodeProfileForElection } from './codec.js'
import { DISTRICT_ORDER } from './districts.js'
import { electionGuide } from './officialLinks.js'

// Titles of the active election's axes that an archived rubric lacks or titles
// differently, keyed by the active app-data `election.id`. The archived page
// cannot see the active rubric without fetching a second app-data file, so the
// few titles it needs live here. compare.test.js pins this map to the shipped
// data; update it when the active election or its rubric changes.
export const SOURCE_AXIS_TITLES = {
  '2026-11-03-general': {
    social: 'Gender, LGBTQ+ and reproductive policy',
    'parental-rights': 'Parents and public schools',
  },
}

const RESOLVED_STATUSES = new Set(['full_county', 'partial_county', 'statewide_only'])

/**
 * The archived election to link to, or null when the link should not show.
 *
 * Shown only for a ballot context the voter resolved in this session through
 * the address flow, on a page that is not itself archived:
 * - `restored` is null: the report did not arrive by link (a tampered link
 *   can carry any context; a genuine one is still someone else's ballot or an
 *   old visit, and the voter can start over to get a fresh one);
 * - `coverageStatus` is full_county, partial_county or statewide_only;
 * - `county.id` is set, so the archived page can scope countywide contests;
 * - `matched` (the geocoder's matched address) is set. Only
 *   lookupBallotContext produces it and the URL payload never carries it, so
 *   this also rules out a context rebuilt from a link.
 * The target is the newest archived election in the index.
 */
export function comparisonTarget({ index, election, context, restored }) {
  if (restored) return null
  if (!election || election.status === 'archived') return null
  if (!context || !RESOLVED_STATUSES.has(context.coverageStatus)) return null
  if (!context.county?.id || !context.matched) return null
  return archivedElections(index).find((e) => e.id !== election.id) || null
}

/** 'See how these values would have applied to the August 4 primary ballot →' */
export function comparisonLinkText(entry) {
  return `See how these values would have applied to the ${monthDay(entry.day)} ${electionKind(entry)} ballot →`
}

/**
 * `<base><archived id>#p=<payload>`: the same answers and ballot context,
 * with `e`/`v` of the archived election and `f` = `fromElectionId`, the
 * app-data `election.id` the answers were given for.
 */
export function comparisonHref(base, entry, fromElectionId, context, answers) {
  return `${electionHref(base, entry)}#p=${encodeProfileForElection(entry, context, answers, fromElectionId)}`
}

const districtRank = (k) => {
  const i = DISTRICT_ORDER.indexOf(k)
  return i < 0 ? DISTRICT_ORDER.length : i
}

/**
 * Reconcile a restored ballot context with the coverage of the election being
 * served. A context resolved against the same election passes through
 * unchanged; one resolved against another election (the archived-comparison
 * link) can disagree with this election's coverage:
 *
 * - The county is supported here but the context has no districts at all (a
 *   statewide-only context from an election that covered no counties). A real
 *   lookup against this election would have found at least the congressional
 *   and legislative districts, so this is a partial guide: countywide contests
 *   match, district contests cannot, and every district layer this election's
 *   data scopes on for the county is reported missing. `districtsNotLookedUp`
 *   lets the page say why.
 * - The county is not supported here but the context claims county coverage:
 *   degrade to statewide-only rather than overclaim.
 */
export function reconcileContext(context, data) {
  if (!context) return context
  const countyId = context.county?.id
  const coverage = data.coverage?.supported_counties?.find((c) => c.id === countyId)
  if (!coverage) {
    return context.coverageStatus === 'statewide_only' || !countyId
      ? context
      : { ...context, coverageStatus: 'statewide_only' }
  }
  if (Object.keys(context.districts || {}).length) return context
  const layers = new Set()
  for (const item of [...(data.contests || []), ...(data.measures || [])]) {
    const s = item.scope
    if (s?.kind === 'DISTRICT' && s.county === countyId) layers.add(s.layer)
  }
  const missingLayers = [...layers].sort((a, b) => districtRank(a) - districtRank(b) || a.localeCompare(b))
  return {
    ...context,
    coverageStatus: missingLayers.length ? 'partial_county' : coverage.coverage,
    districts: {},
    missingLayers,
    districtsNotLookedUp: missingLayers.length > 0,
  }
}

/** The answers on axes the served rubric defines; others are left out of scoring. */
export function answersInRubric(answers, data) {
  const ids = new Set(data.rubric.axes.map((a) => a.id))
  return Object.fromEntries(Object.entries(answers || {}).filter(([axis]) => ids.has(axis)))
}

const humanize = (id) => id.replace(/-/g, ' ')
const orList = (xs) =>
  xs.length <= 1 ? xs.join('') : `${xs.slice(0, -1).join(', ')} or ${xs[xs.length - 1]}`

/**
 * One line for the archived page when the answers were given for another
 * election (`fromElectionId`), or null. N = answered axes this rubric has,
 * M = answered axes in the payload; the first sentence shows only when
 * N < M and names the missing axes by the source election's titles. A second
 * sentence says when an answered axis exists here under a different title,
 * since the answer is applied to this rubric's axis as-is.
 */
export function comparisonNote(data, answers, fromElectionId) {
  if (!fromElectionId || fromElectionId === data.election?.id) return null
  const titles = SOURCE_AXIS_TITLES[fromElectionId] || {}
  const here = new Map(data.rubric.axes.map((a) => [a.id, a]))
  const answered = Object.keys(answers || {})
  const missing = answered.filter((id) => !here.has(id))
  const sentences = []
  if (missing.length) {
    const n = answered.length - missing.length
    const guide = electionGuide(data.election).kind
    sentences.push(
      `Compared on ${n} of ${answered.length} values you answered; ${guide ? `the ${guide}` : 'this'} guide did not ask about ${orList(
        missing.map((id) => titles[id] || humanize(id))
      )}.`
    )
  }
  const retitled = answered.filter((id) => here.has(id) && titles[id] && titles[id] !== here.get(id).title)
  if (retitled.length) {
    const pairs = retitled.map((id) => `“${titles[id]}” answer is used as-is for this guide’s “${here.get(id).title}” value`)
    sentences.push(`Your ${pairs.join('; your ')}.`)
  }
  return sentences.length ? sentences.join(' ') : null
}
