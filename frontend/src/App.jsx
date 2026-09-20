import { useCallback, useEffect, useRef, useState } from 'react'
import BackgroundArt from './components/BackgroundArt.jsx'
import BotMascot from './components/BotMascot.jsx'
import TopNav from './components/TopNav.jsx'
import UploadBox from './components/UploadBox.jsx'
import ExampleCards from './components/ExampleCards.jsx'
import DocumentView from './components/DocumentView.jsx'
import HistoryPanel from './components/HistoryPanel.jsx'
import HowItWorks from './components/HowItWorks.jsx'
import WhyDoculyze from './components/WhyDoculyze.jsx'
import UseCases from './components/UseCases.jsx'
import FAQ from './components/FAQ.jsx'
import { uploadDocument, pollResult, cancelDocument, listResults, deleteDocument } from './api/client.js'

export default function App() {
  // 'home' = the marketing/upload page. 'document' = the dashboard
  // that takes over the same screen once a file is uploaded.
  const [view, setView] = useState('home')
  const [stage, setStage] = useState('idle') // idle | uploading | processing | complete | failed
  const [fileName, setFileName] = useState('')
  const [lastFile, setLastFile] = useState(null)
  const [currentDocumentId, setCurrentDocumentId] = useState(null)
  const [result, setResult] = useState(null)
  const [errorMessage, setErrorMessage] = useState('')
  const [startedAt, setStartedAt] = useState(null)
  const [elapsedMs, setElapsedMs] = useState(0)

  const [historyOpen, setHistoryOpen] = useState(false)
  const [historyItems, setHistoryItems] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)

  // Bumped on cancel / new upload / retry so a poll or upload in
  // flight from a previous attempt can't land on top of a newer one.
  const activeToken = useRef(0)

  const refreshHistory = useCallback(async () => {
    setHistoryLoading(true)
    try {
      const items = await listResults()
      setHistoryItems(items)
    } catch {
      // History is a nice-to-have — a failed fetch shouldn't block
      // the rest of the app.
    } finally {
      setHistoryLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshHistory()
  }, [refreshHistory])

  // Drives the step indicator in DocumentView while a job is active.
  useEffect(() => {
    if (stage !== 'uploading' && stage !== 'processing') return
    const id = setInterval(() => {
      setElapsedMs(startedAt ? Date.now() - startedAt : 0)
    }, 300)
    return () => clearInterval(id)
  }, [stage, startedAt])

  const startUpload = useCallback(async (file) => {
    const token = ++activeToken.current

    setLastFile(file)
    setView('document')
    setStage('uploading')
    setFileName(file.name)
    setResult(null)
    setErrorMessage('')
    setStartedAt(Date.now())
    setElapsedMs(0)

    try {
      const { documentId } = await uploadDocument(file)
      if (activeToken.current !== token) return
      setCurrentDocumentId(documentId)
      setStage('processing')

      const data = await pollResult(documentId, {
        shouldStop: () => activeToken.current !== token,
      })
      if (activeToken.current !== token) return

      if (data.status === 'complete') {
        setResult(data)
        setStage('complete')
        refreshHistory()
      } else if (data.status === 'failed') {
        setErrorMessage(data.error || 'Something went wrong analyzing this document.')
        setStage('failed')
        refreshHistory()
      } else {
        // cancelled, or any other non-terminal outcome — back to the
        // upload screen rather than stranding the user on a dead view.
        setView('home')
        setStage('idle')
      }
    } catch (err) {
      if (activeToken.current !== token) return
      setErrorMessage(err.message || 'Something went wrong.')
      setStage('failed')
    }
  }, [refreshHistory])

  const handleCancel = useCallback(() => {
    activeToken.current += 1 // invalidates any in-flight upload/poll immediately
    if (currentDocumentId) cancelDocument(currentDocumentId) // best-effort, fire and forget
    setView('home')
    setStage('idle')
    setCurrentDocumentId(null)
    setResult(null)
    setErrorMessage('')
  }, [currentDocumentId])

  const handleNewUpload = useCallback(() => {
    activeToken.current += 1
    setView('home')
    setStage('idle')
    setCurrentDocumentId(null)
    setResult(null)
    setErrorMessage('')
  }, [])

  const handleRetry = useCallback(() => {
    if (lastFile) startUpload(lastFile)
  }, [lastFile, startUpload])

  const handleOpenHistoryItem = useCallback((item) => {
    if (item.status !== 'complete') return
    activeToken.current += 1
    setView('document')
    setStage('complete')
    setResult(item)
    setCurrentDocumentId(item.documentId)
    setFileName(item.documentName || 'Document')
    setHistoryOpen(false)
  }, [])

  const handleDeleteHistoryItem = useCallback(
    async (documentId) => {
      setHistoryItems((prev) => prev.filter((i) => i.documentId !== documentId))
      try {
        await deleteDocument(documentId)
      } catch {
        refreshHistory() // reconcile with the server if the delete didn't actually land
      }
      if (currentDocumentId === documentId) {
        handleNewUpload()
      }
    },
    [currentDocumentId, handleNewUpload, refreshHistory]
  )

  const goHome = useCallback(
    (e) => {
      if (view === 'document') {
        e.preventDefault()
        handleNewUpload()
      }
    },
    [view, handleNewUpload]
  )

  return (
    <div className="app-shell">
      <div className="bg-glow" aria-hidden="true" />
      <BackgroundArt />
      <div className="ambient-orb orb-a" aria-hidden="true" />
      <div className="ambient-orb orb-b" aria-hidden="true" />

      <header className="topbar">
        <a className="brand" href="#home" onClick={goHome}>
          <span className="brand-mark">
            <BrandGlyph />
          </span>
          <span className="brand-name">Doculyze</span>
        </a>
        {view === 'home' && <TopNav />}
        <button className="ghost-button" onClick={() => setHistoryOpen(true)}>
          <ClockIcon /> Recent
        </button>
      </header>

      <main className="main-column">
        {view === 'home' ? (
          <>
            <section id="home" className="hero">
              <div className="hero-copy">
                <h1>
                  Any document in. <span className="hero-accent">Plain language</span> out.
                </h1>
                <p className="hero-sub">
                  Turn confusing documents into clear explanations. Upload a bill, lease, syllabus, or anything else with text on it. Doculyze reads it,
                  explains it in plain language, flags what's worth double-checking, and reads the
                  summary back to you.
                </p>
              </div>
              <BotMascot />
            </section>

            <UploadBox stage="idle" onFile={startUpload} errorMessage="" onRetry={() => {}} />

            <ExampleCards />

            <section id="how-it-works">
              <HowItWorks />
            </section>
            <section id="why-doculyze">
              <WhyDoculyze />
            </section>
            <section id="use-cases">
              <UseCases />
            </section>
            <section id="faq">
              <FAQ />
            </section>
          </>
        ) : (
          <DocumentView
            fileName={fileName}
            stage={stage}
            elapsedMs={elapsedMs}
            result={result}
            errorMessage={errorMessage}
            onCancel={handleCancel}
            onNewUpload={handleNewUpload}
            onRetry={handleRetry}
          />
        )}
      </main>

      <footer className="page-footer">
        <span>Powered by AWS</span>
      </footer>

      <HistoryPanel
        open={historyOpen}
        onClose={() => setHistoryOpen(false)}
        items={historyItems}
        loading={historyLoading}
        onOpen={handleOpenHistoryItem}
        onDelete={handleDeleteHistoryItem}
      />
    </div>
  )
}

function BrandGlyph() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M7 3.5h7l5 5V19a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 6 19V5A1.5 1.5 0 0 1 7 3.5Z" strokeLinejoin="round" />
      <path d="M14 3.5v5h5" strokeLinejoin="round" />
    </svg>
  )
}

function ClockIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M12 7.5V12l3 2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
