import { useCallback, useEffect, useRef, useState } from 'react'
import { getChatHistory, sendChatMessage } from '../api/client.js'

export default function ChatPanel({ documentId, suggestedQuestions = [] }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const scrollRef = useRef(null)

  useEffect(() => {
    let cancelled = false
    getChatHistory(documentId)
      .then((data) => {
        if (!cancelled) setMessages(data.history || [])
      })
      .catch(() => {
        // No prior history yet — not an error worth surfacing.
      })
    return () => {
      cancelled = true
    }
  }, [documentId])

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, sending])

  const ask = useCallback(
    async (question) => {
      const trimmed = question.trim()
      if (!trimmed || sending) return

      setError('')
      setMessages((prev) => [...prev, { role: 'user', content: trimmed }])
      setInput('')
      setSending(true)

      try {
        const data = await sendChatMessage(documentId, trimmed)
        setMessages(data.history)
      } catch (err) {
        setError(err.message || 'Something went wrong asking that.')
        // Roll back the optimistic user message so it's not stranded
        // without a reply.
        setMessages((prev) => prev.slice(0, -1))
      } finally {
        setSending(false)
      }
    },
    [documentId, sending]
  )

  const handleSubmit = (e) => {
    e.preventDefault()
    ask(input)
  }

  const showSuggestions = messages.length === 0 && suggestedQuestions.length > 0

  return (
    <div className="glass-card chat-panel">
      <h3>Ask about this document</h3>

      {showSuggestions && (
        <div className="chat-suggestions">
          {suggestedQuestions.map((question, i) => (
            <button key={i} className="chat-suggestion-chip" onClick={() => ask(question)} disabled={sending}>
              {question}
            </button>
          ))}
        </div>
      )}

      <div className="chat-messages" ref={scrollRef}>
        {messages.length === 0 && !showSuggestions && (
          <p className="fine-print chat-empty">Ask a question and Doculyze answers using only this document.</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble chat-bubble-${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {sending && (
          <div className="chat-bubble chat-bubble-assistant chat-bubble-typing" aria-label="Doculyze is answering">
            <span />
            <span />
            <span />
          </div>
        )}
      </div>

      {error && <p className="error-text chat-error">{error}</p>}

      <form className="chat-input-row" onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about this document..."
          disabled={sending}
        />
        <button type="submit" className="primary-button chat-send" disabled={sending || !input.trim()}>
          Ask
        </button>
      </form>
    </div>
  )
}
