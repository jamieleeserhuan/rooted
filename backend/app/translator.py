"""
translator.py
-------------
This file is responsible for ONE thing: detecting the user's input language
and translating text between that language and English.

Main functions:
  resolve_source_language(language, text) -> str
  translate_text(text, source_lang, target_lang) -> str

HOW IT FITS INTO ROOTED:
  1. main.py receives the user's work experience description
  2. translator.py detects the language, or uses the provided source language
  3. translator.py translates non-English text into English with NLLB
  4. matcher.py uses the English text to find the closest NOC occupations

TO USE THIS FILE:
  from app.translator import resolve_source_language, translate_text

  text = "Cociné comida en un restaurante."
  lang = resolve_source_language("auto", text)
  english = translate_text(text, lang, "eng_Latn")
  print(lang)
  print(english)

MODEL USED:
  facebook/nllb-200-distilled-600M

DEPENDENCIES:
  pip install -r backend/requirements.txt

"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

import torch

try:
    from langdetect import DetectorFactory, LangDetectException, detect_langs
except ImportError:
    DetectorFactory = None
    LangDetectException = Exception
    detect_langs = None

from transformers.utils import import_utils as transformers_import_utils

# Translation is text-only. This avoids optional torchvision imports in
# environments where torchvision is installed but incompatible with torch.
transformers_import_utils._torchvision_available = False
transformers_import_utils._torchvision_version = "disabled"

from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers.utils import logging as transformers_logging

transformers_logging.set_verbosity_error()
transformers_logging.disable_progress_bar()

if DetectorFactory is not None:
    DetectorFactory.seed = 0


SCRIPT_DIR = Path(__file__).resolve().parent
TRANSLATION_MODEL_REPO = "facebook/nllb-200-distilled-600M"


def discover_base_dir() -> Path:
    """Find the repository root that contains the backend directory."""
    configured_base_dir = os.getenv("NOC_BASE_DIR")
    if configured_base_dir:
        return Path(configured_base_dir).expanduser().resolve()

    for parent in (SCRIPT_DIR, *SCRIPT_DIR.parents):
        if parent.name == "backend":
            return parent.parent.resolve()

    return SCRIPT_DIR.parent.resolve()


BASE_DIR = discover_base_dir()
BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BACKEND_DIR / "data"
DEFAULT_CACHE_DIR = DATA_DIR / "cache"

hf_home_value = Path(os.getenv("HF_HOME", DEFAULT_CACHE_DIR / "huggingface")).expanduser()
if not hf_home_value.is_absolute():
    hf_home_value = (BASE_DIR / hf_home_value).resolve()
os.environ.setdefault("HF_HOME", str(hf_home_value))

HF_HOME_DIR = Path(os.environ["HF_HOME"]).expanduser().resolve()
LEGACY_HF_HOME_DIR = (Path.home() / ".cache" / "huggingface").resolve()
TRANSLATION_CACHE_ROOT = HF_HOME_DIR / "hub" / "models--facebook--nllb-200-distilled-600M"
TRANSLATION_LEGACY_CACHE_ROOT = (
    LEGACY_HF_HOME_DIR / "hub" / "models--facebook--nllb-200-distilled-600M"
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

LANGDETECT_TO_NLLB = {
    "ar": "arb_Arab",
    "bg": "bul_Cyrl",
    "bn": "ben_Beng",
    "ca": "cat_Latn",
    "cs": "ces_Latn",
    "da": "dan_Latn",
    "de": "deu_Latn",
    "el": "ell_Grek",
    "en": "eng_Latn",
    "es": "spa_Latn",
    "fa": "fas_Arab",
    "fi": "fin_Latn",
    "fr": "fra_Latn",
    "gu": "guj_Gujr",
    "he": "heb_Hebr",
    "hi": "hin_Deva",
    "id": "ind_Latn",
    "it": "ita_Latn",
    "ja": "jpn_Jpan",
    "kn": "kan_Knda",
    "ko": "kor_Hang",
    "ml": "mal_Mlym",
    "mr": "mar_Deva",
    "nl": "nld_Latn",
    "no": "nob_Latn",
    "pa": "pan_Guru",
    "pl": "pol_Latn",
    "pt": "por_Latn",
    "ro": "ron_Latn",
    "ru": "rus_Cyrl",
    "sk": "slk_Latn",
    "sl": "slv_Latn",
    "sv": "swe_Latn",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "th": "tha_Thai",
    "tl": "tgl_Latn",
    "tr": "tur_Latn",
    "uk": "ukr_Cyrl",
    "ur": "urd_Arab",
    "vi": "vie_Latn",
}

SCRIPT_LANGUAGE_PATTERNS = (
    (r"[\u4e00-\u9fff]", "zho_Hans"),
    (r"[\u3040-\u30ff]", "jpn_Jpan"),
    (r"[\uac00-\ud7af]", "kor_Hang"),
    (r"[\u0600-\u06ff]", "arb_Arab"),
    (r"[\u0590-\u05ff]", "heb_Hebr"),
    (r"[\u0370-\u03ff]", "ell_Grek"),
    (r"[\u0900-\u097f]", "hin_Deva"),
    (r"[\u0980-\u09ff]", "ben_Beng"),
    (r"[\u0a00-\u0a7f]", "pan_Guru"),
    (r"[\u0a80-\u0aff]", "guj_Gujr"),
    (r"[\u0b80-\u0bff]", "tam_Taml"),
    (r"[\u0c00-\u0c7f]", "tel_Telu"),
    (r"[\u0c80-\u0cff]", "kan_Knda"),
    (r"[\u0d00-\u0d7f]", "mal_Mlym"),
    (r"[\u0e00-\u0e7f]", "tha_Thai"),
)


def normalize_text(text: str) -> str:
    """Collapse whitespace before sending text to the translation model."""
    return re.sub(r"\s+", " ", text).strip()


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
    """Detect the input language and return the matching NLLB language code."""
    normalized = normalize_text(text)
    if not normalized:
        return "eng_Latn"

    # Non-Latin scripts can be routed reliably before using statistical detection.
    for pattern, language_code in SCRIPT_LANGUAGE_PATTERNS:
        if re.search(pattern, normalized):
            return language_code

    lowered = normalized.lower()
    if re.search(r"[\u0400-\u04ff]", normalized):
        return "ukr_Cyrl" if re.search(r"[іїєґ]", lowered) else "rus_Cyrl"

    if detect_langs is None:
        raise SystemExit(
            "Auto language detection requires langdetect. Install dependencies "
            "with 'pip install -r backend/requirements.txt' or pass a source "
            "language like '--source-lang es' or '--source-lang spa_Latn'."
        )

    try:
        detected_languages = detect_langs(normalized)
    except LangDetectException as exc:
        raise SystemExit(
            "Could not auto-detect the input language. Pass a source language "
            "like '--source-lang es' or '--source-lang spa_Latn'."
        ) from exc

    for detected_language in detected_languages:
        nllb_code = LANGDETECT_TO_NLLB.get(detected_language.lang)
        if nllb_code:
            return nllb_code

    detected_summary = ", ".join(
        f"{item.lang}:{item.prob:.2f}" for item in detected_languages
    )
    raise SystemExit(
        "Auto-detected the input language, but it is not mapped to an NLLB "
        f"code yet ({detected_summary}). Pass --source-lang with an NLLB code."
    )


def resolve_source_language(language: str, text: str) -> str:
    """Choose the explicit source language or fall back to auto-detection."""
    canonical = canonical_language_code(language)
    if canonical != "auto":
        return canonical
    return detect_source_language(text)


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """Translate with NLLB; retrieval/ranking remains separate in matcher.py."""
    normalized = normalize_text(text)
    if not normalized or source_lang == target_lang:
        return normalized

    tokenizer = load_translation_tokenizer()
    model = load_translation_model()
    target_lang_id = tokenizer.convert_tokens_to_ids(target_lang)
    if target_lang_id == tokenizer.unk_token_id:
        raise SystemExit(f"Unsupported NLLB target language code '{target_lang}'.")
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
    return normalize_text(translated[0] if translated else "")
