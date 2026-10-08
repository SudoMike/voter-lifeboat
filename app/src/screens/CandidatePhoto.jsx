import React, { useState } from 'react'
import { initials } from '../lib/initials.js'

// The Candidate Photo beside a candidate's name, or the Initials Portrait in
// the same frame when the Candidate has none or the image fails to load
// (blocked hotlink, dead URL, non-image). The browser loads photo.url
// straight from its source; nothing is mirrored. The frame is aria-hidden
// because the name is printed next to it.
export default function CandidatePhoto({ photo, name, size = 46 }) {
  const [failedUrl, setFailedUrl] = useState(null)
  const url = photo?.url
  const frame = { width: size, height: size }
  if (url && failedUrl !== url) {
    return (
      <span className="cand-photo-wrap" style={frame} aria-hidden="true">
        <img
          className="cand-photo"
          src={url}
          alt=""
          width={size}
          height={size}
          loading="lazy"
          decoding="async"
          referrerPolicy="no-referrer"
          onError={() => setFailedUrl(url)}
        />
      </span>
    )
  }
  return (
    <span className="cand-photo-wrap" style={frame} aria-hidden="true">
      <span className="cand-photo cand-photo--initials" style={{ fontSize: Math.round(size * 0.35) }}>
        {initials(name)}
      </span>
    </span>
  )
}
