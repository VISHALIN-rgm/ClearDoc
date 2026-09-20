const EXAMPLES = [
  {
    title: 'Electricity Bill',
    desc: 'Understand charges, due dates and more.',
    icon: BoltIcon,
  },
  {
    title: 'Rental Agreement',
    desc: 'Know your rights, obligations and terms.',
    icon: HomeIcon,
  },
  {
    title: 'Syllabus',
    desc: 'Find important topics, deadlines and more.',
    icon: CapIcon,
  },
  {
    title: 'Any Document',
    desc: 'From reports to policies, we\u2019ve got it covered.',
    icon: DocIcon,
  },
]

export default function ExampleCards({ onPickExample }) {
  return (
    <section className="examples-section">
      <h3>Try with an example</h3>
      <div className="example-grid">
        {EXAMPLES.map((ex) => (
          <button key={ex.title} className="example-card" onClick={() => onPickExample?.(ex.title)}>
            <span className="example-icon">
              <ex.icon />
            </span>
            <strong>{ex.title}</strong>
            <span>{ex.desc}</span>
          </button>
        ))}
      </div>
    </section>
  )
}

function BoltIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
      <path d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z" />
    </svg>
  )
}

function HomeIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M3.5 11.5 12 4l8.5 7.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M6 10v9a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function CapIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="m2.5 9 9.5-4.5L21.5 9 12 13.5 2.5 9Z" strokeLinejoin="round" />
      <path d="M6.5 11v4.5c0 1.4 2.5 2.5 5.5 2.5s5.5-1.1 5.5-2.5V11" strokeLinecap="round" />
    </svg>
  )
}

function DocIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M7 3.5h7l5 5V19a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 6 19V5A1.5 1.5 0 0 1 7 3.5Z" strokeLinejoin="round" />
      <path d="M14 3.5v5h5" strokeLinejoin="round" />
      <path d="M9 13h6M9 16h6" strokeLinecap="round" />
    </svg>
  )
}
