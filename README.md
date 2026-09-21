# Doculyze

> **Any document in. Plain language out.**  
> Turn confusing documents into clear explanations — and listen to the summary out loud.

Doculyze is an AI document assistant that transforms PDFs, images, and text files into structured, easy-to-understand explanations. Upload a document and get:

- A plain-language summary
- Important terms and details
- Items worth double-checking
- Suggested next actions
- A document-specific chat experience
- An audio narration of the summary

It can handle a bill, lease, syllabus, terms-of-service document, or any other document with readable text without asking you to choose a document type first.

> **Important:** Doculyze provides an explanation and starting point, not legal, financial, medical, or professional advice. Always verify important information with a qualified professional.

## ✨ Product flow

```text
Upload a document
        │
        ▼
Extract readable text
        │
        ▼
Understand and explain the document
        │
        ▼
Show summary, terms, flags, and actions
        │
        ▼
Generate an audio narration
        │
        ▼
Ask follow-up questions about that document
```

## 🏗️ Architecture at a glance

Doculyze is a monorepo with a React/Vite frontend and a FastAPI/Python backend.

```mermaid
flowchart LR
    User([User])
    Amplify[AWS Amplify<br/>Frontend hosting]
    React[React + Vite<br/>frontend/]
    API[FastAPI API<br/>backend/app.py]
    Pipeline[Background pipeline<br/>backend/pipeline.py]
    Extract[Text extraction<br/>pypdf + Tesseract]
    LLM[Groq LLM<br/>structured explanation]
    TTS[gTTS<br/>MP3 narration]
    Store[(Local JSON storage<br/>uploads, results, audio)]

    User --> Amplify
    Amplify --> React
    React -->|POST /upload| API
    React -->|GET /result/{id}<br/>GET /results<br/>POST /chat/{id}| API
    API --> Pipeline
    Pipeline --> Extract
    Extract --> LLM
    LLM --> TTS
    TTS --> Store
    Pipeline --> Store
    API --> Store
    API -->|JSON results + audio URL| React
```

### Request and processing flow

1. The user selects a PDF, image, or text file in the React frontend.
2. The frontend sends the file to `POST /upload`.
3. FastAPI stores the upload and immediately returns a `documentId`.
4. A background task runs the processing pipeline:
   - Extract text locally using `pypdf` or Tesseract OCR.
   - Send the extracted text to Groq for a structured explanation.
   - Convert the summary into speech with gTTS.
   - Save the result, document metadata, and audio path.
5. The frontend polls `GET /result/{id}` until processing is complete.
6. The user sees the explanation and can ask questions scoped to the uploaded document.

### Why this behaves like an agent

The pipeline does not branch on hardcoded document types. The model identifies what the document is, decides what matters, and determines what should be flagged. The same pipeline can process a bill, lease, syllabus, or another text-based document.

## ☁️ Deployment

### Frontend: AWS Amplify

The frontend is deployed on **AWS Amplify** from the `main` branch. The repository uses a root-level `amplify.yml` monorepo configuration, which tells Amplify to build the application from `frontend/`.

```yaml
version: 1
applications:
  - appRoot: frontend
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: dist
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
```

Amplify runs the following production steps:

```bash
cd frontend
npm ci
npm run build
```

The generated Vite files are published from `frontend/dist`.

### Backend

The backend is a FastAPI service. Configure the frontend API URL using `frontend/.env`:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

For production, replace the local URL with the publicly reachable URL of the deployed backend.

> The frontend and backend must be deployed separately unless the backend is hosted behind the same service or domain. AWS Amplify hosts the frontend; it does not automatically host this FastAPI service.

## 📁 Repository layout

```text
ClearDoc/
├── amplify.yml                 # AWS Amplify monorepo build configuration
├── backend/                    # FastAPI service and document pipeline
│   ├── app.py                 # API routes
│   ├── extraction.py          # PDF and image text extraction
│   ├── groq_service.py        # LLM explanation and document chat
│   ├── pipeline.py            # Extract → explain → speak → save
│   ├── prompts.py             # LLM prompts
│   ├── storage.py             # Local JSON result storage
│   └── tts_service.py         # Audio narration generation
├── frontend/                   # React + Vite application
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── amplify.yml            # Legacy/local frontend config
├── docs/                       # Architecture notes and sample documents
└── scripts/                    # Local run and seed helpers
```

## 🧩 Backend modules

| Module | Purpose |
|---|---|
| `app.py` | FastAPI routes for upload, polling, chat, cancellation, history, and audio |
| `cancellation.py` | Best-effort cancellation flags for in-progress jobs |
| `extraction.py` | Extracts text from PDFs and images |
| `groq_service.py` | Generates structured explanations and document-specific chat replies |
| `pipeline.py` | Runs extraction, explanation, speech, and storage in order |
| `prompts.py` | System and user prompts sent to the model |
| `storage.py` | Saves and retrieves local JSON results |
| `tts_service.py` | Creates MP3 narration from the document summary |

## 🚀 Run locally

### Prerequisites

- Python 3.10+
- Node.js 18+
- A Groq API key
- Tesseract OCR, only when processing scanned images
- Internet access for Groq and gTTS

### 1. Configure and run the backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate       # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env          # add your GROQ_API_KEY
uvicorn app:app --reload --port 8000
```

The API runs at `http://localhost:8000`.

### 2. Configure and run the frontend

```bash
cd frontend
npm install
cp .env.example .env          # defaults to http://localhost:8000
npm run dev
```

The frontend runs at `http://localhost:5173`.

### 3. Run both services together

From the repository root:

```bash
./scripts/run.sh
```

## 🧪 Testing

Backend tests mock the Groq and gTTS calls, so they can run without real external API requests:

```bash
cd backend
python3 -m pytest tests/ -v
```

Build the frontend locally before deploying:

```bash
cd frontend
npm run build
```

## 🔌 API overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload a document and start processing |
| `GET` | `/result/{id}` | Poll one document's processing status |
| `GET` | `/results` | List recent documents |
| `GET` | `/result/{id}` | Retrieve one completed result |
| `POST` | `/chat/{id}` | Ask a question about one document |
| `POST` | `/cancel/{id}` | Request cancellation of a processing job |
| `DELETE` | `/result/{id}` | Delete a result, upload, and audio file |
| `GET` | `/audio/{filename}` | Serve generated narration audio |
| `GET` | `/health` | Check whether the API is running |

## 🔐 Environment variables

### Backend: `backend/.env`

```bash
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
PUBLIC_BASE_URL=http://localhost:8000
```

### Frontend: `frontend/.env`

```bash
VITE_API_BASE_URL=http://localhost:8000
```

## 📌 Current limitations

- Local JSON storage is intended for a simple deployment and demo; a multi-user production deployment should use a database and object storage.
- The backend must be publicly reachable for an Amplify-hosted frontend to call it.
- Tesseract is required for scanned image OCR.
- Explanations should be reviewed before making important decisions.
