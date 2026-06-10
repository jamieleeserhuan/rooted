"""
pathway.py
----------
This file is responsible for ONE thing: taking a matched NOC occupation
(code, title, description) and generating a plain-language pathway card
that tells a refugee what steps to take to work in that field in Canada.

It uses Llama 3.1 8B (via HuggingFace Inference API, routed through Novita)
to generate the card content, then validates the output with Pydantic before
returning it — so the rest of the app always gets a clean, predictable object.

HOW IT FITS INTO ROOTED:
  1. User describes their work experience (frontend)
  2. S-BERT matches that description to NOC codes (matching pipeline, separate file)
  3. THIS FILE takes those NOC matches and generates pathway cards for each one
  4. The cards are returned to the frontend for display

TO USE THIS FILE:
  from pathway import generate_pathway_card, card_to_dict

  card = generate_pathway_card(
      noc_code="31301",
      title="Registered nurses and registered psychiatric nurses",
      definition="Registered nurses provide..."
  )
  print(card.occupation_title)
  print(card.steps[0].heading)

DEPENDENCIES:
  pip install huggingface_hub pydantic

ENVIRONMENT VARIABLES NEEDED:
  HF_TOKEN — your HuggingFace API token (set in .env or Colab Secrets)
"""

import json
import logging
import os
import re
from typing import Optional

from huggingface_hub import InferenceClient
from pydantic import BaseModel, Field, field_validator

# Set up logging so errors show up clearly without flooding the console
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("pathway")


# =============================================================================
# CLIENT SETUP
# Connects to HuggingFace's Inference API using the Novita provider.
# Novita gives us faster access to Llama 3.1 8B than the default HF endpoint.
# The token is read from environment variables — never hardcode it here.
# =============================================================================

def _get_client() -> InferenceClient:
    """
    Create the HuggingFace client on demand rather than at import time.
    This ensures HF_TOKEN is read after load_dotenv() has run in main.py.
    """
    token = os.environ.get("HF_TOKEN")
    if not token:
        raise ValueError(
            "HF_TOKEN environment variable is not set. "
            "Add it to backend/.env and make sure load_dotenv() is called in main.py."
        )
    return InferenceClient(
        provider="novita",
        api_key=token,
    )

# The specific LLM model we're using to generate pathway cards.
# Llama 3.1 8B is a good balance of quality and speed for this task.
MODEL = "meta-llama/llama-3.1-8b-instruct"


# =============================================================================
# DATA SCHEMAS (Pydantic models)
#
# These define the exact shape of a pathway card. Every card the LLM generates
# gets validated against these schemas before leaving this file.
#
# Why bother? Because LLMs sometimes return unexpected output (wrong field
# names, missing fields, wrong data types). Pydantic catches those problems
# early so the frontend never receives broken data.
# =============================================================================

class PathwayStep(BaseModel):
    """
    One step in the pathway — e.g. "Get your credentials assessed by WES".
    A card will have between 3 and 5 of these.
    """
    number: int          # Step number (1, 2, 3...)
    heading: str         # Short title for the step, e.g. "Get a credential assessment"
    description: str     # 1-2 sentences explaining what to do and why

    # Optional flag that highlights something important about this step.
    # The frontend uses this to show icons/badges next to the step.
    # Must be one of: "no_docs", "english_test", "fee", "assessment", or null.
    flag: Optional[str] = None

    @field_validator("flag")
    @classmethod
    def valid_flag(cls, v):
        """
        If the LLM returns an unrecognised flag value (e.g. "regulated"),
        quietly set it to null instead of crashing. We'd rather lose a badge
        than break the whole card.
        """
        if v not in {"no_docs", "english_test", "fee", "assessment", None}:
            return None
        return v


