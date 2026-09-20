const CASES = [
  {
    title: 'Renters & tenants',
    desc: 'Understand lease terms, deposit rules, and notice periods before you sign — or after, if something feels off.',
    icon: KeyIcon,
  },
  {
    title: 'Students',
    desc: 'Turn a dense syllabus into a clear list of deadlines, grading weight, and attendance rules.',
    icon: CapIcon,
  },
  {
    title: 'Consumers',
    desc: 'Make sense of bills, warranties, and terms-of-service pages without reading every line yourself.',
    icon: ReceiptIcon,
  },
  {
    title: 'Employees',
    desc: 'Get a plain-language read on offer letters, policy documents, and benefits paperwork.',
    icon: BriefcaseIcon,
  },
  {
    title: 'Honestly, anyone',
    desc: 'These four just come up the most. Doculyze reads any document for anyone — there\u2019s no list it\u2019s limited to.',
    icon: GlobeIcon,
  },
]

export default function UseCases() {
  return (
    <section className="content-section" id="use-cases">
      <div className="section-heading-wrap">
        <h2 className="section-heading">Who It Helps</h2>
        <p className="section-sub">A few common cases — not the whole list. If you've got a confusing document, this is for you.</p>
      </div>
      <div className="usecase-list">
        {CASES.map((c, i) => (
          <div className="usecase-row" key={c.title}>
            <span className="usecase-num">{String(i + 1).padStart(2, '0')}</span>
            <span className="usecase-icon">
              <c.icon />
            </span>
            <div className="usecase-copy">
              <strong>{c.title}</strong>
              <span>{c.desc}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

function KeyIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <circle cx="8" cy="15" r="3.5" />
      <path d="M10.5 12.5 18 5M15.5 7.5l2 2M18 5l2.5 2.5" strokeLinecap="round" strokeLinejoin="round" />
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

function ReceiptIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M6 3.5h12v17l-2.5-1.5L13 20.5 10.5 19 8 20.5 5.5 19V6a2.5 2.5 0 0 1 .5-1.5" strokeLinejoin="round" />
      <path d="M9 8h6M9 11.5h6M9 15h4" strokeLinecap="round" />
    </svg>
  )
}

function BriefcaseIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <rect x="3.5" y="7.5" width="17" height="12" rx="2" strokeLinejoin="round" />
      <path d="M8.5 7.5V6a2 2 0 0 1 2-2h3a2 2 0 0 1 2 2v1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M3.5 12.5h17" />
    </svg>
  )
}

function GlobeIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <circle cx="12" cy="12" r="8.5" />
      <path d="M3.5 12h17M12 3.5c2.5 2.4 3.8 5.4 3.8 8.5s-1.3 6.1-3.8 8.5c-2.5-2.4-3.8-5.4-3.8-8.5S9.5 5.9 12 3.5Z" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
