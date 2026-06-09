from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path


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
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DEFAULT_INPUT_PATH = DATA_DIR / "level5.xlsx"
DEFAULT_CACHE_DIR = DATA_DIR / "cache"
CACHE_BASE_DIR = resolve_path_from_base(os.getenv("NOC_CACHE_DIR", DEFAULT_CACHE_DIR))


def discover_local_pydeps() -> Path:
    """Locate optional local Python dependencies shipped with the project."""
    configured_pydeps = os.getenv("NOC_PYDEPS_DIR")
    if configured_pydeps:
        return resolve_path_from_base(configured_pydeps)

    for candidate in (
        SCRIPT_DIR / "pydeps",
        BASE_DIR / "work" / "pydeps",
        BACKEND_DIR / "pydeps",
    ):
        if candidate.exists():
            return candidate.resolve()

    return (BASE_DIR / "work" / "pydeps").resolve()


LOCAL_PYDEPS = discover_local_pydeps()
BOOTSTRAP_FLAG = "NOC_SIMILARITY_BOOTSTRAPPED"
REQUIRED_RUNTIME_IMPORTS = (
    "numpy",
    "pandas",
    "torch",
    "sentence_transformers",
    "transformers",
)
os.environ.setdefault("TRANSFORMERS_NO_ADVISORY_WARNINGS", "1")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")

hf_home_value = Path(os.getenv("HF_HOME", CACHE_BASE_DIR / "huggingface")).expanduser()
if not hf_home_value.is_absolute():
    hf_home_value = (BASE_DIR / hf_home_value).resolve()
os.environ.setdefault("HF_HOME", str(hf_home_value))


def runtime_candidates() -> list[Path]:
    """Return Python runtimes to try before falling back to the current one."""
    candidates: list[Path] = []

    configured_runtime = os.getenv("NOC_PYTHON_RUNTIME")
    if configured_runtime:
        configured_path = Path(configured_runtime).expanduser()
        if not configured_path.is_absolute():
            configured_path = BASE_DIR / configured_path
        candidates.append(configured_path.absolute())

    # The active interpreter is the least surprising choice when it already has
    # the ML packages installed.
    candidates.append(Path(sys.executable).expanduser().absolute())

    # Prefer repository-local virtual environments when they exist.
    for relative_path in (
        ".venv/bin/python3",
        "backend/.venv/bin/python3",
        "venv/bin/python3",
        ".venv/Scripts/python.exe",
        "backend/.venv/Scripts/python.exe",
    ):
        candidates.append((BASE_DIR / relative_path).absolute())

    # If a venv is active but missing packages, try the base Python that created
    # it. This helps on local machines where ML packages are installed globally.
    base_python_dir = "Scripts" if os.name == "nt" else "bin"
    base_python_name = "python.exe" if os.name == "nt" else "python3"
    candidates.append(
        (Path(sys.base_prefix) / base_python_dir / base_python_name).absolute()
    )

    # Fall back to a Codex runtime if one is installed for the current user.
    codex_runtime = (
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "python"
        / "bin"
        / "python3"
    )
    candidates.append(codex_runtime.absolute())
    return candidates


