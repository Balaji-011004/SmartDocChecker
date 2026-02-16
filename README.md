# SmartDocChecker

**AI-powered enterprise document contradiction detection system.**

SmartDocChecker analyses legal, policy, and compliance documents to automatically detect contradictions, inconsistencies, and conflicting clauses — both within a single document and across multiple documents.

---

## Key Features

- **Single-document analysis** — detect internal contradictions within one document
- **Multi-document comparison** — find cross-document inconsistencies across 2–10 files
- **AI-driven pipeline** — SBERT semantic embeddings → rule-based checks → NLI verification
- **Named Entity Recognition** — spaCy NER detects conflicting people, dates, organizations, and monetary values
- **Real-time progress tracking** — live pipeline stage updates during analysis
- **PDF report generation** — downloadable contradiction reports with severity breakdown
- **Analytics dashboard** — usage metrics, contradiction type distribution, and activity feed
- **Document management** — upload, search, download, and delete documents
- **JWT authentication** — secure user accounts with bcrypt password hashing
- **Rate limiting** — configurable per-endpoint rate limits via SlowAPI
- **Security hardened** — CORS restrictions, security headers, filename sanitization, IDOR protection

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend API** | FastAPI (Python), Uvicorn |
| **Database** | PostgreSQL (Supabase), SQLAlchemy ORM |
| **File Storage** | Supabase Storage |
| **AI / NLP** | Sentence-BERT (`all-MiniLM-L6-v2`), Cross-Encoder NLI (`nli-distilroberta-base`), spaCy (`en_core_web_sm`) |
| **Frontend** | React 18, React Router, Vite |
| **PDF Reports** | jsPDF |
| **Auth** | JWT (HS256), bcrypt |

---

## Project Structure

```
SmartDocChecker/
├── runapp.py                     # One-command launcher (backend + frontend)
├── backend/
│   ├── main.py                   # FastAPI app entrypoint
│   ├── config.py                 # Settings from .env (DB, Supabase, JWT, CORS, AI)
│   ├── constants.py              # Supported file types, size limits
│   ├── dependencies.py           # Shared FastAPI dependencies
│   ├── requirements.txt          # Python dependencies
│   ├── api/
│   │   ├── router.py             # Mounts all sub-routers under /api
│   │   ├── auth.py               # POST /register, /login, GET /me (rate-limited)
│   │   ├── dashboard.py          # GET /dashboard/stats (analytics)
│   │   ├── documents.py          # POST /upload, GET /documents, GET /documents/{id}
│   │   └── results.py            # POST /analyze/single, /analyze/multi, GET /results
│   ├── models/                   # SQLAlchemy ORM models
│   │   ├── user.py               # User (id, email, name, hashed_password)
│   │   ├── document.py           # Document (file metadata, status, progress tracking)
│   │   ├── clause.py             # Clause (text, embedding vector, NER entities, tsvector)
│   │   ├── contradiction.py      # Contradiction (intra-document)
│   │   ├── comparison.py         # ComparisonSession (multi-doc session tracking)
│   │   └── cross_contradiction.py # CrossContradiction (inter-document)
│   ├── services/
│   │   ├── embedding_service.py  # SBERT model loading, encode, similarity, search
│   │   ├── nli_service.py        # Cross-Encoder NLI model, batch contradiction scoring
│   │   ├── ner_service.py        # spaCy NER extraction and entity conflict detection
│   │   ├── rule_checker.py       # Rule-based checks (numeric, modal, authority, entity)
│   │   └── supabase_storage.py   # Supabase Storage client (upload, download, delete)
│   ├── utils/
│   │   ├── text_extractor.py     # PDF/DOCX/TXT text extraction with header dedup
│   │   └── clause_segmenter.py   # Sentence segmentation with noise filtering
│   ├── workers/
│   │   ├── processing_worker.py  # Single-doc analysis pipeline (background thread)
│   │   └── comparison_worker.py  # Multi-doc comparison pipeline (background thread)
│   ├── core/
│   │   ├── security.py           # OAuth2 scheme definition
│   │   ├── jwt_handler.py        # JWT token creation and verification
│   │   └── hashing.py            # bcrypt password hashing
│   └── db/
│       ├── base.py               # SQLAlchemy declarative base
│       └── session.py            # Engine and SessionLocal factory
├── frontend/
│   ├── index.html                # HTML entry point
│   ├── package.json              # Node dependencies (React, jsPDF, React Router)
│   ├── vite.config.js            # Vite dev server config
│   └── src/
│       ├── App.jsx               # Root routes (Landing, Auth, Dashboard)
│       ├── main.jsx              # React DOM render entry
│       ├── index.css             # Global styles
│       ├── context/
│       │   └── AuthContext.jsx   # Auth state, login/signup/logout, token persistence
│       ├── pages/
│       │   ├── LandingPage.jsx   # Public marketing page
│       │   ├── AuthPage.jsx      # Login / Signup form
│       │   ├── DashboardPage.jsx # Analytics overview with metrics & activity feed
│       │   ├── UploadPage.jsx    # Document upload & analysis page (single/multi)
│       │   └── DocumentsPage.jsx # Document management (search, sort, grid/list view)
│       ├── components/
│       │   ├── DashboardLayout.jsx # Authenticated layout with Navbar + routes
│       │   ├── Navbar.jsx        # Top nav (Dashboard, Documents, Analyze)
│       │   ├── UploadArea.jsx    # Drag-and-drop file upload zone
│       │   ├── FileItem.jsx      # Uploaded file row with status
│       │   ├── AnalysisProgress.jsx # Real-time pipeline step progress bar
│       │   ├── AnalysisResults.jsx  # Results display with summary & contradictions
│       │   ├── ContradictionItem.jsx # Single contradiction card
│       │   ├── ProtectedRoute.jsx   # Auth guard wrapper
│       │   ├── Notification.jsx  # Toast notification component
│       │   ├── ErrorBoundary.jsx # React error boundary
│       │   ├── Button.jsx        # Reusable button component
│       │   └── Input.jsx         # Reusable input component
│       └── utils/
│           ├── api.js            # API client (auth, documents, analysis, dashboard)
│           ├── helpers.js        # Formatting utilities (file size, type colors)
│           └── pdfReport.js      # PDF report generation with jsPDF
└── .gitignore
```

