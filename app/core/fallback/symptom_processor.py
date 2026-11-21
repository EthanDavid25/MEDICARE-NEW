"""
Pure Python fallback for symptom processing and normalization.
Mirrors native/src/symptom_processor.c
"""
import re
import unicodedata

STOP_WORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "have", "am", "is", "are", 
    "was", "were", "feel", "feeling", "a", "an", "the", "and", "but", "if", 
    "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", 
    "about", "against", "between", "into", "through", "during", "before", "after", 
    "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", 
    "under", "again", "further", "then", "once", "here", "there", "when", "where", 
    "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", 
    "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", 
    "very", "s", "t", "can", "will", "just", "don", "should", "now", "experiencing", "got"
}

def normalize_symptom(input_text: str, max_len: int = 128) -> str:
    """
    Lowercases, strips punctuation, and collapses whitespace.
    Mirrors normalize_symptom() in symptom_processor.c
    """
    if not input_text:
        return ""
    text = unicodedata.normalize("NFKD", str(input_text))
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s_\-]", " ", text)
    text = re.sub(r"[\s_\-]+", " ", text).strip()
    return text[:max_len]

def extract_symptom_tokens(text: str) -> list[str]:
    """Extract search/matching tokens, filtering stopwords."""
    cleaned = normalize_symptom(text)
    tokens = [t for t in cleaned.split() if t not in STOP_WORDS and len(t) > 2]
    seen = set()
    result = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            result.append(t)
    return result

def deduplicate_symptoms(entries: list[dict]) -> list[dict]:
    """
    Removes exact code duplicates, keeping the entry with the higher severity.
    Mirrors deduplicate_symptoms() in symptom_processor.c
    """
    if not entries:
        return []
    deduped = {}
    for entry in entries:
        code = entry.get("code") or entry.get("symptom_code", "")
        if not code:
            continue
        if code in deduped:
            if entry.get("severity", 0) > deduped[code].get("severity", 0):
                deduped[code] = entry
        else:
            deduped[code] = entry
    return list(deduped.values())
