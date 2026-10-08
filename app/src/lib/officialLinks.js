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
      // Snohomish County Auditor's general Local Voters' Pamphlet, from the
      // package pointer counties/snohomish/raw/snohomish/
      // local-voters-pamphlet.pdf.url. Checked 2026-10-08: 301 to
      // .../View/151457/Nov-3-2026-General-Pamphlet, then 200
      // application/pdf, 104 pages; PDF pages equal the printed page numbers.
      'snohomish/local-voters-pamphlet': 'https://www.snohomishcountywa.gov/DocumentCenter/View/151457',
      // SOS Edition 09 (Pierce), from the package pointer counties/pierce/
      // raw/sos/voters-pamphlet-edition-09-pierce.pdf.url; Pierce's dossiers
      // cite its federal and legislative statements. Checked 2026-10-08: 200
      // application/pdf, 64 pages, sha256 as in the pointer's meta; PDF
      // pages equal the printed page numbers (CD 6 pp. 24-25, LD 29 p. 43).
      'pierce/voters-pamphlet-edition-09-pierce':
        'https://www.sos.wa.gov/sites/default/files/2026-10/Voters%20Pamphlet%202026%20-%20Edition%2009%20-%20Pierce.pdf',
      // Clark County's general voters' pamphlet (the SOS state section and
      // Clark's local section in one PDF), from the package pointer
      // counties/clark/raw/clark/local-voters-pamphlet.pdf.url. Checked
      // 2026-10-08: 200 application/pdf, 112 pages, sha256 as in the
      // pointer's meta; PDF pages equal the printed page numbers (CD 3 p. 24,
      // Battle Ground SD Prop 11 p. 86). The local section (pp. 41-99) has no
      // text layer, so its pages were located by printed page number.
      'clark/local-voters-pamphlet':
        'https://clark.wa.gov/sites/default/files/media/document/2026-09/2026clarkcountygeneralvp_web.pdf',
      // Thurston County's general Local Voters' Pamphlet, from the package
      // pointer counties/thurston/raw/thurston/local-voters-pamphlet.pdf.url.
      // Checked 2026-10-08: 200 application/pdf (via S3), 30 pages, sha256
      // as in the pointer's meta. Citations are PDF pages, which run 46
      // behind the printed numbers (PDF p. 11 is printed p. 57, the Auditor
      // candidates; PDF p. 26 is printed p. 72, Yelm Prop 1).
      'thurston/local-voters-pamphlet': 'https://www.thurstoncountywa.gov/media/34849',
      // SOS Edition 27 (Thurston), from counties/thurston/raw/sos/
      // voters-pamphlet-edition-27-thurston.pdf.url (also statewide/interim/
      // pamphlet-editions.json); Thurston's dossiers cite its legislative and
      // Court of Appeals statements. Checked 2026-10-08: 200
      // application/pdf, 88 pages, sha256 as in the pointer's meta; PDF
      // pages equal the printed page numbers (LD 19 Pos. 1 p. 31, LD 22
      // Pos. 2 p. 36, Court of Appeals p. 46).
      'thurston/voters-pamphlet-edition-27-thurston':
        'https://www.sos.wa.gov/sites/default/files/2026-10/Voters%20Pamphlet%202026%20-%20Edition%2027%20-%20Thurston.pdf',
      // Skagit County's general Local Voters' Pamphlet, from the package
      // pointer counties/skagit/raw/skagit/local-voters-pamphlet.pdf.url
      // (#28). Checked 2026-10-08: 200 application/pdf, 23 pages, sha256 as
      // in the pointer's meta. Citations are PDF pages, which run 38 behind
      // the printed numbers (PDF p. 6 is printed p. 44, the Assessor; PDF
      // p. 18 is printed p. 56, Mount Vernon Prop 1).
      'skagit/local-voters-pamphlet': 'https://www.skagitcountywa.gov/media/nopbncyw/2026-11-03-vp-skagit.pdf',
      // Cowlitz County's general voters' pamphlet (Cowlitz's local section
      // combined with the SOS edition), from the package pointer
      // counties/cowlitz/raw/cowlitz/local-voters-pamphlet.pdf.url (#28).
      // Checked 2026-10-08: 200 application/pdf (via a redirect to
      // .../G126-Combined-Voters-Pamphlet_SOS), 72 pages, sha256 as in the
      // pointer's meta; PDF pages equal the printed page numbers (Superior
      // Court Pos. 4 p. 37, Clerk p. 47, Longview Prop 1 pp. 57-58).
      'cowlitz/local-voters-pamphlet':
        'https://www.co.cowlitz.wa.us/DocumentCenter/View/39451/G126-Combined-Voters-Pamplet_SOS',
      // Chelan, Clallam and Franklin general Local Voters' Pamphlets (#29),
      // from each package's pointer counties/<county>/raw/<county>/
      // local-voters-pamphlet.pdf.url. Checked 2026-10-08: each 200
      // application/pdf with the sha256 in the pointer's meta. Citations are
      // PDF pages. Chelan: 24 pages (candidates pp. 6-15, Wenatchee SD 246
      // pp. 16-17, Cashmere p. 18). Clallam: the printed combined state and
      // local pamphlet, 72 pages (District Court 1 p. 55, QVSD p. 58, FD 6
      // pp. 62-63). Franklin: 16 pages, printed pp. 43-58 (Assessor PDF p. 5,
      // FPD 3 p. 16).
      'chelan/local-voters-pamphlet':
        'https://www.co.chelan.wa.us/files/elections/documents/election/2026%20November%203%20General%20Election%20LVP.pdf',
      'clallam/local-voters-pamphlet': 'https://www.clallamcountywa.gov/DocumentCenter/View/29375/2026-General-Voter-Pamphlet',
      'franklin/local-voters-pamphlet':
        'https://www.franklincountywa.gov/DocumentCenter/View/4553/2611-Franklin-County-Voters-Pamphlet-',
      // Jefferson and Kittitas general Local Voters' Pamphlets (#31), from each
      // package's raw/<county>/local-voters-pamphlet.pdf.url. Checked
      // 2026-10-08: each 200 application/pdf with the pointer's sha256 (with a
      // browser User-Agent; Jefferson's DocumentCenter link 301s to
      // .../25551/Jeffco-Voter-Guide-2026_General_WEB first). PDF page numbers
      // equal the printed ones. Jefferson: 16 pages (candidates pp. 6-12,
      // measures pp. 14-15). Kittitas: 12 pages (candidates pp. 4-11, no
      // measures).
      'jefferson/local-voters-pamphlet': 'https://www.co.jefferson.wa.us/DocumentCenter/View/25551',
      'kittitas/local-voters-pamphlet':
        'https://www.co.kittitas.wa.us/uploads/auditor/elections/voters-pamphlet//General%20Pamphlet.pdf',
      // Klickitat and Asotin general voters' pamphlets (#31), from each
      // package's raw/<county>/local-voters-pamphlet.pdf.url. Checked
      // 2026-10-08: each 200 application/pdf with the pointer's sha256 (with a
      // browser User-Agent; Klickitat's DocumentCenter link redirects to
      // .../23954/2026-General-Election-Voters-Pamphlet). Klickitat: the SOS
      // state pamphlet bound with the local one, 72 PDF pages, PDF page =
      // printed page (Court of Appeals p. 37, candidates pp. 46-55, EMS
      // measure p. 56). Asotin: the local pamphlet alone, 12 PDF pages,
      // printed pp. 37-48; citations are PDF pages (Assessor p. 3, PUD p. 11,
      // Rural EMS levy p. 12).
      'klickitat/local-voters-pamphlet': 'https://www.klickitatcounty.gov/DocumentCenter/View/23954',
      'asotin/local-voters-pamphlet':
        'https://www.asotincountywa.gov/DocumentCenter/View/18054/2026GeneralElectionLocalVotersPamphlet-_Asotin-82726',
      // Mason general Local Voters' Pamphlet (#30), from the package's pointer
      // counties/mason/raw/mason/local-voters-pamphlet.pdf.url. Checked
      // 2026-10-08: 302 to cms2.revize.com, then 200 application/pdf with the
      // pointer's sha256; 32 PDF pages (candidates pp. 10-22, measures pp.
      // 24-30).
      'mason/local-voters-pamphlet':
        'https://www.masoncountywa.gov/Documents/Departments/Auditor/Elections/Current%20Election/General_2026_Local_Voters_Pamphlet.pdf',
      // Walla Walla general Local Voters' Pamphlet (#30), from the package's
      // pointer counties/walla-walla/raw/walla-walla/local-voters-pamphlet.pdf.url.
      // Checked 2026-10-08: redirect to cms7files.revize.com, then 200
      // application/pdf with the pointer's sha256; 28 PDF pages, PDF page
      // numbers equal the printed ones (candidates pp. 11-20, measures pp.
      // 22-25).
      'walla-walla/local-voters-pamphlet': 'https://www.wwcowa.gov/November%20General%202026-%20Final.pdf',
      // Whitman general Official Local Voters' Pamphlet (#30), from the
      // package's pointer counties/whitman/raw/whitman/local-voters-pamphlet.pdf.url.
      // Checked 2026-10-08: redirect to .../12618/Whitman-County-LVP-NOV-2026-WebV1,
      // then 200 application/pdf with the pointer's sha256; 32 PDF pages, PDF
      // page numbers equal the printed ones (candidates pp. 5-11, measures
      // pp. 12-31).
      'whitman/local-voters-pamphlet': 'https://www.whitmancounty.gov/DocumentCenter/View/12618',
      // Skamania general Local Voters' Pamphlet (#32), from the package's
      // pointer counties/skamania/raw/skamania/local-voters-pamphlet.pdf.url.
      // skamaniacounty.gov's front end answers 403 to a bare scripted
      // User-Agent; checked 2026-10-08 with full browser request headers
      // (Chrome User-Agent, Accept, Accept-Language, Sec-Fetch-*): 200
      // application/pdf with the pointer's sha256, 10 PDF pages printed as
      // pp. 35-44. Citations are PDF pages, which run 34 behind the printed
      // numbers (PDF p. 6 is printed p. 40, the Assessor; PDF p. 10 is
      // printed p. 44, District Court and PUD).
      'skamania/local-voters-pamphlet':
        'https://www.skamaniacounty.gov/home/showpublisheddocument/19600/639253463106470000',
      // San Juan's combined state and county voters' pamphlet (#32), from the
      // package's pointer counties/san-juan/raw/san-juan/
      // local-voters-pamphlet.pdf.url. Checked 2026-10-08: redirect to
      // .../36027/2026-General-VP-San-Juan-County---Final-State-and-County,
      // then 200 application/pdf with the pointer's sha256; 72 PDF pages, PDF
      // page numbers equal the printed ones (Assessor p. 42, Fire District 4
      // levy p. 50, Lopez Solid Waste levy p. 56).
      'san-juan/local-voters-pamphlet': 'https://www.sanjuancountywa.gov/DocumentCenter/View/36027',
      // Lincoln County Local Voters' Pamphlet (#32), from the package's pointer
      // counties/lincoln/raw/lincoln/local-voters-pamphlet.pdf.url. Checked
      // 2026-10-08: 301 to .../2055/2026-General-LVP-Final-PDF, then 200
      // application/pdf with the pointer's sha256; 8 PDF pages, PDF page
      // numbers equal the printed ones (candidates pp. 4-6: Assessor p. 4,
      // District Court p. 6).
      'lincoln/local-voters-pamphlet': 'https://www.lincolncountywa.com/DocumentCenter/View/2055',
      // Pend Oreille County Local Voters' Pamphlet (#32), from the package's
      // pointer counties/pend-oreille/raw/pend-oreille/local-voters-pamphlet.pdf.url.
      // Checked 2026-10-08: 200 application/pdf with the pointer's sha256; 19
      // PDF pages printed as pp. 39-57. Citations are PDF pages, which run 38
      // behind the printed numbers (PDF p. 14 is printed p. 52, Hospital
      // District No. 1; PDF p. 18 is printed p. 56, Sacheen Lake W/S District).
      'pend-oreille/local-voters-pamphlet':
        'https://www.pendoreille.gov/sites/g/files/vyhlif14901/files/media/auditor/file/34071/final_vp_general_2026_pend_oreille.pdf',
    },
    // Counties whose research cites VoteWA's online voters' guide, which has
    // no page numbers, instead of a printed pamphlet: their records carry no
    // pamphlet_pages, so a link goes to the county's guide. Spokane's
    // dossiers cite voter.votewa.gov candidate.ashx / measure.ashx pages
    // (spokanecounty.gov answered 403 to scripted requests, so no local
    // pamphlet PDF was fetched). Checked 2026-10-08: 200 text/html.
    // Pierce's county offices, District Court and local measures cite VoteWA
    // too (piercecountywa.gov answered 403, so its local pamphlet was not
    // fetched); its federal and legislative statements cite Edition 09
    // above. Checked 2026-10-08: 200 text/html.
    // Kitsap's dossiers cite VoteWA only (kitsap.gov answered 403 to scripted
    // requests for its pamphlet PDFs). A few Clark dossiers cite VoteWA
    // records rather than the printed pamphlet; Clark's guide is their
    // fallback. Checked 2026-10-08: both 200 text/html.
    // Yakima, Whatcom and Benton dossiers cite VoteWA only (#28): Benton
    // publishes its general pamphlet only as this guide, whatcomcounty.us
    // answered 403 to scripted requests, and no Yakima dossier cites a page
    // of SOS Edition 01. Checked 2026-10-08: each 200 text/html.
    // Grant dossiers cite VoteWA only (Grant prints no local pamphlet);
    // every Skagit and Cowlitz dossier cites a page of its local pamphlet
    // above, and their guides link any record without a page (#28).
    // Checked 2026-10-08: each 200 text/html.
    // Island and Lewis dossiers cite VoteWA only (#29): neither county prints
    // a general pamphlet, and each Auditor links this guide as its own.
    // Checked 2026-10-08: both 200 text/html.
    // Chelan's Court of Appeals record and Clallam's measure records cite
    // VoteWA as well as their pamphlets; Franklin's cite the pamphlet only,
    // and its guide links any record without a page. Grays Harbor's dossiers
    // cite VoteWA only: the county posts no printed pamphlet (#29). Checked
    // 2026-10-08: each 200 text/html.
    countyGuides: {
      spokane: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=32',
      pierce: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=27',
      kitsap: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=18',
      clark: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=06',
      yakima: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=39',
      whatcom: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=37',
      benton: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=03',
      skagit: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=29',
      cowlitz: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=08',
      grant: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=13',
      island: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=15',
      lewis: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=21',
      franklin: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=11',
      chelan: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=04',
      clallam: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=05',
      'grays-harbor': 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=14',
      // Mason's dossiers cite the pamphlet and VoteWA's guide records; the
      // Auditor links this guide as its "Voter Guide Portal" (#30; 200
      // text/html, 2026-10-08).
      mason: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=23',
      // Walla Walla's Court of Appeals record cites VoteWA's guide (its
      // pamphlet does not print the race); Stevens's dossiers cite VoteWA
      // only (stevenscountywa.gov answered 403 to scripted requests, and no
      // printed general pamphlet was found). #30; each 200 text/html,
      // 2026-10-08.
      'walla-walla': 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=36',
      stevens: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=33',
      // Whitman's eight measures that filed hardship waivers, and its records
      // whose candidates printed no statement, appear only in VoteWA's guide;
      // Douglas prints no local pamphlet and its dossiers cite VoteWA only.
      // #30; each 200 text/html, 2026-10-08.
      whitman: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=38',
      douglas: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=09',
      // Jefferson's and Kittitas's dossiers cite their local pamphlets and
      // VoteWA's guide records; the guide links any record without a page
      // (CD, LD and Court of Appeals seats are not in either local pamphlet).
      // #31; each 200 text/html, 2026-10-08.
      jefferson: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=16',
      kittitas: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=19',
      // Okanogan prints no local pamphlet; its dossiers cite VoteWA only.
      // #30; 200 text/html, 2026-10-08.
      okanogan: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=24',
      // Klickitat's and Asotin's dossiers cite their pamphlets and VoteWA's
      // guide records; the guide links any record without a page (Asotin's
      // CD, LD and Court of Appeals seats). Pacific's dossiers cite VoteWA
      // only: the county's site (co.pacific.wa.us) did not answer on
      // 2026-10-08, and its local pamphlet is not posted online. #31; each
      // 200 text/html, 2026-10-08.
      klickitat: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=20',
      pacific: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=25',
      asotin: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=02',
      // Adams prints no local pamphlet; its dossiers cite VoteWA only. #31;
      // 200 text/html, 2026-10-08.
      adams: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=01',
      // Skamania's and San Juan's dossiers cite their pamphlets and VoteWA's
      // guide records; the guide links any record without a page (CD, LD and
      // Court of Appeals seats). #32; each 200 text/html, 2026-10-08.
      skamania: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=30',
      'san-juan': 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=28',
      // Lincoln's and Pend Oreille's guides link any record without a page
      // (CD, LD, Court of Appeals and Superior Court seats). #32; each 200
      // text/html, 2026-10-08.
      lincoln: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=22',
      'pend-oreille': 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=26',
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
 * page when the election knows the edition, else the owner's online county
 * voters' guide (countyGuides), else the election's pamphlet index (unpaged),
 * else null. With no pages, only an owner's county guide.
 */
export function pamphletLink(pages, owner, electionId) {
  const guide = electionGuide({ id: electionId })
  const countyGuide = guide.countyGuides?.[owner] || null
  if (!pages?.length) return countyGuide
  for (const p of pages) {
    const url =
      guide.pamphletPdfs[`${owner}/${p.edition}`] ||
      (guide.fallbackOwner && guide.pamphletPdfs[`${guide.fallbackOwner}/${p.edition}`])
    if (url) return `${url}#page=${p.page}`
  }
  return countyGuide || guide.pamphletIndex || null
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
