import React from 'react'
import { formatElectionDay } from '../lib/elections.js'

// results.vote.wa.gov (the address the Secretary of State publicizes) 301s
// here; link the final URL.
export const OFFICIAL_RESULTS_URL = 'https://results.votewa.gov/results/public/washington'

// Shown above every screen while an archived election is being served.
export default function ArchivedBanner({ election, activeHref }) {
  return (
    <div className="banner-tcc archived-banner" role="status">
      This election ended {formatElectionDay(election.day)}. Official results:{' '}
      <a href={OFFICIAL_RESULTS_URL} target="_blank" rel="noopener noreferrer">
        results.votewa.gov
      </a>
      {activeHref && (
        <>
          {' · '}
          <a href={activeHref}>Current election</a>
        </>
      )}
    </div>
  )
}
