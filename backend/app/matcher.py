"""
matcher.py
----------
This file is responsible for ONE thing: taking an English work experience
description and returning the top 5 most similar NOC occupations.

Main function:
  get_match(text) -> list[Job]

HOW IT FITS INTO ROOTED:
  1. translator.py converts the user's input to English
  2. matcher.py embeds that English text with S-BERT
  3. matcher.py compares it against cached NOC occupation embeddings
  4. main.py returns the top matches to the frontend

TO USE THIS FILE:
  from app.matcher import get_match

  matches = get_match("I cooked food in a restaurant")
  print(matches[0]["job_title"])
  print(matches[0]["job_description"])

DATA NEEDED:
  backend/data/level5.csv

DEPENDENCIES:
  pip install -r backend/requirements.txt

ENVIRONMENT VARIABLES OPTIONAL:
  NOC_BASE_DIR    — project root override if auto-discovery fails
  NOC_INPUT_PATH  — custom path to level5.csv
  NOC_CACHE_DIR   — custom directory for generated embeddings/cache files
  HF_HOME         — custom Hugging Face model cache directory
"""

from __future__ import annotations

import json
import os
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import TypedDict


SCRIPT_DIR = Path(__file__).resolve().parent

def discover_base_dir() -> Path:
    """Find the repository root that contains the backend directory."""
    configured_base_dir = os.getenv("NOC_BASE_DIR")
    if configured_base_dir:
        return Path(configured_base_dir).expanduser().resolve()

    # The project root is the directory that contains the backend folder,
    # regardless of whether this file lives in backend/app or deeper.
    for parent in (SCRIPT_DIR, *SCRIPT_DIR.parents):
        if parent.name == "backend":
            return parent.parent.resolve()

    return SCRIPT_DIR.parent.resolve()


# Resolve all defaults from the project root so the script can move across
# machines without carrying any user-specific absolute paths.
BASE_DIR = discover_base_dir()


def resolve_path_from_base(raw_path: str | Path) -> Path:
    """Resolve relative paths against the shared project root."""
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path.resolve()
    return (BASE_DIR / path).resolve()


BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"
DEFAULT_INPUT_PATH = DATA_DIR / "level5.csv"
DEFAULT_CACHE_DIR = DATA_DIR / "cache"
CACHE_BASE_DIR = resolve_path_from_base(os.getenv("NOC_CACHE_DIR", DEFAULT_CACHE_DIR))
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

hf_home_value = Path(os.getenv("HF_HOME", CACHE_BASE_DIR / "huggingface")).expanduser()
if not hf_home_value.is_absolute():
    hf_home_value = (BASE_DIR / hf_home_value).resolve()
os.environ.setdefault("HF_HOME", str(hf_home_value))

import numpy as np
import pandas as pd
from transformers.utils import import_utils as transformers_import_utils

# This script only uses text models. Some environments have an incompatible
# optional torchvision install, so keep Transformers from importing vision code.
transformers_import_utils._torchvision_available = False
transformers_import_utils._torchvision_version = "disabled"

from sentence_transformers import SentenceTransformer
from transformers.utils import logging as transformers_logging

transformers_logging.set_verbosity_error()
transformers_logging.disable_progress_bar()


EMBEDDING_MODEL_REPO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
TOP_MATCHES = 5


class Job(TypedDict):
    rank: int
    job_title: str
    job_description: str
    full_job_description: str


HF_HOME_DIR = Path(os.environ["HF_HOME"]).expanduser().resolve()
# Keep compatibility with models that may already be cached outside the repo.
LEGACY_HF_HOME_DIR = (Path.home() / ".cache" / "huggingface").resolve()
EMBEDDING_CACHE_ROOT = (
    HF_HOME_DIR
    / "hub"
    / "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2"
)
EMBEDDING_LEGACY_CACHE_ROOT = (
    LEGACY_HF_HOME_DIR
    / "hub"
    / "models--sentence-transformers--paraphrase-multilingual-MiniLM-L12-v2"
)


