import React from 'react'

export default function NoSuchElection({ electionId, activeHref }) {
  return (
    <main className="screen screen--app" style={{ padding: '60px 24px', textAlign: 'center' }}>
      <h1 className="display display--md">No such election</h1>
      <p className="copy" style={{ marginTop: 10 }}>
        This guide has no election called “{electionId}”.
      </p>
      <p className="copy" style={{ marginTop: 16 }}>
        <a href={activeHref}>Go to the current election’s guide →</a>
      </p>
    </main>
  )
}