---

## Analysis Pipeline

### Single-Document Analysis

```
Upload → Download from Storage → Extract Text (PDF/DOCX/TXT)
  → Segment into Clauses → Generate SBERT Embeddings + tsvector
  → Extract Named Entities (NER) → Cosine Similarity Matrix (≥ 0.82)
  → Rule-Based Checks (numeric, modal, authority, entity)
  → NLI Verification (softmax, multi-gate scoring)
  → Store Contradictions
```

### Multi-Document Comparison

```
Prepare Session → Extract/Reuse per-doc Clauses & Embeddings
  → Cross-Doc Cosine Similarity Matrix (≥ 0.75)
  → Cross-Doc Rule-Based Checks
  → NLI Verification (batch scoring with word-overlap filter)
  → Store Cross-Contradictions
```

### Contradiction Types Detected

| Type | Detection Method |
|------|-----------------|
| **Numeric** | Different numbers/quantities in semantically similar clauses |
| **Modal** | Conflicting obligation levels (e.g., "shall" vs "may") |
| **Authority** | Conflicting responsible parties or decision-makers |
| **Entity** | Mismatched named entities (people, dates, organizations, money) |
| **Semantic** | General meaning contradictions verified by NLI model |
| **Date** | Conflicting temporal references |
| **Location** | Conflicting geographical references |
| **Financial** | Conflicting monetary values |

### Real-Time Progress Stages

The frontend receives live updates as each pipeline stage completes:

| Stage | Progress | Description |
|-------|----------|-------------|
| `downloading` | 5% | Fetching document from storage |
| `extracting` | 15% | Extracting text content |
| `segmenting` | 25% | Splitting into clauses |
| `embedding` | 40% | Generating AI embeddings |
| `ner` | 55% | Extracting named entities |
| `similarity` | 65% | Finding similar clause pairs |
| `rules` | 72% | Running rule-based checks |
| `nli` | 80% | NLI contradiction verification |
| `storing` | 90% | Persisting results |
| `completed` | 100% | Done |

---

## Getting Started

### Prerequisites

- **Python 3.12+**
- **Node.js 18+** and npm
- **PostgreSQL** database (Supabase recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/SmartDocChecker.git
cd SmartDocChecker
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create a `backend/.env` file:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-key
SECRET_KEY=your-jwt-secret          # Required — generate with: python -c "import secrets; print(secrets.token_urlsafe(64))"
ADMIN_PASSWORD=YourSecurePassword1   # Default admin account password
DEBUG=false                          # Set to true to enable /docs and /redoc
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Run Both Services

From the project root:

```bash
python runapp.py
```

This starts:
- **Backend** at `http://localhost:8000` (API docs at `/docs` when `DEBUG=true`)
- **Frontend** at `http://localhost:5173`

Or run them individually:

```bash
# Terminal 1 — Backend
cd backend
uvicorn main:app --reload

# Terminal 2 — Frontend
cd frontend
npm run dev
```

---

## API Endpoints

| Method | Endpoint | Rate Limit | Description |
|--------|----------|------------|-------------|
| `POST` | `/api/auth/register` | 10/min | Create new user account |
| `POST` | `/api/auth/login` | 10/min | Login and receive JWT token |
| `GET` | `/api/auth/me` | — | Get current user info |
| `POST` | `/api/documents/upload` | 20/min | Upload a document (PDF/DOCX/TXT) |
| `GET` | `/api/documents/` | — | List user's documents |
| `GET` | `/api/documents/{id}` | — | Get document details + progress |
| `DELETE` | `/api/documents/{id}` | — | Delete a document |
| `POST` | `/api/analyze/single` | 10/min | Start single-document analysis |
| `POST` | `/api/analyze/multi` | 5/min | Start multi-document comparison |
| `GET` | `/api/documents/{id}/results` | — | Get analysis results |
| `GET` | `/api/comparison/{id}/status` | — | Poll comparison progress |
| `GET` | `/api/comparison/{id}/results` | — | Get comparison results |
| `GET` | `/api/dashboard/stats` | — | Get dashboard analytics |

### Security Headers

All API responses include:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Cache-Control: no-store` (on `/api/` routes)

---

## Supported File Types

- **PDF** (`.pdf`) — with header/footer deduplication and page-number normalization
- **DOCX** (`.docx`) — paragraphs and table cells extracted
- **Plain Text** (`.txt`)

Maximum file size: **10 MB**

---

## License

This project is for educational and research purposes.
