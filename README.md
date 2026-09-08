# HireWise — AI-Powered Resume Screening & Blind Hiring Platform

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-000000?logo=flask&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6-F7931E?logo=scikitlearn&logoColor=white)

HireWise is a full-stack recruitment tool that screens, classifies, ranks and shortlists candidates using machine learning — with a built-in **blind hiring mode** to reduce unconscious bias and automated **email notifications** for every decision.

---

## The Problem

Recruiters receiving dozens (or hundreds) of applications per opening face three recurring problems:

| Pain point | Consequence |
|---|---|
| **Manual screening doesn't scale** | Every resume is opened, skimmed and compared by hand — hours of repetitive work per role, and the quality of screening degrades as the pile grows. |
| **Screening is inconsistent and biased** | A candidate's name, gender, institute or location can unconsciously influence judgement long before skills are assessed. |
| **Communication is an afterthought** | Even after shortlisting decisions are made, telling every selected or rejected candidate individually is tedious — so many candidates simply never hear back. |

## The Solution

HireWise turns resume screening into a repeatable, criteria-driven pipeline:

1. **Parse** — resumes (PDF/DOCX) are uploaded in bulk and parsed locally; names, emails, phones and skills are extracted with heuristics robust to real-world formatting quirks (emails split across PDF lines, year ranges mistaken for phone numbers, degree suffixes attached to names).
2. **Classify** — a TF-IDF + Logistic Regression model labels each resume with one of 12 job categories (Data Science, ML, Web/Software/Java/Python Development, DevOps, Cybersecurity, Android, DBA, HR, Finance…).
3. **Score** — every candidate is scored 0–100 against the recruiter's hiring criteria using a transparent, weighted formula (see below).
4. **Review blind** — one toggle hides all personally identifiable information (name, gender, location, institute) across every screen, so decisions are made on skills alone.
5. **Decide & notify** — candidates above the threshold are auto-shortlisted (with full manual override), and branded shortlist/rejection emails can be sent individually or in bulk in one click.

## How Scoring Works

Each candidate's match score is a weighted blend of four transparent components:

| Component | Weight | What it measures |
|---|---|---|
| Skill match | 35% | Coverage of the required skills (extracted from the resume + a 150+ skill dictionary) |
| Job-description similarity | 25% | TF-IDF cosine similarity between the resume text and role title + skills + job description |
| Category match | 20% | Agreement between the ML-predicted category and the role (with a related-category fallback, e.g. ML ↔ Data Science) |
| Experience match | 20% | Years of experience vs. the requirement, with partial credit near the threshold |

The breakdown is stored per candidate, so a recruiter can always see *why* a candidate scored 84 — not just that they did.

The classifier itself was selected by comparing four algorithms (Logistic Regression, Naive Bayes, Random Forest, SVM) on a 960-resume dataset; Logistic Regression won and ships as the default model. Retraining is one command: `python train_model.py`.

## Features

### Core

- **ML resume classification** — 12 job categories, model + vectorizer persisted as artifacts
- **Criteria-based scoring** — transparent 4-component weighted score with per-candidate breakdown
- **Auto-shortlisting** — configurable minimum score threshold per hiring round
- **Manual override** — shortlist or reject any candidate at any time
- **Blind hiring mode** — global PII masking across table, card, and detail views plus a dedicated blind-review page
- **Email notifications** — shortlist/rejection emails, individually or in bulk, with delivery-hardened SMTP (timeouts, retries, plain-text alternative parts to avoid spam folders)
- **Dashboard & reports** — live stats, funnel metrics, and category breakdowns with charts

### Extras

- **Job description input** — paste JD text or upload `.txt`/`.pdf`/`.docx`; the JD feeds directly into the similarity component of the score
- **Bulk upload** — up to 80 resumes per batch (200 MB) with per-file success/failure reporting
- **Custom email templates** — editable templates with `{name}`, `{position}` and `{email}` variables, send individually or in bulk
- **Manual email fix-up** — edit a candidate's extracted email if parsing got it wrong
- **Reparse tooling** — re-run extraction on one candidate or the entire pool (idempotent) after data-quality fixes
- **Candidate management** — multi-select with badges, bulk delete, clear-all per hiring round
- **Hiring criteria CRUD** — create, edit and delete screening criteria
- **New-candidate badge** — candidates added in the last 24 hours are highlighted
- **Dark/light theme** — polished SaaS-style UI, fully responsive

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Flask 3.1, SQLAlchemy 2, SQLite |
| ML | scikit-learn (TF-IDF + Logistic Regression), NLTK |
| Resume parsing | pdfplumber (PDF), python-docx (DOCX) |
| Email | smtplib with STARTTLS, retry & timeout handling |
| Frontend | Next.js 16 (App Router), React 19, TypeScript 5, Tailwind CSS 4 |
| Charts / UX | Recharts, react-hot-toast, react-icons |

## Getting Started

### Prerequisites

- **Python 3.10+** (built and tested on 3.13)
- **Node.js 18+** (built and tested on 24)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt

# Generate the dataset and train the ML model (creates ml/models/*.pkl)
python train_model.py

# Start the API on http://localhost:5000
python app.py
```

### 2. Frontend

```bash
cd frontend
npm install