def runtime_has_required_packages(candidate: Path) -> bool:
    """Check that a candidate interpreter can import the matcher dependencies."""
    if not candidate.exists():
        return False

    imports = "; ".join(f"import {module}" for module in REQUIRED_RUNTIME_IMPORTS)
    result = subprocess.run(
        [str(candidate), "-c", imports],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def resolve_runtime_python() -> Path | None:
    """Pick the first runtime that actually has the required ML packages."""
    seen: set[Path] = set()
    for candidate in runtime_candidates():
        if candidate in seen:
            continue
        seen.add(candidate)
        if runtime_has_required_packages(candidate):
            return candidate
    return None


def ensure_runtime() -> None:
    """Re-launch with a configured runtime so project deps are available."""
    if os.environ.get(BOOTSTRAP_FLAG) == "1":
        return

    runtime_python = resolve_runtime_python()
    if runtime_python is None:
        missing = ", ".join(REQUIRED_RUNTIME_IMPORTS)
        raise SystemExit(
            "Could not find a Python runtime with the matcher dependencies. "
            f"Install them with 'pip install -r backend/requirements.txt'. "
            f"Required imports: {missing}."
        )

    if Path(sys.executable).expanduser().absolute() == runtime_python.absolute():
        return

    env = os.environ.copy()
    env[BOOTSTRAP_FLAG] = "1"

    extra_paths = []
    if LOCAL_PYDEPS.exists():
        extra_paths.append(str(LOCAL_PYDEPS))
    if env.get("PYTHONPATH"):
        extra_paths.append(env["PYTHONPATH"])
    if extra_paths:
        env["PYTHONPATH"] = os.pathsep.join(extra_paths)

    os.execvpe(str(runtime_python), [str(runtime_python), __file__, *sys.argv[1:]], env)


ensure_runtime()

import numpy as np
import pandas as pd
import torch
from transformers.utils import import_utils as transformers_import_utils

# This script only uses text models. Some environments have an incompatible
# optional torchvision install, so keep Transformers from importing vision code.
transformers_import_utils._torchvision_available = False
transformers_import_utils._torchvision_version = "disabled"

from sentence_transformers import SentenceTransformer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers.utils import logging as transformers_logging

transformers_logging.set_verbosity_error()
transformers_logging.disable_progress_bar()


DEFAULT_SHEET_NAME = "noc_merged_level5"
EMBEDDING_MODEL_REPO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
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
TRANSLATION_MODEL_REPO = "facebook/nllb-200-distilled-600M"
TRANSLATION_CACHE_ROOT = (
    HF_HOME_DIR
    / "hub"
    / "models--facebook--nllb-200-distilled-600M"
)
TRANSLATION_LEGACY_CACHE_ROOT = (
    LEGACY_HF_HOME_DIR
    / "hub"
    / "models--facebook--nllb-200-distilled-600M"
)

LANGUAGE_ALIASES = {
    "english": "eng_Latn",
    "en": "eng_Latn",
    "eng": "eng_Latn",
    "spanish": "spa_Latn",
    "es": "spa_Latn",
    "spa": "spa_Latn",
    "french": "fra_Latn",
    "fr": "fra_Latn",
    "fra": "fra_Latn",
    "german": "deu_Latn",
    "de": "deu_Latn",
    "deu": "deu_Latn",
    "italian": "ita_Latn",
    "it": "ita_Latn",
    "ita": "ita_Latn",
    "portuguese": "por_Latn",
    "pt": "por_Latn",
    "por": "por_Latn",
    "brazilian-portuguese": "por_Latn",
    "brazilian portuguese": "por_Latn",
    "romanian": "ron_Latn",
    "ro": "ron_Latn",
    "ron": "ron_Latn",
    "dutch": "nld_Latn",
    "nl": "nld_Latn",
    "nld": "nld_Latn",
    "catalan": "cat_Latn",
    "ca": "cat_Latn",
    "cat": "cat_Latn",
    "polish": "pol_Latn",
    "pl": "pol_Latn",
    "pol": "pol_Latn",
    "turkish": "tur_Latn",
    "tr": "tur_Latn",
    "tur": "tur_Latn",
    "czech": "ces_Latn",
    "cs": "ces_Latn",
    "ces": "ces_Latn",
    "slovak": "slk_Latn",
    "sk": "slk_Latn",
    "slk": "slk_Latn",
    "slovenian": "slv_Latn",
    "sl": "slv_Latn",
    "slv": "slv_Latn",
    "danish": "dan_Latn",
    "da": "dan_Latn",
    "dan": "dan_Latn",
    "swedish": "swe_Latn",
    "sv": "swe_Latn",
    "swe": "swe_Latn",
    "finnish": "fin_Latn",
    "fi": "fin_Latn",
    "fin": "fin_Latn",
    "norwegian": "nob_Latn",
    "no": "nob_Latn",
    "nob": "nob_Latn",
    "ukrainian": "ukr_Cyrl",
    "uk": "ukr_Cyrl",
    "ukr": "ukr_Cyrl",
    "russian": "rus_Cyrl",
    "ru": "rus_Cyrl",
    "rus": "rus_Cyrl",
    "bulgarian": "bul_Cyrl",
    "bg": "bul_Cyrl",
    "bul": "bul_Cyrl",
    "greek": "ell_Grek",
    "el": "ell_Grek",
    "ell": "ell_Grek",
    "arabic": "arb_Arab",
    "ar": "arb_Arab",
    "arb": "arb_Arab",
    "hebrew": "heb_Hebr",
    "he": "heb_Hebr",
    "heb": "heb_Hebr",
    "persian": "fas_Arab",
    "farsi": "fas_Arab",
    "fa": "fas_Arab",
    "fas": "fas_Arab",
    "urdu": "urd_Arab",
    "ur": "urd_Arab",
    "urd": "urd_Arab",
    "hindi": "hin_Deva",
    "hi": "hin_Deva",
    "hin": "hin_Deva",
    "bengali": "ben_Beng",
    "bn": "ben_Beng",
    "ben": "ben_Beng",
    "punjabi": "pan_Guru",
    "pa": "pan_Guru",
    "pan": "pan_Guru",
    "gujarati": "guj_Gujr",
    "gu": "guj_Gujr",
    "guj": "guj_Gujr",
    "marathi": "mar_Deva",
    "mr": "mar_Deva",
    "mar": "mar_Deva",
    "tamil": "tam_Taml",
    "ta": "tam_Taml",
    "tam": "tam_Taml",
    "telugu": "tel_Telu",
    "te": "tel_Telu",
    "tel": "tel_Telu",
    "kannada": "kan_Knda",
    "kn": "kan_Knda",
    "kan": "kan_Knda",
    "malayalam": "mal_Mlym",
    "ml": "mal_Mlym",
    "mal": "mal_Mlym",
    "thai": "tha_Thai",
    "th": "tha_Thai",
    "tha": "tha_Thai",
    "vietnamese": "vie_Latn",
    "vi": "vie_Latn",
    "vie": "vie_Latn",
    "indonesian": "ind_Latn",
    "id": "ind_Latn",
    "ind": "ind_Latn",
    "malay": "msa_Latn",
    "ms": "msa_Latn",
    "msa": "msa_Latn",
    "tagalog": "tgl_Latn",
    "filipino": "tgl_Latn",
    "tl": "tgl_Latn",
    "tgl": "tgl_Latn",
    "chinese": "zho_Hans",
    "zh": "zho_Hans",
    "zh-cn": "zho_Hans",
    "zh-hans": "zho_Hans",
    "zh-tw": "zho_Hant",
    "zh-hant": "zho_Hant",
    "japanese": "jpn_Jpan",
    "ja": "jpn_Jpan",
    "jpn": "jpn_Jpan",
    "korean": "kor_Hang",
    "ko": "kor_Hang",
    "kor": "kor_Hang",
}

ENGLISH_STOPWORDS = {
    "a",
    "about",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "i",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "them",
    "they",
    "this",
    "to",
    "was",
    "were",
    "with",
    "work",
    "worked",
    "working",
}


def clean_text(value: object) -> str:
    """Normalize raw spreadsheet text before embedding or display."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text = text.replace(" | ", "; ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_term(term: str) -> str:
    """Apply light stemming so overlap terms are a bit less brittle."""
    normalized = term.lower()
    for suffix in ("ing", "ers", "ies", "ied", "ed", "es", "s"):
        if normalized.endswith(suffix) and len(normalized) >= 5:
            if suffix in {"ies", "ied"}:
                return normalized[: -len(suffix)] + "y"
            return normalized[: -len(suffix)]
    return normalized


def english_terms(text: str) -> list[str]:
    """Extract simple English keyword candidates from the translated query text."""
    return re.findall(r"[a-zA-Z][a-zA-Z'-]{1,}", text.lower())


def extract_matched_terms(query_text: str, occupation_text: str, limit: int = 5) -> list[str]:
    """Return approximate overlap terms that help explain a semantic match.

    The similarity search is embedding-based, so these terms are only a heuristic
    explanation layer built from the English query and the occupation text.
    """
    query_terms = english_terms(query_text)
    occupation_terms = english_terms(occupation_text)

    query_terms_by_root: dict[str, str] = {}
    for term in query_terms:
        if term in ENGLISH_STOPWORDS:
            continue
        root = normalize_term(term)
        query_terms_by_root.setdefault(root, term)

    occupation_roots = {
        normalize_term(term)
        for term in occupation_terms
        if term not in ENGLISH_STOPWORDS
    }

    matched_terms: list[str] = []
    for root, original_term in query_terms_by_root.items():
        if root in occupation_roots and original_term not in matched_terms:
            matched_terms.append(original_term)
        if len(matched_terms) >= limit:
            break

    return matched_terms


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


def resolve_input_path(input_path_arg: str | None) -> Path:
    """Resolve the dataset path from CLI/env input or project data defaults."""
    if input_path_arg:
        candidate_paths = [resolve_path_from_base(input_path_arg)]
    else:
        configured_input = os.getenv("NOC_INPUT_PATH")
        if configured_input:
            candidate_paths = [resolve_path_from_base(configured_input)]
        else:
            # Prefer the current project data layout, then fall back to older
            # processed/raw filenames that may exist during migration.
            candidate_paths = [
                DEFAULT_INPUT_PATH,
                DATA_DIR / "level5.csv",
                PROCESSED_DATA_DIR / "level5.xlsx",
                PROCESSED_DATA_DIR / "level5.csv",
                PROCESSED_DATA_DIR / "noc_merged_level5.xlsx",
                PROCESSED_DATA_DIR / "noc_merged_level5.csv",
                RAW_DATA_DIR / "noc_merged_level5.xlsx",
            ]

    for candidate in candidate_paths:
        if candidate.exists():
            return candidate

    checked_paths = "\n".join(f"- {path}" for path in candidate_paths)
    raise SystemExit(
        "Could not find the input dataset. Checked:\n"
        f"{checked_paths}\n"
        "Set NOC_INPUT_PATH or pass --input-path to point at your dataset."
    )


def resolve_cache_dir(cache_dir_arg: str | None) -> Path:
    """Resolve and create the shared cache directory for embeddings."""
    raw_cache_dir = cache_dir_arg or os.getenv("NOC_CACHE_DIR") or str(CACHE_BASE_DIR)
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


@lru_cache(maxsize=1)
def load_translation_tokenizer():
    """Load the NLLB tokenizer used for translation in and out of English."""
    ref, is_local = resolve_model_reference(
        [TRANSLATION_CACHE_ROOT, TRANSLATION_LEGACY_CACHE_ROOT],
        TRANSLATION_MODEL_REPO,
    )
    try:
        return AutoTokenizer.from_pretrained(ref, local_files_only=is_local)
    except OSError as exc:
        raise SystemExit(
            "The translation model facebook/nllb-200-distilled-600M is not "
            "available locally yet. Run once with network access to download it, "
            "or ask Codex to fetch it for you."
        ) from exc


@lru_cache(maxsize=1)
def load_translation_model() -> AutoModelForSeq2SeqLM:
    """Load the NLLB seq2seq model used only for translation."""
    ref, is_local = resolve_model_reference(
        [TRANSLATION_CACHE_ROOT, TRANSLATION_LEGACY_CACHE_ROOT],
        TRANSLATION_MODEL_REPO,
    )
    try:
        model = AutoModelForSeq2SeqLM.from_pretrained(ref, local_files_only=is_local)
    except OSError as exc:
        raise SystemExit(
            "The translation model facebook/nllb-200-distilled-600M is not "
            "available locally yet. Run once with network access to download it, "
            "or ask Codex to fetch it for you."
        ) from exc
    model.eval()
    return model


def canonical_language_code(language: str) -> str:
    """Map short aliases like 'es' to the NLLB language code."""
    if not language:
        return "auto"

    normalized = language.strip()
    if not normalized:
        return "auto"

    lower = normalized.lower()
    if lower == "auto":
        return "auto"

    if normalized in LANGUAGE_ALIASES.values():
        return normalized
    if lower in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[lower]
    if re.fullmatch(r"[a-z]{3}_[A-Z][a-z]{3,4}", normalized):
        return normalized

    supported = ", ".join(sorted(list(LANGUAGE_ALIASES.keys()))[:12])
    raise SystemExit(
        f"Unsupported source language '{language}'. Use an NLLB code such as "
        f"'spa_Latn' or a common alias like 'es'. Sample aliases: {supported}."
    )


def detect_source_language(text: str) -> str:
    """Use lightweight heuristics when the caller does not pass --source-lang."""
    lowered = text.lower()

    if re.search(r"[\u4e00-\u9fff]", text):
        return "zho_Hans"
    if re.search(r"[\u3040-\u30ff]", text):
        return "jpn_Jpan"
    if re.search(r"[\uac00-\ud7af]", text):
        return "kor_Hang"
    if re.search(r"[\u0600-\u06ff]", text):
        return "arb_Arab"
    if re.search(r"[\u0590-\u05ff]", text):
        return "heb_Hebr"
    if re.search(r"[\u0370-\u03ff]", text):
        return "ell_Grek"
    if re.search(r"[\u0900-\u097f]", text):
        return "hin_Deva"
    if re.search(r"[\u0980-\u09ff]", text):
        return "ben_Beng"
    if re.search(r"[\u0a00-\u0a7f]", text):
        return "pan_Guru"
    if re.search(r"[\u0a80-\u0aff]", text):
        return "guj_Gujr"
    if re.search(r"[\u0b80-\u0bff]", text):
        return "tam_Taml"
    if re.search(r"[\u0c00-\u0c7f]", text):
        return "tel_Telu"
    if re.search(r"[\u0c80-\u0cff]", text):
        return "kan_Knda"
    if re.search(r"[\u0d00-\u0d7f]", text):
        return "mal_Mlym"
    if re.search(r"[\u0e00-\u0e7f]", text):
        return "tha_Thai"
    if re.search(r"[\u0400-\u04ff]", text):
        return "ukr_Cyrl" if re.search(r"[іїєґ]", lowered) else "rus_Cyrl"

    if re.search(
        r"\b(trabajaba|alumnos|escuela|infantes|niños|ciencias|enseñé|docente|universidad|tenia|pasantia|banco|papeleo|clientes|necesidades|transaciones|basicos)\b",
        lowered,
    ) or re.search(r"[ñáéíóúü¿¡]", lowered):
        return "spa_Latn"
    if re.search(
        r"\b(école|enfants|enseignais|université|lycée)\b",
        lowered,
    ) or re.search(r"[àâæçéèêëîïôœùûüÿ]", lowered):
        return "fra_Latn"
    if re.search(
        r"\b(escola|crianças|ciências|universidade|ensinei|trabalhava)\b",
        lowered,
    ) or re.search(r"[ãõ]", lowered):
        return "por_Latn"
    if re.search(r"\b(lehrer|schule|kinder|wissenschaft)\b", lowered):
        return "deu_Latn"

    return "eng_Latn"


def resolve_source_language(language: str, text: str) -> str:
    """Choose the explicit source language or fall back to auto-detection."""
    canonical = canonical_language_code(language)
    if canonical != "auto":
        return canonical
    return detect_source_language(text)


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate with NLLB while keeping retrieval itself in English."""
    normalized = normalize_query_text(text)
    if not normalized or source_lang == target_lang:
        return normalized

    tokenizer = load_translation_tokenizer()
    model = load_translation_model()
    target_lang_id = tokenizer.convert_tokens_to_ids(target_lang)
    if target_lang_id == tokenizer.unk_token_id:
        raise SystemExit(
            f"Unsupported NLLB target language code '{target_lang}'."
        )
    tokenizer.src_lang = source_lang
    inputs = tokenizer(normalized, return_tensors="pt", truncation=True)

    with torch.inference_mode():
        output_tokens = model.generate(
            **inputs,
            forced_bos_token_id=target_lang_id,
            max_new_tokens=128,
            num_beams=4,
        )

    translated = tokenizer.batch_decode(output_tokens, skip_special_tokens=True)
    return normalize_query_text(translated[0] if translated else "")


@lru_cache(maxsize=512)
def translate_term(term: str, source_lang: str, target_lang: str) -> str:
    """Cache small term translations so multilingual result formatting stays fast."""
    return translate_text(term, source_lang, target_lang)


def translate_matched_terms(
    matched_terms: list[str], source_lang: str, target_lang: str
) -> list[str]:
    """Translate the matched-term explainer into the user's source language."""
    if source_lang == target_lang:
        return matched_terms

    translated_terms: list[str] = []
    for term in matched_terms:
        translated = translate_term(term, source_lang, target_lang)
        translated_terms.append(translated or term)
    return translated_terms


def load_dataset(input_path: Path, sheet_name: str) -> pd.DataFrame:
    # Step 1: load the raw occupation rows from CSV or Excel.
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        df = pd.read_csv(input_path)
    elif suffix in {".xlsx", ".xls"}:
        df = pd.read_excel(input_path, sheet_name=sheet_name)
    else:
        raise SystemExit(
            f"Unsupported input file type '{input_path.suffix}'. Use CSV or Excel."
        )

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
            "title": clean_text(row["Class_Title"]),
            "noc_code": str(row["NOC_Code"]),
            "occupation_text": row["occupation_text"],
        }
        for _, row in df.iterrows()
    ]

    if embeddings_path.exists() and metadata_path.exists():
        cached_metadata = json.loads(metadata_path.read_text())
        if len(cached_metadata) == len(metadata):
            return np.load(embeddings_path), cached_metadata

    texts = [item["occupation_text"] for item in metadata]
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


