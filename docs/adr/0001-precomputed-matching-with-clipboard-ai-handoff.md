# Precomputed matching with clipboard AI handoff, no runtime AI

All AI work happens offline in the data pipeline: an LLM reads each
candidate's Dossier and scores it against the Rubric (with citations)
before launch, and the site ships those scores as static JSON. At
runtime, matching a Values Profile to candidates is deterministic
client-side math. For open-ended discussion, the site offers the Ballot
Brief — a copy-to-clipboard packet of the voter's profile, results, and
dossier summaries — which the voter pastes into *their own* AI chat.

We rejected runtime AI matching because it would make recommendations
non-deterministic (identical voters could get different answers on a
public voting tool), unauditable before display, costly per user, and
would require a backend holding an API key. The clipboard handoff keeps
the chat-depth benefit while the site stays a static app with zero
per-user cost.
