import { useRef, useState, useCallback } from 'react'

const ACCEPTED_HINT = 'PDF, PNG, JPG, or scanned image'

export default function UploadBox({ stage, onFile, errorMessage, onRetry }) {
  const cardRef = useRef(null)
  const inputRef = useRef(null)
  const [dragActive, setDragActive] = useState(false)
  const [tilt, setTilt] = useState({ rx: 0, ry: 0 })

  const handleMouseMove = useCallback((e) => {
    const card = cardRef.current
    if (!card) return
    const rect = card.getBoundingClientRect()
    const px = (e.clientX - rect.left) / rect.width - 0.5
    const py = (e.clientY - rect.top) / rect.height - 0.5
    setTilt({ rx: py * -8, ry: px * 10 })
  }, [])

  const resetTilt = useCallback(() => setTilt({ rx: 0, ry: 0 }), [])

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault()
      setDragActive(false)
      const file = e.dataTransfer.files?.[0]
      if (file) onFile(file)
    },
    [onFile]
  )

  const handleSelect = (e) => {
    const file = e.target.files?.[0]
    if (file) onFile(file)
  }

  const busy = stage === 'uploading' || stage === 'processing'

  return (
    <div
      ref={cardRef}
      className={`glass-card upload-card ${dragActive ? 'drag-active' : ''} ${busy ? 'busy' : ''}`}
      style={{ transform: `perspective(1000px) rotateX(${tilt.rx}deg) rotateY(${tilt.ry}deg)` }}
      onMouseMove={handleMouseMove}
      onMouseLeave={resetTilt}
      onDragOver={(e) => {
        e.preventDefault()
        setDragActive(true)
      }}
      onDragLeave={() => setDragActive(false)}
      onDrop={handleDrop}
    >
      <div className="card-sheen" aria-hidden="true" />

      {stage === 'idle' && (
        <>
          <div className="upload-icon">
            <CloudUploadGlyph />
          </div>
          <h2>Drop your document here</h2>
          <p className="muted">or</p>
          <button className="primary-button" onClick={() => inputRef.current?.click()}>
            <UploadArrowIcon />
            Choose File
          </button>
          <input
            ref={inputRef}
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            hidden
            onChange={handleSelect}
          />
          <p className="fine-print">{ACCEPTED_HINT}</p>
        </>
      )}

      {stage === 'uploading' && <StatusState label="Uploading document…" />}
      {stage === 'processing' && (
        <StatusState label="Reading and explaining your document…" sub="Usually takes 15–30 seconds" />
      )}

      {stage === 'error' && (
        <div className="error-state">
          <p className="error-text">{errorMessage}</p>
          <button className="primary-button" onClick={onRetry}>
            Try again
          </button>
        </div>
      )}
    </div>
  )
}

function StatusState({ label, sub }) {
  return (
    <div className="status-state">
      <div className="loader-ring" aria-hidden="true" />
      <p>{label}</p>
      {sub && <p className="fine-print">{sub}</p>}
    </div>
  )
}

function CloudUploadGlyph() {
  return (
    <svg viewBox="0 0 64 64" width="46" height="46" fill="none">
      <path
        d="M20 44h-4a9 9 0 0 1-1-17.9A12 12 0 0 1 38 20.4 9.5 9.5 0 0 1 48 30v.2A8 8 0 0 1 47 46H24"
        stroke="url(#glyph-gradient)"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M32 50V33" stroke="url(#glyph-gradient)" strokeWidth="2.4" strokeLinecap="round" />
      <path d="M25 39l7-7 7 7" stroke="url(#glyph-gradient)" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
      <defs>
        <linearGradient id="glyph-gradient" x1="0" y1="0" x2="64" y2="64">
          <stop offset="0" stopColor="#ff5e1a" />
          <stop offset="1" stopColor="#ffb35c" />
        </linearGradient>
      </defs>
    </svg>
  )
}

function UploadArrowIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
      <path d="M12 16V6M7 10l5-5 5 5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5 19h14" strokeLinecap="round" />
    </svg>
  )
}
