const BENEFITS = [
  {
    title: 'No dropdowns, no guessing',
    desc: 'Upload anything with text on it. The agent works out what kind of document it is itself — you never pick a category.',
    icon: MagicIcon,
  },
  {
    title: 'Plain language, not jargon',
    desc: 'Every explanation is written for someone with zero background in the subject — clauses and fine print, translated.',
    icon: ChatIcon,
  },
  {
    title: 'Flags what actually matters',
    desc: 'Unusual terms, risky clauses, or numbers worth double-checking are called out automatically, not buried in the text.',
    icon: FlagIcon,
  },
  {
    title: 'Fast, and it talks back',
    desc: 'Groq explains your document in seconds, and the summary is read aloud — no separate app or setup needed.',
    icon: BoltIcon,
  },
]

export default function WhyDoculyze() {
  return (
    <section className="content-section" id="why-doculyze">
      <div className="section-heading-wrap">
        <h2 className="section-heading">Why Doculyze</h2>
        <p className="section-sub">Built around one idea — understanding a document shouldn't take effort.</p>
      </div>
      <div className="example-grid">
        {BENEFITS.map((b) => (
          <div className="example-card static" key={b.title}>
            <span className="example-icon">
              <b.icon />
            </span>
            <strong>{b.title}</strong>
            <span>{b.desc}</span>
          </div>
        ))}
      </div>
    </section>
  )
}

function MagicIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="m4 20 11-11" strokeLinecap="round" />
      <path d="M13.5 4.5 15 3l1.5 1.5L18 3l1.5 1.5L18 6l1.5 1.5L18 9l-1.5-1.5L15 9l-1.5-1.5L15 6l-1.5-1.5Z" strokeLinejoin="round" />
      <path d="m15 9 3 3" strokeLinecap="round" />
    </svg>
  )
}

function ChatIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4.5 6.5A2 2 0 0 1 6.5 4.5h11a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H9l-4.5 4v-4h-0A2 2 0 0 1 4.5 13.5v-7Z" strokeLinejoin="round" />
    </svg>
  )
}

function FlagIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M6 3.5v17" strokeLinecap="round" />
      <path d="M6 4.5h10.5l-2.3 3.5 2.3 3.5H6" strokeLinejoin="round" />
    </svg>
  )
}

function BoltIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z" />
    </svg>
  )
}
