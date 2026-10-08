// The Initials Portrait text for a Candidate: the first letter of the first
// and last name tokens, uppercase, at most two. The same rule the Ballot
// Brief's reference skeleton gives the chatbot. Generational suffixes and
// quoted or parenthesized nicknames are not name tokens.

const SUFFIX = /^(jr|sr|ii|iii|iv|v)$/i

export function initials(name) {
  const tokens = String(name || '')
    .replace(/["“”][^"“”]*["“”]|\([^)]*\)/g, ' ')
    .split(/\s+/)
    .map((t) => t.replace(/[^\p{L}\p{N}]/gu, ''))
    .filter((t) => t && !SUFFIX.test(t))
  if (!tokens.length) return ''
  const first = tokens[0][0]
  const last = tokens.length > 1 ? tokens[tokens.length - 1][0] : ''
  return (first + last).toUpperCase()
}