class PathwayCard(BaseModel):
    """
    The full pathway card for one NOC occupation.
    This is what gets returned to the frontend — one card per NOC match.
    """
    noc_code: str                      # e.g. "31301"
    occupation_title: str              # Official Canadian job title
    province: str = "Ontario"          # Province this pathway applies to (default Ontario)
    is_regulated: bool                 # True if this occupation requires a licence in Canada
    estimated_time_months_min: int     # Fastest realistic timeline to work in this field
    estimated_time_months_max: int     # More typical/conservative timeline
    typical_cost_cad: int              # Estimated cost in Canadian dollars to get started
    cost_note: str                     # Short note about what the cost covers, e.g. "to start"
    steps: list[PathwayStep] = Field(..., min_length=1, max_length=8)
    funding_note: Optional[str] = None # Any funding/bursary info if available
    disclaimer: str = (
        "This pathway is AI-generated and may not reflect the latest regulatory "
        "requirements. Always verify with the relevant regulatory body or a "
        "certified immigration/career professional."
    )

    @field_validator("estimated_time_months_min", "estimated_time_months_max")
    @classmethod
    def nonzero_time(cls, v):
        """
        The prompt uses 0 as a placeholder in the JSON template example.
        If the LLM copies those zeros instead of filling in real values,
        this validator catches it and triggers the fallback card instead.
        """
        if v == 0:
            raise ValueError("Model returned placeholder zero — triggering fallback")
        return v


# =============================================================================
# PROMPTS
#
# These are the instructions we send to Llama. The system prompt sets the
# persona and rules. The user prompt provides the specific NOC occupation
# and asks for a JSON card in return.
#
# Key design decisions:
# - We ask for JSON output so the frontend can parse it reliably
# - We tell the model to focus on credential recognition, not new degrees
#   (refugees already have skills — they need recognition, not retraining)
# - We mention limited documentation as a common refugee reality
# =============================================================================

SYSTEM_PROMPT = """You are a Canadian career counsellor helping newcomer refugees \
navigate credential recognition and employment. You give clear, plain-language guidance.
You are warm, encouraging, and realistic. You always note that rules can vary by \
province and that users should verify with the relevant regulatory body directly.
You never give legal or immigration advice.
The user already has foreign credentials and work experience from another country.
Never suggest obtaining a new Canadian degree as a first step.
Step 1 should always be about getting foreign credentials assessed or recognised, \
for example through WES (World Education Services) or the relevant regulatory body.
Assume the user fled with limited documents — always mention if a statutory \
declaration or verbal history is accepted as an alternative to official documents."""


# This is a template — {noc_code}, {title}, {definition} get filled in at runtime
# for each NOC match. The JSON block shows the model exactly what shape to return.
# The zeros in the JSON are placeholders — the IMPORTANT note tells the model to
# replace them with real values.
USER_PROMPT_TEMPLATE = """\
A refugee's work experience matched this Canadian occupation:

NOC Code: {noc_code}
Occupation Title: {title}
Description: {definition}

This person has real foreign work experience but may lack documentation. \
Focus on credential recognition and bridging pathways, not new degrees.

Return ONLY a valid JSON object — no markdown fences, no extra text:

{{
  "occupation_title": "official Canadian job title",
  "province": "Ontario",
  "is_regulated": true,
  "estimated_time_months_min": 0,
  "estimated_time_months_max": 0,
  "typical_cost_cad": 0,
  "cost_note": "to start",
  "steps": [
    {{
      "number": 1,
      "heading": "short heading",
      "description": "2 sentences max",
      "flag": "assessment"
    }}
  ],
  "funding_note": null
}}

IMPORTANT: The zeros above are FORMAT PLACEHOLDERS ONLY. \
Replace every numeric field with accurate, realistic values for this occupation in Canada.

Rules:
- 3 to 5 steps
- Use real regulatory body names (CNO for nurses, PEO for engineers, OCT for teachers)
- flag must be one of: "no_docs", "english_test", "fee", "assessment", or null
- Return ONLY JSON. No explanation before or after.\
"""


# =============================================================================
# JSON EXTRACTION
#
# Even when we ask Llama to return "ONLY JSON", it sometimes adds extra text
# before or after, or wraps the JSON in markdown code fences like ```json...```
# This function tries multiple strategies to extract valid JSON from whatever
# the model returns.
# =============================================================================

