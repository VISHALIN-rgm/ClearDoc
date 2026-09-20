const SEVERITY_LABEL = { low: 'Low', medium: 'Medium', high: 'High' }

export default function ResultView({ result, onAnalyzeAnother, hideHeaderAction = false }) {
  const {
    documentType,
    documentName,
    summary,
    keyTerms = [],
    redFlags = [],
    actionItems = [],
    audioUrl,
  } = result

  return (
    <section className="result-grid">
      <div className="glass-card result-header">
        <div>
          <p className="fine-print">{documentName || 'Your document'}</p>
          <h2 className="doc-type">{documentType || 'Document'}</h2>
        </div>
        {!hideHeaderAction && (
          <button className="ghost-button" onClick={onAnalyzeAnother}>
            Analyze another
          </button>
        )}
      </div>

      <div className="glass-card summary-card">
        <h3>What this says</h3>
        <p>{summary}</p>
        {audioUrl && (
          <div className="audio-player">
            <span className="fine-print">Listen to the summary</span>
            <audio controls src={audioUrl}>
              Your browser does not support audio playback.
            </audio>
          </div>
        )}
      </div>

      {keyTerms.length > 0 && (
        <div className="glass-card">
          <h3>Key terms</h3>
          <ul className="pill-list">
            {keyTerms.map((term, i) => (
              <li key={i} className="pill">
                {term}
              </li>
            ))}
          </ul>
        </div>
      )}

      {redFlags.length > 0 && (
        <div className="glass-card">
          <h3>Worth double-checking</h3>
          <ul className="flag-list">
            {redFlags.map((flag, i) => (
              <li key={i} className={`flag-item severity-${flag.severity || 'low'}`}>
                <span className="severity-dot" aria-hidden="true" />
                <div>
                  <p className="flag-issue">{flag.issue}</p>
                  <p className="flag-reason">{flag.why_it_matters || flag.whyItMatters}</p>
                </div>
                <span className="severity-tag">{SEVERITY_LABEL[flag.severity] || 'Note'}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {actionItems.length > 0 && (
        <div className="glass-card">
          <h3>What to do next</h3>
          <ul className="action-list">
            {actionItems.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </section>
  )
}
