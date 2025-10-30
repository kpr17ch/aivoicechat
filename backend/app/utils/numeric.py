"""Utilities for handling German numeric phrases and validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List

DIGIT_WORDS: dict[str, str] = {
    "null": "0",
    "o": "0",
    "zero": "0",
    "eins": "1",
    "ein": "1",
    "eine": "1",
    "einer": "1",
    "zwei": "2",
    "zwo": "2",
    "drei": "3",
    "vier": "4",
    "fünf": "5",
    "sechs": "6",
    "sieben": "7",
    "acht": "8",
    "neun": "9",
}

LETTER_WORDS: dict[str, str] = {
    "a": "A",
    "ä": "AE",
    "b": "B",
    "c": "C",
    "d": "D",
    "e": "E",
    "f": "F",
    "g": "G",
    "h": "H",
    "i": "I",
    "j": "J",
    "k": "K",
    "l": "L",
    "m": "M",
    "n": "N",
    "o": "O",
    "ö": "OE",
    "p": "P",
    "q": "Q",
    "r": "R",
    "s": "S",
    "ß": "SS",
    "t": "T",
    "u": "U",
    "ü": "UE",
    "v": "V",
    "w": "W",
    "x": "X",
    "y": "Y",
    "z": "Z",
}

TOKEN_PATTERN = re.compile(r"[a-zäöüß]+|\d+|\+|#|[-]")
PHONE_CLEAN_PATTERN = re.compile(r"[^\d+]")
PHONE_VALID_PATTERN = re.compile(r"^(?:\+?49|0)(?:\d){6,}$")


@dataclass(slots=True)
class NumericAnalysis:
    """Structured result describing normalized numeric content."""

    normalized: str
    phone_candidates: List[str]


def _normalize_tokens(tokens: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    skip_next = False
    for token in tokens:
        if skip_next:
            skip_next = False
            continue
        lower = token.lower()
        if lower == "doppel" and normalized:
            # Duplicate the previous numeric token if present
            last = normalized[-1]
            if last.isdigit():
                normalized.append(last)
            continue
        if lower == "plus":
            normalized.append("+")
            continue
        if lower in DIGIT_WORDS:
            normalized.append(DIGIT_WORDS[lower])
            continue
        if lower in LETTER_WORDS:
            normalized.append(LETTER_WORDS[lower])
            continue
        normalized.append(token)
    return normalized


def normalize_numeric_phrase(text: str | None) -> NumericAnalysis:
    """Return normalized numeric string and phone candidates."""
    if not text:
        return NumericAnalysis(normalized="", phone_candidates=[])

    tokens = TOKEN_PATTERN.findall(text)
    normalized_tokens = _normalize_tokens(tokens)
    normalized_str = " ".join(normalized_tokens).strip()

    phone_candidates = _extract_phone_candidates(normalized_tokens)
    return NumericAnalysis(normalized=normalized_str, phone_candidates=phone_candidates)


def _extract_phone_candidates(tokens: list[str]) -> list[str]:
    joined = " ".join(tokens)
    candidate_pattern = re.compile(r"(?:\+?\d[\d\s-]{3,}\d)")
    candidates = []
    for match in candidate_pattern.findall(joined):
        cleaned = PHONE_CLEAN_PATTERN.sub("", match)
        if cleaned and len(cleaned) >= 6:
            candidates.append(cleaned)
    seen: set[str] = set()
    unique: list[str] = []
    for c in candidates:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique


def is_plausible_german_phone(number: str | None) -> bool:
    """Return True when number looks like a German phone number."""
    if not number:
        return False
    return bool(PHONE_VALID_PATTERN.match(number))
