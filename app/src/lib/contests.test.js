import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { contestHeading } from './contests.js'

const load = (id) =>
  JSON.parse(readFileSync(new URL(`../../public/data/${id}/app-data.json`, import.meta.url), 'utf8'))
const general = load('2026-11-03-general')
const primary = load('2026-08-04-primary')
const bySlug = (data, slug) => {
  const c = data.contests.find((x) => x.slug === slug)
  assert.ok(c, `missing contest ${slug}`)
  return c
}

test('King legislative seats read office first, with a clean district number', () => {
  assert.deepEqual(contestHeading(bySlug(general, 'state-senator-legislative-district-no-46')), {
    office: 'State Senator',
    place: 'Legislative District 46',
  })
  const rep = general.contests.find(
    (c) => c.scope?.layer === 'LEGDST' && c.scope.value === '46' && /Position No\. 1/.test(c.district)
  )
  assert.deepEqual(contestHeading(rep), {
    office: 'State Representative Position No. 1',
    place: 'Legislative District 46',
  })
})

test('King District Court seats name the court and the electoral district', () => {
  assert.deepEqual(contestHeading(bySlug(general, 'judge-position-no-5-southwest-electoral-district')), {
    office: 'Judge Position No. 5',
    place: 'King County District Court, Southwest Electoral District',
  })
})

test('King city and council seats put the seat before the jurisdiction', () => {
  const seattle = general.contests.find((c) => c.scope?.layer === 'SCCDST')
  assert.deepEqual(contestHeading(seattle), { office: 'Council District No. 5', place: 'City of Seattle' })
  const kcc = general.contests.find((c) => c.scope?.layer === 'KCCDST')
  assert.deepEqual(contestHeading(kcc), {
    office: kcc.district,
    place: 'Metropolitan King County',
  })
})

test('contests without a district read as countywide or statewide', () => {
  assert.deepEqual(contestHeading(bySlug(general, 'prosecuting-attorney')), {
    office: 'Prosecuting Attorney',
    place: 'Countywide',
  })
  assert.equal(contestHeading({ office: 'Governor', district: '', scope: { kind: 'STATEWIDE' } }).place, 'Statewide')
})

test('the primary archive renders the same King contest kinds the same way', () => {
  const senator = primary.contests.find(
    (c) => c.owner === 'king' && c.scope?.layer === 'LEGDST' && c.scope.value === '46' && c.district === 'State Senator'
  )
  assert.deepEqual(contestHeading(senator), { office: 'State Senator', place: 'Legislative District 46' })
  const court = primary.contests.find((c) => c.owner === 'king' && c.scope?.layer === 'JUDDST')
  assert.deepEqual(contestHeading(court), {
    office: 'Judge Position No. 1',
    place: 'King County District Court, Northeast Electoral District',
  })
})

test('every shipped contest outside the King office-district swap keeps its fields as-is', () => {
  for (const data of [general, primary]) {
    for (const c of data.contests) {
      const h = contestHeading(c)
      assert.ok(h.office && h.place, `${data.election.id} ${c.slug} has an empty heading part`)
      assert.doesNotMatch(`${h.office} ${h.place}`, /\s{2}/, `${c.slug} keeps a double space`)
      const squash = (s) => String(s || '').replace(/\s+/g, ' ').trim()
      if (c.owner !== 'king') {
        assert.equal(h.office, squash(c.office), `${data.election.id} ${c.slug} (${c.owner}) should not be rewritten`)
        if (c.district) assert.equal(h.place, squash(c.district))
      }
      // No King contest should still lead with the jurisdiction.
      assert.doesNotMatch(h.office, /^(Legislative District|City of|Metropolitan King County|\w+ Electoral District)/,
        `${data.election.id} ${c.slug} still leads with a jurisdiction`)
    }
  }
})
