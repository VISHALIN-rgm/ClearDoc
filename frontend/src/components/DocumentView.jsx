import ResultView from './ResultView.jsx'
import ChatPanel from './ChatPanel.jsx'

const STEPS = [
  { key: 'extract', label: 'Extracting text' },
  { key: 'explain', label: 'Explaining with Groq' },
  { key: 'speak', label: 'Generating narration' },
  { key: 'save', label: 'Saving result' },
]

// The backend doesn't report step-by-step progress (the pipeline is a
// handful of seconds end to end), so this maps elapsed time since
// upload to a step index just to give the user a sense of motion —
// it's not read back from the server.
function stepIndexForElapsed(ms) {
  if (ms < 2000) return 0
  if (ms < 6000) return 1
  if (ms < 8000) return 2
  return 3
}

export default function DocumentView({
  fileName,
  stage,
  elapsedMs,
  result,
  errorMessage,
  onCancel,
  onNewUpload,
  onRetry,
}) {
  const isActive = stage === 'uploading' || stage === 'processing'
  const activeStep = stepIndexForElapsed(elapsedMs)

  return (
    <section className="document-view">
      <div className="glass-card doc-view-header">
        <div className="doc-view-title">
          <FileIcon />
          <span>{fileName}</span>
        </div>
        {isActive ? (
          <button className="cancel-button" onClick={onCancel} aria-label="Cancel">
            <XIcon />
          </button>
        ) : (
          <button className="ghost-button" onClick={onNewUpload}>
            New upload
          </button>
        )}
      </div>

      {isActive && (
        <div className="glass-card processing-card">
          <ul className="processing-steps">
            {STEPS.map((step, i) => (
              <li
                key={step.key}
                className={`step-item ${i < activeStep ? 'step-done' : i === activeStep ? 'step-active' : 'step-pending'}`}
              >
                {i < activeStep ? <CheckIcon /> : i === activeStep ? <SpinnerIcon /> : <DotIcon />}
                {step.label}
              </li>
            ))}
          </ul>
          <p className="fine-print">Usually takes 15–30 seconds</p>
        </div>
      )}

      {stage === 'failed' && (
        <div className="glass-card error-state">
          <p className="error-text">{errorMessage}</p>
          <button className="primary-button" onClick={onRetry}>
            Try again
          </button>
        </div>
      )}

      {stage === 'complete' && result && (
        <div className="dashboard-columns">
          <ResultView result={result} onAnalyzeAnother={onNewUpload} hideHeaderAction />
          <ChatPanel documentId={result.documentId} suggestedQuestions={result.suggestedQuestions} />
        </div>
      )}
    </section>
  )
}

function FileIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M7 3.5h7l5 5V19a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 6 19V5A1.5 1.5 0 0 1 7 3.5Z" strokeLinejoin="round" />
      <path d="M14 3.5v5h5" strokeLinejoin="round" />
    </svg>
  )
}

function XIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
      <path d="M6 6l12 12M18 6L6 18" strokeLinecap="round" />
    </svg>
  )
}

function CheckIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" className="step-icon step-icon-done">
      <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function SpinnerIcon() {
  return <span className="step-icon step-spinner" aria-hidden="true" />
}

function DotIcon() {
  return <span className="step-icon step-dot" aria-hidden="true" />
}
