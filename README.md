# 🌱 Rooted

Rooted was built by five developers who are either immigrants or children of immigrants to Canada. We know firsthand how hard it is to navigate the system, especially when it comes to careers.

**Rooted is for refugees who don't know where to start, or who feel too overwhelmed to reach out to social services.** It meets you where you are: whether you have formal credentials, informal work experience, or no documents at all.

Tell Rooted what you've done in your own words. It matches your skills (formal or informal) to the Canadian NOC (National Occupational Classification) database and returns your top career pathway matches. For each match, you get a plain-language pathway card with the steps to take, estimated time and costs, and funding sources available to you. You can export this card and bring it to a settlement agency or social services for further help.

**Privacy first.** Rooted does not store, log, or retain any personal information. Everything you share is processed in memory and discarded when your session ends. This app is for the people, built with care and designed to be a tool you can trust.

Built for the [HuggingFace Build Small Hackathon](https://huggingface.co/build-small) and the AI4Good Lab (Mila/McGill, 2026).

---

## What it does

1. **Describe your experience** — type your work history in any language
2. **Get matched** — S-BERT matches your description to the 516 Canadian NOC unit groups
3. **See your pathway** — Llama 3.1 8B generates a step-by-step credential recognition card with estimated time, costs, and funding options

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + TypeScript + Vite |
| Backend | Python + FastAPI |
| Matching | S-BERT (`paraphrase-multilingual-MiniLM-L12-v2`) |
| Translation | NLLB-200 (`facebook/nllb-200-distilled-600M`) |
| Pathway generation | Llama 3.1 8B via HuggingFace Inference API (Novita) |
| NOC data | ESDC level5.csv (516 unit groups) |

---

## Prerequisites

- Python 3.10+
- Node.js 18+
- A [HuggingFace account](https://huggingface.co) with an API token

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/jamieleeserhuan/rooted.git
cd rooted
```

### 2. Set up the backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder:
```
HF_TOKEN=your_huggingface_token_here
```

Start the backend server:
```bash
uvicorn main:app --reload --port 8000
```

The backend runs at `http://localhost:8000`. You can verify it's working at `http://localhost:8000/health`.

### 3. Set up the frontend

Open a new terminal:

```bash
cd frontend
npm install
```

Create a `.env.local` file in the `frontend/` folder:
```
VITE_USE_MOCK=false
VITE_API_URL=http://localhost:3000
```

Start the frontend server:
```bash
npm run dev
```

### 4. Open the app

Go to `http://localhost:3000` in your browser.

---

## Running with mock data (no backend needed)

If you want to run the frontend without the Python backend:

In `frontend/.env.local`, set:
```
VITE_USE_MOCK=true
```

Then run `npm run dev` in the frontend folder. The app will use realistic mock NOC matches and pathway cards.

---

## Project structure

```
rooted/
├── backend/
│   ├── app/
│   │   ├── matcher.py       # S-BERT NOC matching
│   │   └── translator.py    # NLLB multilingual translation
│   ├── pathway.py           # Llama 3.1 8B pathway card generation
│   ├── main.py              # FastAPI entry point
│   ├── data/
│   │   └── level5.csv       # NOC dataset (516 unit groups)
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/
    │   │   ├── match.ts      # NOC matching API calls
    │   │   └── pathway.ts    # Pathway generation API calls
    │   ├── components/
    │   │   ├── Home.tsx
    │   │   ├── InputScreen.tsx
    │   │   ├── MatchResults.tsx
    │   │   └── PathwayScreen.tsx
    │   ├── App.tsx
    │   └── types.ts
    └── server.ts             # Express proxy server
```

---

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/match` | Translate + match description to NOC codes |
| `POST` | `/pathway` | Generate LLM pathway card for a NOC code |
| `GET` | `/health` | Check backend is running |

---

## Environment variables

### Backend (`backend/.env`)
| Variable | Required | Description |
|----------|----------|-------------|
| `HF_TOKEN` | Yes | HuggingFace API token for Llama 3.1 8B via Novita |

### Frontend (`frontend/.env.local`)
| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_USE_MOCK` | `false` | Set to `true` to run without backend |
| `VITE_API_URL` | `http://localhost:3000` | Frontend server URL |

---

## Team

Built at the AI4Good Lab (Mila/McGill) — May/June 2026.

---

## Disclaimer

Pathway cards are AI-generated and may not reflect the latest regulatory requirements. Always verify with the relevant regulatory body or a certified immigration professional.
