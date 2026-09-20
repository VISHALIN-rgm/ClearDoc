const FAQS = [
  {
    q: 'What kinds of documents can I upload?',
    a: 'Any document with readable text — a PDF, a scanned image, or a photo. There\u2019s no menu of supported types; Doculyze reads whatever you give it and works out what it is.',
  },
  {
    q: 'Is my document stored anywhere?',
    a: 'It\u2019s kept on the server running Doculyze, only for as long as it takes to process and show you the result.',
  },
  {
    q: 'Can I trust the explanation completely?',
    a: 'Treat it as a clear starting point, not professional advice. Always double-check anything flagged as a red flag before acting on it.',
  },
  {
    q: 'Does it work with handwritten documents?',
    a: 'It can read some handwriting, but results are most reliable with typed or printed text.',
  },
  {
    q: 'Can Doculyze read the summary out loud?',
    a: 'Yes — every result comes with a short spoken narration of the summary. Press play on the audio player under \u201cWhat this says.\u201d',
  },
  {
    q: 'Is there a cost to use it?',
    a: 'Running it costs whatever your Groq usage comes to for the explanation step — text extraction and speech are free and run locally.',
  },
]

export default function FAQ() {
  return (
    <section className="content-section" id="faq">
      <div className="section-heading-wrap">
        <h2 className="section-heading">Frequently Asked Questions</h2>
        <p className="section-sub">Everything else worth knowing before you upload something.</p>
      </div>
      <div className="faq-list">
        {FAQS.map((item) => (
          <details className="faq-item" key={item.q}>
            <summary>
              <span>{item.q}</span>
              <ChevronIcon />
            </summary>
            <p>{item.a}</p>
          </details>
        ))}
      </div>
    </section>
  )
}

function ChevronIcon() {
  return (
    <svg className="faq-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="m6 9 6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}
