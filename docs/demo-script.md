# Demo script — 3 minutes

**0:00–0:20 — The problem**
Everyone has a drawer of documents they signed or skimmed without really
understanding — a lease, a bill, a syllabus, a terms-of-service page.
Doculyze is an AI agent that reads any of them and explains what they
actually say — and reads the summary aloud, too.

**0:20–0:40 — Upload live**
Drag a real document into the app (use one from `docs/sample-documents/`
or something on hand). Point out: no dropdown asking what kind of
document it is — the agent decides that for itself, and adapts its
extraction and explanation to whatever comes in.

**0:40–1:10 — While it processes**
Narrate the pipeline while the loader spins: "This is being read
locally right now, then the extracted text goes to Groq to actually
get explained — and turned into speech."

**1:10–2:00 — Show the result**
Walk through the four sections: plain-language summary, key terms,
flagged items worth double-checking (with severity), and suggested next
steps. Press play on the audio player and let it read the summary
aloud — this is the "aha" moment. Then pick one flagged item and read
it aloud yourself for emphasis.

**2:00–2:30 — Architecture**
Describe it: upload → local text extraction → Groq → text-to-speech →
saved locally, fronted by a small FastAPI backend and a React UI.
Mention it's fully self-hosted — no cloud account needed to run it.

**2:30–3:00 — Close**
Show the history panel with a couple of prior documents. Close on: "One
pipeline, any document, and it talks back — that's the point."
