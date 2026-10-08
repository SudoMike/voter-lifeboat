import React, { useEffect, useMemo, useState } from 'react'
import Landing from './screens/Landing.jsx'
import Address from './screens/Address.jsx'
import Confirm from './screens/Confirm.jsx'
import Interview from './screens/Interview.jsx'
import Snapshot from './screens/Snapshot.jsx'
import Results from './screens/Results.jsx'
import DataPage from './screens/DataPage.jsx'
import Methodology from './screens/Methodology.jsx'
import ArchivedBanner from './screens/ArchivedBanner.jsx'
import ElectionNotice from './screens/ElectionNotice.jsx'
import NoSuchElection from './screens/NoSuchElection.jsx'
import { scopeMatches } from './lib/geo.js'
import {
  contestsOnBallot,
  measuresOnBallot,
  axesForBallot,
  interviewItemsForBallot,
} from './lib/scoring.js'
import { readHash, clearHash } from './lib/codec.js'
import { ElectionNotFound, electionIdFromPath, loadElection } from './lib/elections.js'

const BASE = import.meta.env.BASE_URL

export default function App() {
  const [site, setSite] = useState(null) // { index, election, data }
  const data = site?.data ?? null
  const [loadErr, setLoadErr] = useState(null)
  const [stage, setStage] = useState('landing')
  const [ballotContext, setBallotContext] = useState(null)
  const [answers, setAnswers] = useState(null)
  const [restored, setRestored] = useState(null) // profile that arrived via URL
  const [dataPage, setDataPage] = useState(location.hash === '#data')
  const [methodologyPage, setMethodologyPage] = useState(location.hash === '#methodology')

  // #data and #methodology overlay whatever stage the visitor is in; leaving
  // them returns the visitor to that stage.
  useEffect(() => {
    const onHash = () => {
      setDataPage(location.hash === '#data')
      setMethodologyPage(location.hash === '#methodology')
    }
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  // Routes: /washington-state serves the active election (or, for a report
  // link, the election the link was made for); /washington-state/<id> serves
  // that election.
  useEffect(() => {
    if (location.pathname === '/')
      history.replaceState(null, '', `${BASE}${location.search}${location.hash}`)
    const routeId = electionIdFromPath(location.pathname, BASE)
    const link = readHash()
    loadElection(BASE, { routeId, linkElectionId: link?.electionId })
      .then((loaded) => {
        // A report link for another election moves to that election's route,
        // so the link the results screen rewrites keeps pointing at it.
        if (!routeId && loaded.election.id !== loaded.index.active)
          history.replaceState(
            null,
            '',
            `${BASE}${loaded.election.id}${location.search}${location.hash}`
          )
        setSite(loaded)
      })
      .catch(setLoadErr)
  }, [])

  // index.html carries a generic title; name the election being served.
  useEffect(() => {
    if (data?.election?.name) document.title = `Voter Lifeboat — ${data.election.name}`
  }, [data])

  // Restore a shared/bookmarked report from the hash fragment.
  useEffect(() => {
    if (!data) return
    const p = readHash()
    if (p) {
      setBallotContext(p.context)
      setAnswers(p.answers)
      setRestored(p)
      setStage('results')
    }
  }, [data])

  const ballot = useMemo(() => {
    if (!data || !ballotContext) return null
    const contests = contestsOnBallot(data, ballotContext, scopeMatches)
    const measures = measuresOnBallot(data, ballotContext, scopeMatches)
    const axes = axesForBallot(data, contests, measures)
    const items = interviewItemsForBallot(data, axes)
    return { contests, measures, axes, items }
  }, [data, ballotContext])

  if (loadErr instanceof ElectionNotFound)
    return <NoSuchElection electionId={loadErr.electionId} activeHref={BASE} />
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

  const leaveOverlay = () => {
    history.replaceState(null, '', location.pathname)
    setDataPage(false)
    setMethodologyPage(false)
  }
  const archived = site.election.status === 'archived'
  const withBanner = (screen) => (
    <>
      {archived && <ArchivedBanner election={site.election} activeHref={BASE} />}
      {screen}
    </>
  )

  if (dataPage) return withBanner(<DataPage data={data} onBack={leaveOverlay} />)
  if (methodologyPage) return withBanner(<Methodology data={data} onBack={leaveOverlay} />)

  // An election with nothing researched yet gets a notice, not the guide.
  if (!data.contests.length && !data.measures.length && !restored)
    return withBanner(<ElectionNotice data={data} index={site.index} base={BASE} />)

  const startOver = () => {
    clearHash()
    setBallotContext(null)
    setAnswers(null)
    setRestored(null)
    setStage('landing')
  }

  return withBanner(renderStage())

  function renderStage() {
    switch (stage) {
      case 'landing':
        return (
          <Landing
            data={data}
            index={site.index}
            election={site.election}
            base={BASE}
            onStart={() => setStage('address')}
          />
        )
      case 'address':
        return (
          <Address
            onBack={() => setStage('landing')}
            data={data}
            onFound={(context) => {
              setBallotContext(context)
              setStage('confirm')
            }}
          />
        )
      case 'confirm':
        return (
          <Confirm
            data={data}
            context={ballotContext}
            ballot={ballot}
            onProceed={() => setStage('interview')}
            onRetry={() => {
              setBallotContext(null)
              setStage('address')
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
            election={site.election}
            ballotContext={ballotContext}
            answers={answers}
            restored={restored}
            onStartOver={startOver}
          />
        )
      default:
        return null
    }
  }
}