def clean_text(value: object) -> str:
    """Normalize raw CSV text before embedding or display."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = text.replace(" | ", "; ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def build_occupation_text(row: pd.Series) -> str:
    """Combine the most job-descriptive NOC fields into one embedding string."""
    field_map = [
        ("Title", row.get("Class_Title")),
        ("Definition", row.get("Class_Definition")),
        ("Main duties", row.get("Main duties")),
        ("Example job titles", row.get("All examples")),
        ("Illustrative examples", row.get("Illustrative example(s)")),
        ("Employment requirements", row.get("Employment requirements")),
        ("Additional information", row.get("Additional information")),
        ("Inclusions", row.get("Inclusion(s)")),
    ]

    sections = []
    for label, raw_value in field_map:
        cleaned = clean_text(raw_value)
        if cleaned:
            sections.append(f"{label}: {cleaned}")
    return "\n".join(sections)


def short_job_description(full_description: str, max_chars: int = 280) -> str:
    """Build a compact display description from the full NOC text."""
    definition_match = re.search(
        r"Definition:\s*(.*?)(?:\nMain duties:|\n[A-Z][A-Za-z ]+:|$)",
        full_description,
        flags=re.S,
    )
    description = clean_text(definition_match.group(1) if definition_match else full_description)
    if len(description) <= max_chars:
        return description

    shortened = description[:max_chars].rsplit(" ", 1)[0].rstrip(" ;,.")
    return f"{shortened}..."


def resolve_input_path() -> Path:
    """Resolve the NOC dataset path from env config or project defaults."""
    configured_input = os.getenv("NOC_INPUT_PATH")
    if configured_input:
        candidate_paths = [resolve_path_from_base(configured_input)]
    else:
        candidate_paths = [DEFAULT_INPUT_PATH]

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    checked_paths = "\n".join(f"- {path}" for path in candidate_paths)
    raise SystemExit(
        "Could not find the input dataset. Checked:\n"
        f"{checked_paths}\n"
        "Set NOC_INPUT_PATH to point at your dataset."
    )


def resolve_cache_dir() -> Path:
    """Resolve and create the shared cache directory for embeddings."""
    raw_cache_dir = os.getenv("NOC_CACHE_DIR") or str(CACHE_BASE_DIR)
    cache_dir = resolve_path_from_base(raw_cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def cache_file_stem(input_path: Path) -> str:
    """Turn the input filename into a stable cache key."""
    stem = re.sub(r"[^a-z0-9]+", "_", input_path.stem.lower()).strip("_")
    return stem or "level5"


def resolve_cache_paths(input_path: Path, cache_dir: Path) -> tuple[Path, Path]:
    """Derive embedding and metadata cache files from the input dataset name."""
    stem = cache_file_stem(input_path)
    embeddings_path = cache_dir / f"{stem}_embeddings.npy"
    metadata_path = cache_dir / f"{stem}_metadata.json"
    return embeddings_path, metadata_path


def resolve_model_reference(cache_roots: list[Path], repo_id: str) -> tuple[str, bool]:
    """Use a local Hugging Face snapshot when available before trying the hub."""
    for cache_root in cache_roots:
        if not cache_root.exists():
            continue
        ref_path = cache_root / "refs" / "main"
        if ref_path.exists():
            revision = ref_path.read_text().strip()
            snapshot_path = cache_root / "snapshots" / revision
            if snapshot_path.exists():
                return str(snapshot_path), True
    return repo_id, False


@lru_cache(maxsize=1)
def load_embedding_model() -> SentenceTransformer:
    """Load the multilingual embedding model used for similarity search."""
    ref, is_local = resolve_model_reference(
        [EMBEDDING_CACHE_ROOT, EMBEDDING_LEGACY_CACHE_ROOT],
        EMBEDDING_MODEL_REPO,
    )
    try:
        return SentenceTransformer(ref, local_files_only=is_local)
    except TypeError:
        # Older sentence-transformers versions do not expose local_files_only.
        # Passing a resolved snapshot path still keeps local loads local.
        return SentenceTransformer(ref)


def load_dataset(input_path: Path) -> pd.DataFrame:
    # Step 1: load the raw occupation rows from the shared Level 5 CSV.
    if input_path.suffix.lower() != ".csv":
        raise SystemExit(
            f"Unsupported input file type '{input_path.suffix}'. Use level5.csv."
        )

    df = pd.read_csv(input_path)

    # Step 2: build the text block each occupation will be embedded from.
    df = df.copy()
    df["occupation_text"] = df.apply(build_occupation_text, axis=1)
    df = df[df["occupation_text"].str.len() > 0].reset_index(drop=True)
    return df


def load_or_build_embeddings(
    model: SentenceTransformer,
    df: pd.DataFrame,
    embeddings_path: Path,
    metadata_path: Path,
) -> tuple[np.ndarray, list[dict[str, object]]]:
    """Reuse cached occupation embeddings when the dataset shape has not changed."""
    embeddings_path.parent.mkdir(parents=True, exist_ok=True)

    metadata = [
        {
            "job_title": clean_text(row["Class_Title"]),
            "job_description": short_job_description(row["occupation_text"]),
            "full_job_description": row["occupation_text"],
        }
        for _, row in df.iterrows()
    ]

    if embeddings_path.exists() and metadata_path.exists():
        cached_metadata = json.loads(metadata_path.read_text())
        cached_embeddings = np.load(embeddings_path)
        if cached_metadata == metadata and cached_embeddings.shape[0] == len(metadata):
            return cached_embeddings, cached_metadata

    texts = [str(item["full_job_description"]) for item in metadata]
    
    #insert chunking here

    embeddings = model.encode(
        texts,
        batch_size=64,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    np.save(embeddings_path, embeddings)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    return embeddings, metadata


def get_match(text: str) -> list[Job]:
    """Return the top 5 matching jobs for a user query."""
    query = normalize_query_text(text)
    if not query:
        return []

    input_path = resolve_input_path()
    cache_dir = resolve_cache_dir()
    df = load_dataset(input_path)
    model = load_embedding_model()
    embeddings_path, metadata_path = resolve_cache_paths(input_path, cache_dir)
    embeddings, metadata = load_or_build_embeddings(
        model,
        df,
        embeddings_path,
        metadata_path,
    )

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )[0]
    similarities = embeddings @ query_embedding
    top_indices = np.argsort(similarities)[::-1][:TOP_MATCHES]

    jobs: list[Job] = []
    for rank, index in enumerate(top_indices, start=1):
        item = metadata[int(index)]
        full_description = str(
            item.get("full_job_description")
            or item.get("job_description")
            or item.get("occupation_text")
            or ""
        )
        jobs.append(
            {
                "rank": rank,
                "job_title": str(item.get("job_title") or item.get("title") or ""),
                "job_description": str(
                    item.get("job_description")
                    or short_job_description(full_description)
                ),
                "full_job_description": full_description,
            }
        )
    return jobs


def normalize_query_text(text: str) -> str:
    """Collapse whitespace so CLI and pasted text behave the same."""
    return re.sub(r"\s+", " ", text).strip()


def read_query_text(cli_query_parts: list[str]) -> str:
    """Accept query text from args, stdin, or an interactive paste session."""
    if cli_query_parts:
        return normalize_query_text(" ".join(cli_query_parts))

    if not sys.stdin.isatty():
        return normalize_query_text(sys.stdin.read())

    print("Paste the job description text, then press Enter twice to search:")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except EOFError:
            break

        if not line.strip():
            if lines:
                break
            continue

        lines.append(line)

    return normalize_query_text("\n".join(lines))


def bold_rank(rank: int) -> str:
    """Bold the rank number when the terminal supports ANSI formatting."""
    label = f"{rank}."
    if sys.stdout.isatty() and os.getenv("TERM", "").lower() != "dumb":
        return f"\033[1m{label}\033[0m"
    return label


def print_matches(jobs: list[Job]) -> None:
    """Print a compact ranked list for terminal use."""
    for job in jobs:
        print(f"{bold_rank(job['rank'])} Job: {job['job_title']}")
        print(f"  Description: {job['job_description']}")


def main() -> None:
    query = read_query_text(sys.argv[1:])
    if not query:
        raise SystemExit(
            "No query text was provided. Pass quoted text after the script name, pipe text into the script, or paste text when prompted."
        )
    print_matches(get_match(query))


if __name__ == "__main__":
    main()