def search(
    query: str,
    top_k: int,
    input_path: Path,
    sheet_name: str,
    cache_dir: Path,
) -> list[dict[str, object]]:
    # Step 3: load the dataset and reuse cached occupation embeddings when possible.
    df = load_dataset(input_path, sheet_name)
    model = load_embedding_model()
    embeddings_path, metadata_path = resolve_cache_paths(input_path, cache_dir)
    embeddings, metadata = load_or_build_embeddings(
        model,
        df,
        embeddings_path,
        metadata_path,
    )

    # Step 4: embed the user query and rank occupations by cosine similarity.
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )[0]
    similarities = embeddings @ query_embedding
    top_indices = np.argsort(similarities)[::-1][:top_k]

    results = []
    for index in top_indices:
        item = metadata[int(index)]
        results.append(
            {
                "title": item["title"],
                "noc_code": item["noc_code"],
                "similarity": float(similarities[int(index)]),
                "matched_terms": extract_matched_terms(query, item["occupation_text"]),
            }
        )
    return results


def normalize_query_text(text: str) -> str:
    """Collapse whitespace so CLI, pasted, and translated text behave the same."""
    return re.sub(r"\s+", " ", text).strip()


def supports_bold_output() -> bool:
    """Use ANSI bold in interactive terminals when the terminal supports it."""
    return sys.stdout.isatty() and os.getenv("TERM", "").lower() != "dumb"


