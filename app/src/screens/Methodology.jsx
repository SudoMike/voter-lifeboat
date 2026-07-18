// How the guide is built, in the guide's own words. Everything here is
// descriptive of the offline pipeline (data/ + pipeline/) and the client-side
// alignment math (lib/scoring.js) — there is no runtime AI. The rubric section
// renders live from the shipped data so it can never drift from what ships.

import React from 'react'
import GitHubLink from './GitHubLink.jsx'

function Section({ eyebrow, title, children }) {
  return (
    <section style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
      {eyebrow && <div className="eyebrow">{eyebrow}</div>}
      {title && <h2 className="display display--md">{title}</h2>}
      {children}
    </section>
  )
}

// One numbered stage of the offline pipeline.
function Stage({ n, title, children }) {
  return (
    <div className="panel" style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
      <div className="trust-icon" style={{ background: 'var(--navy)', flex: 'none' }}>
        {n}
      </div>
      <div>
        <div style={{ fontWeight: 800, fontSize: 14 }}>{title}</div>
        <p className="copy" style={{ fontSize: 13, marginTop: 4 }}>
          {children}
        </p>
      </div>
    </div>
  )
}

function AxisRow({ axis }) {
  return (
    <div className="panel" style={{ padding: '12px 14px' }}>
      <div style={{ fontWeight: 800, fontSize: 14 }}>{axis.title}</div>
      {axis.tension && (
        <p className="copy" style={{ fontSize: 12.5, marginTop: 4 }}>
          {axis.tension}
        </p>
      )}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          gap: 10,
          fontSize: 11,
          fontWeight: 800,
          color: 'var(--muted-deep)',
          marginTop: 8,
        }}
      >
        <span>← {axis.pole_a?.label}</span>
        <span style={{ textAlign: 'right' }}>{axis.pole_b?.label} →</span>
      </div>
    </div>
  )
}

