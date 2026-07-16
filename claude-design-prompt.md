# Design brief: Voter Lifeboat

Mock up **3–4 visually distinct variants** of this site. Each variant should
cover the same screens (listed below) so they can be compared directly. The
winning variant will be handed to developers as HTML/CSS reference for a
Vite + React + Tailwind build — so favor real, buildable HTML/CSS over
image-only mockups, keep everything self-contained (no external assets), and
design **mobile-first** (most users will do this on their phone, thumb-driven;
it should also look great on desktop).

## What the product is

**Voter Lifeboat** (working title) is a free, public, interactive voter guide
for the King County (WA) August 4, 2026 primary election. It interviews a
voter about their values in 2–3 fun minutes, then shows how every candidate
and measure **on their specific ballot** aligns with those values.

The honest hook, stated proudly and up-front: **this whole thing was built and
researched by AI.** No accuracy claims — every score shows its citations so
voters can check the work themselves. That radical transparency is part of the
brand, not fine print to hide.

Privacy is a headline feature: *"Your address and answers never leave your
browser, except to look up your voting districts."* No accounts, no cookies,
no analytics.

## Personality

- **Modern and slick.** You arrive and immediately want to engage. Think the
  energy of a great quiz/game onboarding, not a government form or a
  newspaper endorsement page.
- **Fun but never frivolous** — people are deciding real votes. Playful
  interaction, serious information design.
- **Warm and neutral.** The tool never tells you what to believe; it reflects
  *your* values back at the ballot. Avoid partisan color-coding (no
  red-vs-blue framing) and avoid tired civic clichés (flags, eagles,
  stars-and-stripes). The name "Lifeboat" invites nautical/rescue metaphors —
  use or ignore that freely per variant.
- **Humble where the data is thin.** The design must make honesty look good:
  "too close to call" and "we only have their pamphlet statement" are
  first-class, well-designed states, not apologetic gray text.

## The flow (screens to mock in each variant)

### 1. Landing
The promise ("Answer a few quick questions. See how everyone on YOUR ballot
lines up with YOUR values."), the AI-transparency badge/statement, the privacy
sentence, and one obvious call-to-action. Should feel like the start of
something fun, and set the trust posture in the first screenful.

### 2. Address entry
One field: street address. Explains in a friendly way why we ask (King County
ballots differ street by street — we find your districts, we never store your
address). Needs a graceful loading moment ("finding your ballot…") and an
error state (address not found).

### 3. The Interview
The core loop — this is where "fun" is won or lost. Two question types:

- **Statement Card**: a short, neutrally-worded position statement. Voter
  responds agree / disagree / skip (swipe-friendly on mobile). After a strong
  reaction, an occasional quick follow-up pulse: "How much do you care about
  this?" Show the card mechanic, the care pulse, and a progress indicator that
  makes 12–15 cards feel breezy.
- **Trade-off Scenario**: a concrete forced choice between two goods, e.g.
  "The county has a budget surplus. Where does it go?" with two tappable
  options. These are the highlight moments — make them feel bigger/more
  cinematic than the cards.

Also mock the interview finale: a satisfying "here's your values snapshot"
moment before results (their top axes, what they cared most about).

### 4. Results
A voter's ballot as a list of contests. For each **race**:
- Candidates ranked by alignment score (0–100), with the score visible
- A per-axis breakdown on tap/expand: where the candidate sits on each of the
  voter's top axes, with citations for every claim
- An **Evidence Level** indicator per candidate (rich record vs.
  pamphlet-statement-only) — design this as a legible badge/scale
- Two special states to mock explicitly:
  - **Too close to call** — scores within noise of each other; the design
    says so plainly instead of faking precision
  - **Pamphlet-only candidate** — low evidence, shown honestly
- Uncontested races appear info-only, no scoring theater
- A small note that WA primaries advance the top 2 regardless of party

For each **measure** (levy/proposition): plain-language "what it actually
does," a **Lean** read (leans yes / leans no / genuinely split, derived from
the voter's values), and the official pro & con committee statements side by
side. When the mapping is weak, no lean is shown.

Every candidate card carries a subtle **"report an error"** affordance.

### 5. The Ballot Brief
One tap copies a text packet — the voter's values profile, their results, and
candidate summaries — to the clipboard, so they can paste it into their own
AI chat (ChatGPT, Claude, etc.) and discuss further. Design the moment: what
the button promises, the copied-confirmation, and a hint of what the packet
contains. This is a signature feature; make it feel clever, not like an
export button.

### 6. Footer / trust furniture
Disclaimers (AI-built, no accuracy claims, not affiliated with King County),
a feedback/comment affordance with an opt-in checkbox ("share my interview
answers to help improve this"), and an English-only-for-now acknowledgment.

## Variant direction

Make the 3–4 variants genuinely different from each other — different type
systems, palettes, layout density, and interaction personality (e.g., one
game-like and bold, one editorial and calm, one civic-futurist, one playful
nautical). Same content and screens in each, so the comparison is fair.

## Sample content to use (realistic, invented where needed)

- Contest: "State Representative, 34th Legislative District, Position 1" with
  3 candidates; one rich-evidence, one moderate, one pamphlet-only.
- Measure: "City of Kirkland Proposition 1 — Parks Levy Lid Lift."
- Statement card: "New apartment buildings should be allowed in more
  neighborhoods, even if it changes their character."
- Trade-off: "A budget surplus appears. It goes to: hiring more police
  officers / expanding homelessness services."
- Axes for breakdowns: Housing & density, Tax appetite, Public safety
  approach, Transit priority, Climate urgency.