def _extract_json(raw: str) -> dict:
    """
    Pull a JSON object out of the raw LLM response string.
    Tries three strategies in order, from strictest to most lenient.
    Raises ValueError if none of them work.
    """
    text = raw.strip()

    # Strategy 1: the response IS valid JSON already — just parse it directly
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: strip markdown code fences (```json ... ``` or ``` ... ```)
    # then try parsing again
    fenced = re.sub(r"^```(?:json)?\s*", "", text, flags=re.MULTILINE)
    fenced = re.sub(r"\s*```$", "", fenced, flags=re.MULTILINE).strip()
    try:
        return json.loads(fenced)
    except json.JSONDecodeError:
        pass

    # Strategy 3: find the first { and match it to its closing } by counting
    # brace depth, then try to parse just that substring
    start = text.find("{")
    if start != -1:
        depth = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[start:i + 1])
                    except json.JSONDecodeError:
                        break

    raise ValueError(f"No valid JSON found in LLM output: {raw[:200]}")


# =============================================================================
# FALLBACK CARD
#
# If the LLM call fails for any reason (API error, bad JSON, validation error),
# we return this generic fallback card instead of crashing.
# The frontend always gets something to display — never a blank screen.
# =============================================================================

def _fallback_card(noc_code: str, title: str) -> PathwayCard:
    """
    Returns a minimal but useful pathway card when LLM generation fails.
    Points the user to WES and a settlement agency as safe universal first steps.
    """
    return PathwayCard(
        noc_code=noc_code,
        occupation_title=title,
        province="Ontario",
        is_regulated=False,
        estimated_time_months_min=3,
        estimated_time_months_max=12,
        typical_cost_cad=0,
        cost_note="varies by occupation and province",
        steps=[
            PathwayStep(
                number=1,
                heading="Get a credential assessment",
                description=(
                    "Contact WES (World Education Services) to have your foreign credentials "
                    "evaluated for Canadian equivalency. If you lack original documents, "
                    "ask about their statutory declaration option."
                ),
                flag="assessment",
            ),
            PathwayStep(
                number=2,
                heading="Connect with a settlement agency",
                description=(
                    "A local newcomer settlement agency (e.g. OCISO, ACCES Employment) "
                    "can help you navigate next steps specific to your province and occupation."
                ),
                flag=None,
            ),
        ],
        funding_note="Many settlement agencies offer free bridging support for refugees.",
    )


# =============================================================================
# IN-MEMORY CACHE
#
# Common occupations like nurses, teachers, and engineers will appear in many
# users' results. We cache cards by NOC code so we only call the LLM once per
# occupation per session, instead of making a fresh API call every time.
#
# Note: this cache resets when the server restarts. For production, you'd want
# to replace this with Redis or a database cache.
# =============================================================================

_pathway_cache: dict[str, PathwayCard] = {}


# =============================================================================
# MAIN FUNCTION — this is what the rest of the app calls
# =============================================================================

