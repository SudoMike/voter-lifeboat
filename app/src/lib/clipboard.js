// navigator.clipboard only exists in secure contexts (HTTPS/localhost) —
// HTTP preview deploys don't have it, so fall back to execCommand there.
export function copyText(text) {
  if (navigator.clipboard?.writeText) return navigator.clipboard.writeText(text)
  const ta = document.createElement('textarea')
  ta.value = text
  ta.style.position = 'fixed'
  ta.style.opacity = '0'
  document.body.appendChild(ta)
  ta.select()
  try {
    const ok = document.execCommand('copy')
    return ok ? Promise.resolve() : Promise.reject(new Error('copy failed'))
  } finally {
    document.body.removeChild(ta)
  }
}
