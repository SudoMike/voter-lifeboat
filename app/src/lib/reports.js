// Anonymous Report Records: what the results screen posts to /api/report
// (server.js) for the public dataset, and when it posts at all.

/**
 * Record a report only when it is a fresh completion (never a shared link,
 * which would double-count the original voter) on an election that is still
 * live. Archived elections stay explorable but add nothing to the dataset.
 */
export function shouldRecordReport({ election, restored }) {
  if (restored) return false
  return election?.status !== 'archived'
}

/** Fire-and-forget: answers + ballot context, never an address. */
export function postReport(data, context, answers) {
  const a = {}
  for (const [axis, { v, w }] of Object.entries(answers)) a[axis] = [v, w]
  fetch('/api/report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      v: data.data_version,
      election: data.election?.id,
      coverageStatus: context.coverageStatus,
      county: context.county,
      districts: context.districts || {},
      answers: a,
    }),
  }).catch(() => {})
}
