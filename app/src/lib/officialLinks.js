// Official election sources the app links to, and the small amount of copy
// that differs between a primary and a general. Keyed by the app-data
// `election.id` so an archived election keeps its own links and wording.
// Every URL here was checked live (HTTP 200) when it was added.

// VoteWA: registration, ballot status, and a personalized drop box list.
// https://www.vote.wa.gov redirects here.
export const VOTEWA_URL = 'https://voter.votewa.gov/'

// The Secretary of State's statewide drop box and voting center map.
export const DROP_BOX_URL =
  'https://www.sos.wa.gov/elections/voters/voter-registration/drop-box-and-voting-center-locations'

// The Secretary of State's directory of all 39 county elections offices.
export const COUNTY_OFFICES_URL =
  'https://www.sos.wa.gov/elections/voters/voter-registration/county-elections-offices'

// Every past and present state voters' pamphlet.
const SOS_PAMPHLET_ARCHIVE =
  'https://www.sos.wa.gov/elections/data-research/election-data-and-maps/election-results-and-voters-pamphlets'

const SOS_GENERAL_2026 = `${SOS_PAMPHLET_ARCHIVE}/2026-general-election-voters-guide`

const ELECTIONS = {
  '2026-08-04-primary-special': {
    kind: 'primary',
    statePamphlet: {
      label: 'King County source pamphlets',
      url: 'https://kingcounty.gov/en/dept/elections/how-to-vote/voters-pamphlet',
      site: 'kingcounty.gov',
    },
    resultsNote: 'WA primaries send the top 2 to November, regardless of party.',
    // Pamphlet PDFs by `<owner>/<edition>`; statewide contests cite King's.
    pamphletPdfs: {
      'king/edition-1':
        'https://cdn.kingcounty.gov/-/media/king-county/depts/elections/how-to-vote/voters-pamphlets/2026/08/english/edition-1.pdf',
      'king/edition-2':
        'https://cdn.kingcounty.gov/-/media/king-county/depts/elections/how-to-vote/voters-pamphlets/2026/08/english/edition-2.pdf',
      'clark/local-voters-pamphlet':
        'https://clark.wa.gov/sites/default/files/media/document/2026-06/2026clarkcountyprimaryvp_web.pdf',
      'kitsap/local-voters-pamphlet': 'https://www.kitsap.gov/auditor/Documents/LVP.pdf',
      'pierce/local-voters-pamphlet':
        'https://www.piercecountywa.gov/DocumentCenter/View/158538/Primary-2026-VP-Final',
      'snohomish/local-voters-pamphlet':
        'https://www.snohomishcountywa.gov/DocumentCenter/View/149774',
      'spokane/local-voters-pamphlet':
        'https://www.spokanecounty.gov/DocumentCenter/View/72507/August-4-2026-Primary-Election-Voters-Pamphlet-PDF',
      'thurston/local-voters-pamphlet': 'https://www.thurstoncountywa.gov/media/33642',
    },
    fallbackOwner: 'king',
  },
  '2026-11-03-general': {
    kind: 'general',
    statePamphlet: {
      label: "the state voters' pamphlet",
      url: SOS_GENERAL_2026,
      site: 'sos.wa.gov',
    },
    resultsNote: null,
    // Statewide contests cite the SOS edition they were extracted from
    // (data/washington-state/elections/2026-11-03-general/statewide/interim/
    // pamphlet-editions.json, `statewide_reference_edition`). Editions not
    // listed here link the SOS pamphlet PDFs page without a page anchor.
    // King contests cite their own edition ids: KCE's local pamphlet and the
    // three SOS editions mailed in King County, named after the King
    // package's raw pointers (counties/king/raw/{pamphlet,sos}/*.pdf.url; the
    // URLs are copied from them, %C2%A0 included). Pages are PDF pages.
    pamphletPdfs: {
      'statewide/edition-06':
        'https://www.sos.wa.gov/sites/default/files/2026-10/Voters%20Pamphlet%202026%20-%20Edition%2006%20-%20King%20-%20South%20and%20Southeast.pdf',
      'king/local-edition':
        'https://cdn.kingcounty.gov/-/media/king-county/depts/elections/how-to-vote/voters-pamphlets/2026/11/local-edition.pdf',
      'king/voters-pamphlet-edition-04-king-seattle':
        'https://www.sos.wa.gov/sites/default/files/2026-10/Voters%20Pamphlet%202026%20-%20Edition%2004%C2%A0-%20King%20-%20Seattle.pdf',
      'king/voters-pamphlet-edition-05-king-north-eastside':
        'https://www.sos.wa.gov/sites/default/files/2026-10/Voters%20Pamphlet%202026%20-%20Edition%2005%C2%A0-%20King%20-%20North%20and%20Eastside.pdf',
      'king/voters-pamphlet-edition-06-king-south-southeast':
        'https://www.sos.wa.gov/sites/default/files/2026-10/Voters%20Pamphlet%202026%20-%20Edition%2006%20-%20King%20-%20South%20and%20Southeast.pdf',
    },
    pamphletIndex: `${SOS_GENERAL_2026}/2026-voters-pamphlet-pdfs`,
  },
}

const UNKNOWN = {
  kind: null,
  statePamphlet: { label: "the state voters' pamphlet", url: SOS_PAMPHLET_ARCHIVE, site: 'sos.wa.gov' },
  resultsNote: null,
  pamphletPdfs: {},
}

/** Links and kind-specific copy for one election (`data.election`). */
export function electionGuide(election) {
  return ELECTIONS[election?.id] || UNKNOWN
}

/**
 * The official pamphlet page a citation points at: the edition's PDF at that
 * page when the election knows the edition, else the election's pamphlet
 * index (unpaged), else null.
 */
export function pamphletLink(pages, owner, electionId) {
  if (!pages?.length) return null
  const guide = electionGuide({ id: electionId })
  for (const p of pages) {
    const url =
      guide.pamphletPdfs[`${owner}/${p.edition}`] ||
      (guide.fallbackOwner && guide.pamphletPdfs[`${guide.fallbackOwner}/${p.edition}`])
    if (url) return `${url}#page=${p.page}`
  }
  return guide.pamphletIndex || null
}

/**
 * The voter's county elections office: the county's own site when
 * `coverage.supported_counties` carries an `elections_url`, otherwise the
 * SOS directory of county offices. Null when the county is unknown.
 */
export function countyElectionsOffice(data, county) {
  if (!county?.id || !county?.name) return null
  const entry = data?.coverage?.supported_counties?.find((c) => c.id === county.id)
  return {
    name: `${county.name} Elections`,
    url: entry?.elections_url || COUNTY_OFFICES_URL,
    direct: Boolean(entry?.elections_url),
  }
}