# Start the dev server on http://localhost:3000
npm run dev
```

> **Windows shortcut:** `start_backend.ps1` and `start_frontend.ps1` in the repo root run both steps for you.

### 3. Environment Variables

Copy the template and fill in your SMTP credentials to enable email sending:

```bash
cp backend/.env.example backend/.env
```

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask session signing key | — (required) |
| `DATABASE_URL` | SQLAlchemy database URI | `sqlite:///hirewise.db` |
| `SMTP_HOST` | SMTP server | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (STARTTLS) | `587` |
| `SMTP_USER` | Sender account username | — |
| `SMTP_PASS` | Sender app password (Gmail: use an [App Password](https://myaccount.google.com/apppasswords)) | — |
| `SMTP_SENDER` | From address for outgoing mail | — |

Email sending is optional — the app works fully without SMTP configured.

## Usage

1. Open **http://localhost:3000** — you land straight on the dashboard (no login required for the local single-recruiter setup).
2. Go to **Upload → Step 1** and define the hiring criteria: role title, required skills, experience, minimum score — plus the job description as text or file.
3. **Step 2**: drag in up to 80 resumes (PDF/DOCX). Each is parsed, classified and scored automatically.
4. Review the ranked candidate list; toggle **Blind Mode** (top bar) at any point to hide PII.
5. Shortlist or reject — automatically via the threshold, or manually per candidate.
6. Open **Emails** to send shortlist/rejection notifications individually, in bulk, or via custom templates.
7. Track everything on the **Dashboard** and **Reports** pages.

## API Overview

All endpoints are JSON under `/api`. Highlights:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Service health check |
| POST / GET | `/api/hiring` | Create / list hiring criteria |
| POST | `/api/candidates/upload` | Bulk upload resumes + optional JD file |
| GET | `/api/candidates?criteria_id=` | List/filter candidates |
| GET | `/api/candidates/ranking/<id>` | Ranked list for a hiring round |
| GET | `/api/candidates/<id>/blind` | PII-free candidate payload |
| PUT | `/api/candidates/<id>/status` | Manual shortlist / reject |
| POST | `/api/candidates/reparse-all` | Re-run extraction on all candidates |
| POST | `/api/email/send/<id>` · `/bulk/<id>` | Status emails (single / bulk) |
| POST | `/api/email/send-custom/<id>` · `/bulk-custom/<id>` | Custom-template emails |
| GET | `/api/email/logs` · `/config-status` | Delivery history / SMTP setup check |
| GET | `/api/dashboard/stats` · `/recent` | Dashboard aggregates |

## Project Structure

```
HireWise/
├── backend/
│   ├── app.py                  # Flask factory + blueprint registration
│   ├── config.py               # App configuration (DB, uploads, limits)
│   ├── models.py               # SQLAlchemy models
│   ├── routes/                 # REST endpoints (hiring, candidates, dashboard, email, ml)
│   ├── ml/
│   │   ├── preprocessor.py     # Text cleaning + PII/contact extraction
│   │   ├── model_trainer.py    # 4-algorithm comparison & persistence
│   │   ├── classifier.py       # Category prediction
│   │   ├── matcher.py          # Weighted scoring engine
│   │   ├── resume_parser.py    # PDF/DOCX extraction
│   │   └── models/             # Trained artifacts (generated, gitignored)
│   ├── services/email_service.py  # SMTP delivery + templates
│   ├── data/                   # Training dataset (generated, gitignored)
│   └── uploads/                # Candidate resumes (gitignored)
├── frontend/
│   └── src/
│       ├── app/                # Pages: dashboard, upload, candidates, emails, reports
│       ├── components/         # Tables, cards, forms, blind-mode toggle…
│       ├── context/            # BlindMode provider (global PII masking)
│       ├── lib/api.ts          # Typed API client
│       └── types/              # Shared TypeScript contracts
├── start_backend.ps1           # Windows launcher — backend
├── start_frontend.ps1          # Windows launcher — frontend
└── .gitignore                  # Secrets / PII / artifacts protection
```

## Security & Privacy

- **Secrets never enter the repo** — `backend/.env` (SMTP credentials, secret key), the SQLite database, uploaded resumes and app screenshots (which contain real candidate data) are all gitignored. `backend/.env.example` is the committable template.
- **Blind mode by design** — PII is masked client-side via a global context and served through a dedicated PII-free API payload for the blind review page.
- **Local-first data** — resumes are parsed and stored on your machine; no third-party resume-processing service is involved.
- **Gmail App Passwords** — recommended for SMTP to avoid storing your primary account password.

## Known Limitations

- The bundled model was trained on a **generated dataset** (960 synthetic resumes). The reported 100% accuracy reflects the distinct skill vocabularies of the synthetic categories, not real-world performance — retrain with labeled real resumes before production use.
- SQLite + Flask dev server make this a **single-recruiter, local tool** by design; multi-user auth and a production WSGI server are deployment work, not feature gaps.
- Contact extraction is heuristic-based; the reparse tooling and manual email editing exist precisely to correct edge cases.

## Roadmap

- Authentication & multi-recruiter workspaces
- Retraining on real labeled data + embedding-based semantic matching (e.g., sentence transformers)
- Dockerized one-command deployment
- Email scheduling and a template gallery
- Duplicate/Resume-version detection
- CSV/ATS export of shortlists

---

Built as a portfolio project to demonstrate an end-to-end ML product: parsing → classification → scoring → decisioning → communication.