def generate_pathway_card(
    noc_code,                         # NOC code — accepts int or string (CSV loads it as int)
    title: str,                       # Occupation title from the NOC CSV
    definition: str,                  # Occupation definition/description from the NOC CSV
    force_refresh: bool = False,      # Set True to bypass cache and regenerate
) -> PathwayCard:
    """
    Generate a pathway card for a single NOC occupation.

    This is the main function to call from the rest of the app.
    It handles caching, LLM generation, JSON parsing, validation,
    and fallback — the caller just gets back a clean PathwayCard object.

    Example:
        card = generate_pathway_card("31301", "Registered nurses...", "RNs provide...")
        print(card.occupation_title)
        print(card.steps[0].description)
    """

    # Always convert to string first — the NOC CSV stores codes as integers
    # (np.int64) but our schema and cache keys expect strings
    noc_code = str(noc_code)

    # Return cached card if we've already generated one for this NOC code
    if not force_refresh and noc_code in _pathway_cache:
        logger.debug(f"Cache hit for NOC {noc_code}")
        return _pathway_cache[noc_code]

    # Build the prompt by filling in the NOC details
    user_prompt = USER_PROMPT_TEMPLATE.format(
        noc_code=noc_code,
        title=title,
        definition=definition[:600],  # cap length to stay within token limits
    )

    try:
        # Call the LLM
        response =  _get_client().chat_completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=700,
            temperature=0.2,  # low temperature = more consistent, less creative output
        )

        # Extract the raw text from the response
        raw = response.choices[0].message.content

        # Parse the JSON out of the raw text (handles fences, extra text, etc.)
        data = _extract_json(raw)

        # Add the NOC code — the model doesn't output this field, we add it ourselves
        data["noc_code"] = noc_code

        # Validate the parsed data against our PathwayCard schema.
        # If any field is wrong or missing, this raises a ValidationError
        # which gets caught by the except block below.
        card = PathwayCard.model_validate(data)

    except Exception as e:
        # Something went wrong — log it and return the fallback card instead
        logger.error(f"Pathway generation failed for NOC {noc_code} ({title}): {e}")
        card = _fallback_card(noc_code, title)

    # Store in cache before returning
    _pathway_cache[noc_code] = card
    return card


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def card_to_dict(card: PathwayCard) -> dict:
    """
    Convert a PathwayCard object to a plain Python dict.
    Use this when you need to send the card as JSON (e.g. from a FastAPI endpoint)
    or pass it to Gradio.

    Example:
        card = generate_pathway_card(...)
        card_dict = card_to_dict(card)
        return JSONResponse(content=card_dict)  # in FastAPI
    """
    return card.model_dump()


def generate_cards_for_matches(matches: list[dict]) -> list[dict]:
    """
    Convenience function: takes the full list of NOC matches from the S-BERT
    pipeline and generates a pathway card for each one.

    Input (from match_noc()):
        [
            {
                "rank": 1,
                "noc_code": "31301",
                "job_title": "Registered nurses...",
                "job_description": "Short readable summary...",
                "full_job_description": "Full NOC text..."
            },
            ...
        ]

    Output (ready for the frontend):
        [
            {
                "noc_code": "31301",
                "title": "Registered nurses...",
                "score": 0.82,
                "pathway_card": { ...all PathwayCard fields as a dict... }
            },
            ...
        ]
    """
    results = []
    for match in matches:
        title = match.get("title") or match.get("job_title", "")
        definition = (
            match.get("definition")
            or match.get("full_job_description")
            or match.get("job_description", "")
        )
        card = generate_pathway_card(
            noc_code=match["noc_code"],
            title=title,
            definition=definition,
        )
        result = {
            "noc_code": match["noc_code"],
            "title": title,
            "pathway_card": card_to_dict(card),
        }
        if "score" in match:
            result["score"] = match["score"]
        results.append(result)
    return results


# =============================================================================
# PRETTY PRINT (for Colab / terminal testing only — not used by the frontend)
# =============================================================================

# Maps flag codes to human-readable labels for terminal output
FLAG_LABELS = {
    "no_docs": " No documents needed to start",
    "english_test": " English language test required",
    "fee": " Fee required",
    "assessment": " Credential assessment required",
}


def print_card(match_rank: int, noc_code: str, score: float, card: PathwayCard) -> None:
    """
    Print a pathway card to the terminal in a readable format.
    Used in rooted_pipeline() for Colab testing — not called by the frontend.
    """
    print(f"\n{'=' * 70}")
    print(f"MATCH {match_rank} — {card.occupation_title}  (NOC {noc_code})")
    print(f"Similarity score: {score}  |  Province: {card.province}")
    print(f"Regulated occupation: {'Yes' if card.is_regulated else 'No'}")
    print(f"Estimated time: {card.estimated_time_months_min}–{card.estimated_time_months_max} months")
    print(f"Typical cost: ${card.typical_cost_cad:,} {card.cost_note}")
    if card.funding_note:
        print(f" Funding available: {card.funding_note}")
    print("\nStep by step:")
    for step in card.steps:
        print(f"\n  {step.number}. {step.heading}")
        print(f"     {step.description}")
        if step.flag:
            print(f"     {FLAG_LABELS.get(step.flag, step.flag)}")
    print(f"\n {card.disclaimer}")