def format_rank(rank: int, use_bold: bool) -> str:
    """Render the ranking label, optionally using ANSI bold for terminals."""
    label = f"{rank}."
    if use_bold:
        return f"\033[1m{label}\033[0m"
    return label


def format_match_line(
    rank: int,
    title: str,
    noc_code: str,
    similarity: float,
    matched_terms: list[str],
) -> str:
    """Render one result line for CLI output."""
    parts = [format_rank(rank, supports_bold_output()), title, noc_code, f"{similarity:.4f}"]
    if matched_terms:
        parts.append(f"matched terms: {', '.join(matched_terms)}")
    return "\t".join(parts)


def print_ranked_matches(results: list[dict[str, object]], title_key: str = "title") -> None:
    """Print match rows with a visible ranking prefix."""
    for rank, result in enumerate(results, start=1):
        print(
            format_match_line(
                rank=rank,
                title=str(result[title_key]),
                noc_code=str(result["noc_code"]),
                similarity=float(result["similarity"]),
                matched_terms=list(result.get("display_matched_terms", result["matched_terms"])),
            )
        )


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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find the most similar Level 5 NOC occupations for a text query."
    )
    parser.add_argument("query", nargs="*", help="The text chunk to compare.")
    parser.add_argument(
        "--input-path",
        help=(
            "Path to the Level 5 dataset. Defaults to backend/data/level5.xlsx "
            "with project-relative fallbacks."
        ),
    )
    parser.add_argument(
        "--cache-dir",
        help=(
            "Directory for cached embeddings and metadata. Defaults to "
            "backend/data/cache."
        ),
    )
    parser.add_argument(
        "--sheet-name",
        default=os.getenv("NOC_SHEET_NAME", DEFAULT_SHEET_NAME),
        help="Excel sheet name to read when --input-path points to an .xlsx file.",
    )
    parser.add_argument(
        "--source-lang",
        default="auto",
        help=(
            "Input language as an NLLB code or common alias such as 'es', 'fr', "
            "or 'zh'. Defaults to auto-detection with English fallback."
        ),
    )
    parser.add_argument("--top-k", type=int, default=10, help="Number of matches.")
    parser.add_argument(
        "--json", action="store_true", help="Return results as compact JSON."
    )
    args = parser.parse_args()

    # Step 0: resolve the shared backend data paths before reading any files.
    # The cache directory is generated data and is ignored by Git.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    input_path = resolve_input_path(args.input_path)
    cache_dir = resolve_cache_dir(args.cache_dir)

    query = read_query_text(args.query)
    if not query:
        raise SystemExit(
            "No query text was provided. Pass quoted text after the script name, pipe text into the script, or paste text when prompted."
        )

    # Step 1: translate to English only when needed so the embedding search can
    # continue using the existing multilingual MiniLM retrieval pipeline.
    source_lang = resolve_source_language(args.source_lang, query)
    english_query = translate_text(query, source_lang, "eng_Latn")
    if not english_query:
        raise SystemExit("Unable to translate the query into English.")

    # Step 2: run the semantic search against the configured dataset and cache.
    results = search(
        english_query,
        top_k=args.top_k,
        input_path=input_path,
        sheet_name=args.sheet_name,
        cache_dir=cache_dir,
    )

    translated_results = results
    if source_lang != "eng_Latn":
        translated_results = []
        for result in results:
            translated_results.append(
                {
                    **result,
                    "translated_title": translate_text(
                        result["title"], "eng_Latn", source_lang
                    ),
                    "display_matched_terms": translate_matched_terms(
                        result["matched_terms"], "eng_Latn", source_lang
                    ),
                }
            )

    if args.json:
        payload = {
            "original_input": query,
            "source_language": source_lang,
            "top_matches": translated_results,
        }
        if source_lang != "eng_Latn":
            payload["english_translation"] = english_query
        print(json.dumps(payload, ensure_ascii=False))
        return

    if source_lang == "eng_Latn":
        print_ranked_matches(results)
        return

    print(f"Original input: {query}")
    print(f"Source language: {source_lang}")
    print(f"English translation: {english_query}")
    print("Top matches in English:")
    print_ranked_matches(results)
    print("Top matches in source language:")
    print_ranked_matches(translated_results, title_key="translated_title")


if __name__ == "__main__":
    main()
