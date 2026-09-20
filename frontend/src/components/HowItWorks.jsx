const STEPS = [
  {
    title: 'Detect',
    desc: 'Identifies what the document is and how it is structured.',
    icon: DetectIcon,
  },
  {
    title: 'Analyze',
    desc: 'Pulls out key information — clauses, dates, numbers, and more.',
    icon: AnalyzeIcon,
  },
  {
    title: 'Explain',
    desc: 'Turns the confusing parts into plain, simple language.',
    icon: ExplainIcon,
  },
  {
    title: 'Act',
    desc: 'Flags what to double-check and what to do next.',
    icon: ActIcon,
  },
]

export default function HowItWorks() {
  return (
    <section className="how-it-works" id="how-it-works">
      <div className="glass-card how-card">
        <h3>How It Works</h3>
        <ol className="how-steps">
          {STEPS.map((step, i) => (
            <li className="how-step" key={step.title}>
              <span className="how-step-num">{i + 1}</span>
              <p className="how-step-title">
                <step.icon />
                {step.title}
              </p>
              <p className="how-step-desc">{step.desc}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}

function DetectIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
      <path d="M7 3.5h7l5 5V19a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 6 19V5A1.5 1.5 0 0 1 7 3.5Z" strokeLinejoin="round" />
      <path d="M14 3.5v5h5" strokeLinejoin="round" />
    </svg>
  )
}

function AnalyzeIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
      <circle cx="10.5" cy="10.5" r="6.5" />
      <path d="m19.5 19.5-4-4" strokeLinecap="round" />
    </svg>
  )
}

function ExplainIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
      <path d="M12 3.5a5 5 0 0 0-3 9v2.5h6V12.5a5 5 0 0 0-3-9Z" strokeLinejoin="round" />
      <path d="M10 19h4M10.7 21h2.6" strokeLinecap="round" />
    </svg>
  )
}

function ActIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9">
      <path d="m4 12.5 5.5 5.5L20 7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
