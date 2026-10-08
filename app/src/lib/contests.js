// The heading a contest card and the Ballot Brief show: which office, and
// where. Most shipped contests already carry `office` (the seat) and
// `district` (the jurisdiction). King County's packages are parsed from the
// King County Elections candidate file, which puts them the other way round:
// `office` is the jurisdiction ('Legislative District No.  46', 'City of
// Seattle', 'Southwest Electoral District') and `district` is the seat
// ('State Senator', 'Judge Position No. 5'). Both elections ship that shape,
// so it is normalized here rather than in the archived data.

const KING_LEGISLATIVE = /^Legislative District No\.\s+(\d+)$/
const KING_ELECTORAL = /^(?:Northeast|Southeast|Southwest|West|Shoreline) Electoral District$/
const KING_JURISDICTION = /^(?:City of .+|Metropolitan King County)$/

function squash(s) {
  return String(s || '').replace(/\s+/g, ' ').trim()
}

function swapped(contest) {
  if (contest.owner !== 'king' || !contest.district) return null
  const office = squash(contest.office)
  const seat = squash(contest.district)
  const leg = KING_LEGISLATIVE.exec(office)
  if (leg) return { office: seat, place: `Legislative District ${leg[1]}` }
  if (KING_ELECTORAL.test(office)) return { office: seat, place: `King County District Court, ${office}` }
  if (KING_JURISDICTION.test(office)) return { office: seat, place: office }
  return null
}

// -> { office, place }; place falls back to 'Statewide' or 'Countywide' for a
// contest with no district. Runs of whitespace in the source text (Columbia's
// 'Columbia County  Assessor') collapse to one space. Callers choose their own
// casing and separator.
export function contestHeading(contest) {
  const fixed = swapped(contest)
  if (fixed) return fixed
  const place = squash(contest.district) || (contest.scope?.kind === 'STATEWIDE' ? 'Statewide' : 'Countywide')
  return { office: squash(contest.office), place }
}
