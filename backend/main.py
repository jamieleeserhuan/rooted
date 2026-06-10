"""
main.py
-------
This is the entry point for the Rooted backend server.

It creates a FastAPI web server and defines the API endpoints that the
frontend calls. It imports the three core modules and wires them together:

  - app/translator.py  (teammate) — detects and translates input to English
  - app/matcher.py     (teammate) — matches English text to NOC codes via S-BERT
  - pathway.py         (Jamie)    — generates LLM pathway cards via Llama 3.1 8B

HOW TO RUN:
  cd rooted/backend
  uvicorn main:app --reload --port 8000

ENDPOINTS:
  POST /match    — translate input + return top NOC matches
  POST /pathway  — generate a pathway card for a given NOC code
  GET  /health   — check that the server is running
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import teammate's modules from the app/ subfolder
from app.matcher import get_match
from app.translator import translate_text, resolve_source_language

# Import Jamie's pathway module from the backend root
from pathway import generate_pathway_card, card_to_dict


# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

# Create the FastAPI application instance.
# The title shows up in the auto-generated API docs at /docs
app = FastAPI(title="Rooted API", version="0.1.0")


# ---------------------------------------------------------------------------
# CORS middleware
#
# CORS (Cross-Origin Resource Sharing) allows the frontend (running on
# localhost:3000 or localhost:5173) to make requests to this backend
# (running on localhost:8000). Without this, the browser blocks the requests.
# In production, replace these with your actual deployed frontend URL.
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Node/Express frontend (server.ts)
        "http://localhost:5173",   # Vite dev server
    ],
    allow_credentials=True,
    allow_methods=["*"],           # Allow GET, POST, etc.
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# /match endpoint
# Owned by: teammate (matcher.py + translator.py)
# Called by: frontend when user submits their work experience description
#
# Flow:
#   1. Receive user's raw text (may be in any language)
#   2. Detect the source language (or use the one provided)
#   3. Translate the text to English so S-BERT can match it properly
#   4. Run S-BERT matching against the 516 NOC unit groups
#   5. Return the top 5 matches
# ---------------------------------------------------------------------------

class MatchRequest(BaseModel):
    description: str            # User's free-text work experience description
    source_lang: str = "auto"   # Language code e.g. "fr", "ar", or "auto" to detect


@app.post("/match")
def match_noc(req: MatchRequest):
    """
    Translate the user's description to English then match it to NOC codes.
    Returns a list of the top matching occupations with titles and descriptions.
    """
    try:
        # Step 1: resolve the source language
        # If source_lang is "auto", this detects it from the text itself
        detected_lang = resolve_source_language(req.source_lang, req.description)

        # Step 2: translate to English
        # S-BERT was trained mostly on English NOC text, so we translate first
        # If text is already English, translate_text returns it unchanged
        english_text = translate_text(
            text=req.description,
            source_lang=detected_lang,
            target_lang="eng_Latn",
        )

        # Step 3: run S-BERT matching against the NOC corpus
        # Returns a list of Job dicts with rank, job_title, job_description
        matches = get_match(english_text)

        return {
            "matches": matches,
            "detected_language": detected_lang,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------------------------------------------------------------------
# /pathway endpoint
# Owned by: Jamie (pathway.py)
# Called by: frontend when user clicks on a NOC match to see their pathway
#
# Flow:
#   1. Receive a NOC code, title, and definition from the frontend
#   2. Call generate_pathway_card() which sends a prompt to Llama 3.1 8B
#   3. Validate the LLM output with Pydantic (happens inside pathway.py)
#   4. Return the pathway card as a JSON dict
# ---------------------------------------------------------------------------

class PathwayRequest(BaseModel):
    noc_code: str         # NOC code string e.g. "31301"
    title: str            # Occupation title e.g. "Registered nurses"
    definition: str = ""  # Full NOC definition — used to prompt the LLM


@app.post("/pathway")
def get_pathway(req: PathwayRequest):
    """
    Generate an LLM-powered pathway card for a given NOC occupation.
    Returns estimated time, cost, step-by-step guidance, and funding info.
    Falls back to a generic card if the LLM call fails.
    """
    # generate_pathway_card handles all error cases internally and never raises
    # — it returns a fallback card if anything goes wrong
    card = generate_pathway_card(
        noc_code=req.noc_code,
        title=req.title,
        definition=req.definition,
    )

    # card_to_dict converts the Pydantic PathwayCard object to a plain dict
    # so FastAPI can serialise it to JSON
    return card_to_dict(card)


# ---------------------------------------------------------------------------
# /health endpoint
# Simple check to confirm the server is running.
# Useful for deployment monitoring and debugging.
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    """Returns ok if the server is running."""
    return {"status": "ok", "version": "0.1.0"}
