import React, { useEffect, useMemo, useState } from 'react'
import Landing from './screens/Landing.jsx'
import Address from './screens/Address.jsx'
import Interview from './screens/Interview.jsx'
import Snapshot from './screens/Snapshot.jsx'
import Results from './screens/Results.jsx'
import { scopeMatches } from './lib/geo.js'
import {
  contestsOnBallot,
  measuresOnBallot,
  axesForBallot,
  interviewItemsForBallot,
} from './lib/scoring.js'
import { readHash, clearHash } from './lib/codec.js'

export default function App() {
  const [data, setData] = useState(null)
  const [loadErr, setLoadErr] = useState(null)
  const [stage, setStage] = useState('landing')
  const [districts, setDistricts] = useState(null)
  const [answers, setAnswers] = useState(null)
  const [restored, setRestored] = useState(null) // profile that arrived via URL

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}data/app-data.json`)
      .then((r) => {
        if (!r.ok) throw new Error(`data ${r.status}`)
        return r.json()
      })
      .then(setData)
      .catch((e) => setLoadErr(String(e)))
  }, [])

  // Restore a shared/bookmarked report from the hash fragment.
  useEffect(() => {
    if (!data) return
    const p = readHash()
    if (p) {
      setDistricts(p.districts)
      setAnswers(p.answers)
      setRestored(p)
      setStage('results')
    }
  }, [data])

  const ballot = useMemo(() => {
    if (!data || !districts) return null
    const contests = contestsOnBallot(data, districts, scopeMatches)
    const measures = measuresOnBallot(data, districts, scopeMatches)
    const axes = axesForBallot(data, contests, measures)
    const items = interviewItemsForBallot(data, axes)
    return { contests, measures, axes, items }
  }, [data, districts])

  if (loadErr)
    return (
      <main className="screen screen--app" style={{ padding: '60px 24px', textAlign: 'center' }}>
        <h1 className="display display--md">Something ran aground</h1>
        <p className="copy" style={{ marginTop: 10 }}>
          The guide's data failed to load. Refresh to try again.
        </p>
      </main>
    )
  if (!data)
    return (
      <main className="screen screen--app" style={{ padding: '80px 24px', textAlign: 'center' }}>
        <div className="bar bar--busy" style={{ width: 150, margin: '0 auto' }}>
          <i />
        </div>
      </main>
    )

  const startOver = () => {
    clearHash()
    setDistricts(null)
    setAnswers(null)
    setRestored(null)
    setStage('landing')
  }

  switch (stage) {
    case 'landing':
      return <Landing data={data} onStart={() => setStage('address')} />
    case 'address':
      return (
        <Address
          onBack={() => setStage('landing')}
          onFound={(d) => {
            setDistricts(d)
            setStage('interview')
          }}
        />
      )
    case 'interview':
      return (
        <Interview
          data={data}
          items={ballot.items}
          onDone={(a) => {
            setAnswers(a)
            setStage('snapshot')
          }}
        />
      )
    case 'snapshot':
      return (
        <Snapshot data={data} answers={answers} onShow={() => setStage('results')} />
      )
    case 'results':
      return (
        <Results
          data={data}
          districts={districts}
          answers={answers}
          restored={restored}
          onStartOver={startOver}
        />
      )
    default:
      return null
  }
}