export default function Methodology({ data, onBack }) {
  const axes = data?.rubric?.axes || []
  const scale = data?.rubric?.scale
  const electionName = data?.election?.name || 'the active election'

  return (
    <main className="screen screen--app screen--wide rise" style={{ paddingBottom: 0 }}>
      <header style={{ padding: '22px 24px 0' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div className="brand">
            <div className="buoy" />
            <div className="brand-name">Voter Lifeboat</div>
          </div>
          <GitHubLink />
        </div>
        <div className="eyebrow" style={{ marginTop: 22 }}>
          How this guide is built
        </div>
        <h1 className="display display--lg" style={{ marginTop: 6 }}>
          Methodology
        </h1>
        <p className="copy" style={{ fontSize: 14, marginTop: 8 }}>
          Every candidate score, measure lean, and interview question in Voter
          Lifeboat was produced by AI, offline, and published with its sources
          attached. This page walks through exactly how — the rubric, the
          research, the scoring, and the arithmetic that lines your values up
          against the ballot. We make <strong>no accuracy claims</strong>. The
          citations are the check, and this page is the map for checking them.
        </p>
        <button className="linkish" style={{ fontSize: 12, marginTop: 8 }} onClick={onBack}>
          ← back to the guide
        </button>
      </header>

      <div
        style={{
          padding: '18px 24px 26px',
          display: 'flex',
          flexDirection: 'column',
          gap: 26,
        }}
      >
        {/* ---- principles ---- */}
        <Section eyebrow="What guides the whole thing" title="Four commitments">
          <div className="panel trust-row">
            <div className="trust-icon" style={{ background: 'var(--seafoam)' }}>
              1
            </div>
            <div>
              <strong>No runtime AI.</strong> All AI work happens once, offline,
              in the build pipeline. What ships to your browser is a fixed data
              file plus transparent arithmetic. The site never phones an AI
              model while you use it, so the same answers always produce the
              same result.
            </div>
          </div>
          <div className="panel trust-row">
            <div className="trust-icon" style={{ background: 'var(--coral)' }}>
              2
            </div>
            <div>
              <strong>Citations are the check.</strong> Because the whole guide
              is AI-built, we don't ask you to trust it. Every axis score on a
              candidate or measure carries its sources and a confidence level,
              shown in the results so you can verify each claim yourself.
            </div>
          </div>
          <div className="panel trust-row">
            <div className="trust-icon" style={{ background: 'var(--amber)' }}>
              3
            </div>
            <div>
              <strong>Radical transparency.</strong> The rubric, the dossiers,
              the scores, the scoring code, and this pipeline are all in the
              open. Verification lives in the pipeline itself — a scoring pass
              is checked, and separately <em>refuted</em>, before it's trusted.
            </div>
          </div>
          <div className="panel trust-row">
            <div className="trust-icon" style={{ background: 'var(--navy)' }}>
              4
            </div>
            <div>
              <strong>No recommendations.</strong> The guide reports alignment,
              not endorsements. It shows how each candidate or measure sits
              relative to <em>your</em> stated values and never tells you how to
              vote.
            </div>
          </div>
        </Section>

        {/* ---- the rubric ---- */}
        <Section eyebrow="Step one" title="The rubric">
          <p className="copy" style={{ fontSize: 13.5 }}>
            Everything is scored against one fixed rubric: a set of{' '}
            <strong>{axes.length} issue axes</strong>. Each axis is a real
            tension that recurs across the {electionName} ballot — a spectrum
            running between two honestly-stated poles, not a partisan label. The
            axes
            were derived from the actual contests on the ballot: the dividing
            lines that kept showing up across candidate statements, voting
            records, and measures. Candidates and measures are scored on these
            axes; you are interviewed on the same axes. That shared vocabulary
            is what makes an alignment number meaningful.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {axes.map((a) => (
              <AxisRow key={a.id} axis={a} />
            ))}
          </div>
          {scale?.description && (
            <div className="dashed-note">
              <strong>The scale.</strong> {scale.description}
            </div>
          )}
        </Section>

        {/* ---- the pipeline ---- */}
        <Section eyebrow="Step two" title="From sources to scores">
          <p className="copy" style={{ fontSize: 13.5 }}>
            For every candidate and measure on a covered ballot, the offline
            pipeline runs the same stages. Each stage is a script in{' '}
            <code>pipeline/</code>; each leaves its output in <code>data/</code>{' '}
            for the next stage and for anyone auditing.
          </p>
          <Stage n="1" title="Ingest the official ballot">
            The list of real contests, candidates, and measures for a ballot
            context is parsed from official election sources — the state and
            county voters' pamphlets and ballot data — so the guide only ever
            scores things that are actually on a voter's ballot.
          </Stage>
          <Stage n="2" title="Compile a dossier per candidate & measure">
            A research agent compiles a dossier for each candidate and measure:
            its pamphlet statement plus the public record — filings, voting
            records, endorsements, news, and prior statements. Every factual
            sentence must cite a source — <em>no source, no claim</em>. Social
            media, opposition sites, anonymous posts, and personal blogs are
            excluded entirely.
          </Stage>
          <Stage n="3" title="Score each axis, with citations">
            A second agent — working <strong>only from the dossier, with no web
            access</strong> — places each candidate on every applicable axis
            from −2 to +2. Every score carries the dossier citations that
            support it, a one-line basis, and a confidence level. Where the
            dossier has no evidence for an axis, that axis is{' '}
            <strong>omitted, not guessed</strong>. A measure instead gets a
            mapping of which axes a <em>yes</em> vote leans toward.
          </Stage>
          <Stage n="4" title="Refute — a separate adversarial pass">
            A <strong>different agent</strong>, also with no web access,
            re-reads each dossier and tries to <em>refute</em> every score:
            wrong direction, overstated confidence, a citation that doesn't
            actually support the number, an inapplicable axis, missed contrary
            evidence. Each candidate-axis pair gets a verdict — upheld,
            adjusted, or refuted — and refuted scores are dropped. Keeping
            research, scoring, and refutation in separate agents is the
            transparency guarantee. (In the project history, the
            &ldquo;refute&rdquo; and &ldquo;review&rdquo; commits are this step,
            run county by county.)
          </Stage>
          <Stage n="5" title="Validate the whole set">
            An automated validation pass checks the assembled scores for
            structural soundness — every score in range, every non-low score
            carrying citations, no dangling axes — before anything is merged.
          </Stage>
          <Stage n="6" title="Assemble the app data">
            The validated dossiers, scores, rubric, and interview are merged and
            assembled into the single data file the app loads. That file is all
            the browser ever needs.
          </Stage>
        </Section>

        {/* ---- sourcing & confidence ---- */}
        <Section eyebrow="How much to trust a score" title="Sources & evidence">
          <p className="copy" style={{ fontSize: 13.5 }}>
            Not every source counts the same, and not every score is equally
            well-backed. Both are shown, never hidden.
          </p>
          <div className="panel">
            <div style={{ fontWeight: 800, fontSize: 14 }}>Source tiers</div>
            <p className="copy" style={{ fontSize: 13, marginTop: 4 }}>
              <strong>Tier 1</strong> — pamphlet statements, candidate-owned
              sources, official filings, and voting records: the primary record.{' '}
              <strong>Tier 2</strong> — endorsements and established news
              reporting: corroborating, but secondhand. Each source in a
              dossier is tagged with its tier so you can weigh it.
            </p>
          </div>
          <div className="panel">
            <div style={{ fontWeight: 800, fontSize: 14 }}>Evidence level</div>
            <p className="copy" style={{ fontSize: 13, marginTop: 4 }}>
              Each candidate carries an overall evidence level — how much
              sourcing backs their scores. A well-documented incumbent reads{' '}
              <span className="evidence evidence--rich">rich</span>; one with a
              website and endorsements reads{' '}
              <span className="evidence evidence--mod">moderate</span>; a
              first-time candidate with nothing beyond the pamphlet reads{' '}
              <span className="evidence evidence--thin">pamphlet-only</span>.
              When in doubt, the level is downgraded. Individual axis scores
              also carry a confidence level (high, medium, or low), and{' '}
              <strong>low-confidence scores are excluded from the alignment
              math entirely</strong> — they inform, but they don't sway the
              number.
            </p>
          </div>
        </Section>

        {/* ---- interview + math ---- */}
        <Section eyebrow="Step three" title="Your values, and the arithmetic">
          <p className="copy" style={{ fontSize: 13.5 }}>
            The interview places <em>you</em> on the same axes. Short position
            statements you agree or disagree with (and can skip), plus a few
            forced-choice trade-offs between two public goods, map to axis
            positions from −2 to +2; a quick &ldquo;how much do you care&rdquo;
            pulse sets a per-axis weight (0, 1, or 2). Statement directions are
            deliberately mixed so &ldquo;agree&rdquo; doesn't always point the
            same way — a guard against reflexive agreement. The interview also
            adapts to your ballot: you're only asked about axes that can
            actually affect a contest you're covered for. That's your values
            profile.
          </p>
          <p className="copy" style={{ fontSize: 13.5 }}>
            Alignment is then plain, inspectable arithmetic — the same math for
            everyone, computed in your browser:
          </p>
          <div className="dashed-note">
            <strong>Per axis</strong>, similarity is{' '}
            <code>1 − |your position − their score| ÷ 4</code>, so identical
            positions score 1 and opposite poles score 0.{' '}
            <strong>Overall</strong>, those per-axis similarities are averaged,
            weighted by how much you said you care, and turned into a 0–100
            alignment score.
          </div>
          <p className="copy" style={{ fontSize: 13 }}>
            Two guards keep the number honest. A candidate must share at least a
            couple of scored axes with your answers to be scored at all. And a
            score built from only a few axes is pulled toward the neutral middle
            (50), so a candidate rated on three axes can't post a flashy 100 and
            out-rank one honestly rated on ten — thin evidence shouldn't buy
            false precision. When two candidates land within a few points, the
            guide calls it <strong>too close to call</strong> rather than
            manufacture a winner. For measures, the same weighting produces a{' '}
            <strong>leans yes</strong>, <strong>leans no</strong>, or{' '}
            <strong>genuinely split</strong> read on a <em>yes</em> vote.
          </p>
        </Section>

        {/* ---- check our work ---- */}
        <Section eyebrow="Don't take our word for it" title="How to check our work">
          <p className="copy" style={{ fontSize: 13.5 }}>
            Because there's no runtime AI and every score is sourced, the guide
            is auditable end to end. In any result, open a candidate to see the
            per-axis scores and the citations behind them, and follow the source
            links. Everything you value the guide on is visible: the rubric
            above, the sources on each score, and the arithmetic that combines
            them. If a citation doesn't support its score, that's a bug you can
            catch — and the whole point of building it this way. There's a
            report-an-error button on every result; because the whole guide is
            just data, a fix can be researched, re-scored, and redeployed in
            minutes.
          </p>
          <div className="dashed-note">
            <strong>See also.</strong> The{' '}
            <a href="#data">open dataset</a> shows what Washington voters value
            in aggregate — every anonymous report, never an address.
          </div>
        </Section>
      </div>

      <footer>
        <div className="wave-bottom">
          <div className="wave-label">NO ACCOUNTS · NO COOKIES · OPEN DATA</div>
        </div>
      </footer>
    </main>
  )
}
